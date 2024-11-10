from ultralytics import YOLO, RTDETR
import cv2
import math
import base64
import pandas as pd

import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pyvi.ViTokenizer import tokenize

from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from flask import request
from unidecode import unidecode
from custom_utils import crop_image, convertIdx2Class

app = Flask(__name__)

# Set up module
classes_path = './assets/classes.txt'
excel_file_path = './assets/rules.xlsx'

# models object detector
model_yolo11 = YOLO('./assets/models/runs_yolov11_epoch35.pt')
model_rtdetr = RTDETR('./assets/models/runs_rtdetr_epoch32.pt')
model_yolov8 = YOLO('./assets/models/runs_yolov8_epoch30.pt')
model = SentenceTransformer("dangvantuan/vietnamese-embedding")

df = pd.read_excel(excel_file_path)
classes_ingre = []

with open(classes_path, 'r', encoding='utf-8') as file:
    lines = [line.strip() for line in file]
    classes_ingre = lines


def preprocess_dataframe():
    global df
    normalized_df = df.drop(df.columns[[0, -1]], axis=1)
    
    for index, row in normalized_df.iterrows():
        for col in normalized_df.columns:
            value = row[col]
            if pd.notna(value):
                name_without_accents = unidecode(value)
                values = name_without_accents.split(', ')
                for i in range(len(values)):
                    values[i] = values[i].replace(' ', '-')
                row[col] = ', '.join(values)

    return normalized_df

normalized_df = preprocess_dataframe()
    

CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def detect_ingredients(model, img):
    results = model(img, conf=0.3, save=False)
    names = results[0].names
    detected_cls = results[0].boxes.cls.tolist()
    boxes = results[0].boxes.xyxy.tolist()
    return detected_cls, boxes


def find_foodname_ver_narrow(set_detected_ingre):
    global normalized_df
    global df
    distances = []

    for index, row in normalized_df.iterrows():
        values = {}
        values["prior"] = set(row["Priorities"].split(', '))
        values["main"] = set(row["Ingredients"].split(', '))
        values["extra"] = set(row["Secondary Ingredients"].split(', ')) if pd.notna(row["Secondary Ingredients"]) else set()

        # Không khớp với ƯU TIÊN
        no_match_prior = values["prior"].difference(set_detected_ingre)

        # Không khớp với CHÍNH
        no_match_main = values["main"].difference(set_detected_ingre)

        # Khớp với PHỤ
        match_extra = values["extra"].intersection(set_detected_ingre)

        # Phần tử thuộc detect nhưng không thuộc bộ luật
        combine = values["prior"].union(values["main"])
        combine = combine.union(values["extra"])
        redundancy = set_detected_ingre.difference(combine)

        shortage_score = (len(no_match_prior) * 10) + len(no_match_main) - (len(match_extra)*0.5)
        redundancy_score = len(redundancy)
        score = shortage_score + redundancy_score
        
        # print(index, score)
        distances.append(score)

    min_value = min(distances)
    min_indices = [i for i, value in enumerate(distances) if value == min_value]

    predicted_food = []
    for min_index in min_indices:
        predicted_food.append(df.loc[min_index, "Food"])
    
    return distances, predicted_food


def crop_obj_detected(img, boxes):
    detected_images = []
    for index, box in enumerate(boxes):
        cropped_image = crop_image(img, box)

        _, encoded_image = cv2.imencode('.jpg', cropped_image)
        encoded_image = base64.b64encode(encoded_image).decode('utf-8')
        detected_images.append(encoded_image)
    return detected_images


def calculate_belief_merging_base(v11_distances, rtdetr_distances, v8_distances):
    max_list = []
    sum_list = []
    Gmax = []

    for index, v8_value in enumerate(v8_distances):
        v11_value = v11_distances[index]
        rtdetr_value = rtdetr_distances[index]

        max_value = max(v8_value, v11_value, rtdetr_value)
        sum_value = v8_value + v11_value + rtdetr_value
        numbers = [math.ceil(v8_value), math.ceil(v11_value), math.ceil(rtdetr_value)]
        numbers = sorted(numbers, reverse=True)

        max_list.append(max_value)
        sum_list.append(sum_value)
        Gmax.append(numbers)
    
    return max_list, sum_list, Gmax

def process_multi_distances(v11_distances, rtdetr_distances, v8_distances):
    for i in range(len(v11_distances)):
        if (v11_distances[i] == 0 and rtdetr_distances[i] == 0) or (v11_distances[i] == 0 and v8_distances[i] == 0) or (rtdetr_distances[i] == 0 and v8_distances[i] == 0):
            # Nếu có 2 phần tử bằng 0, biến phần tử còn lại thành 0
            v11_distances[i] = 0
            rtdetr_distances[i] = 0
            v8_distances[i] = 0
    return v11_distances, rtdetr_distances, v8_distances

@app.route('/api/predict', methods=['POST'])
@cross_origin(origins='*')
def recognize_food():
    global classes_ingre
    global model_yolov8
    global model_yolo11
    global model_rtdetr
    global df

    file = request.files['file']
    img = cv2.imread(file)

    models = {
        'yolo11': model_yolo11,
        'rtdetr': model_rtdetr,
        'yolov8': model_yolov8
    }
    results = {}

    # loop through models
    for model_name, model in models.items():
        detected_cls, boxes = detect_ingredients(model, img)
        
        rm_duplicates = set(detected_cls)
        rm_duplicates = [int(number) for number in rm_duplicates]
        detected_cls = list(rm_duplicates)
        rm_duplicates = convertIdx2Class(rm_duplicates, classes_ingre)
        
        distances, predicted_label = find_foodname_ver_narrow(rm_duplicates)

        results[model_name] = {
            'detected_cls': list(rm_duplicates),
            'distances': distances,
            'predicted_label': predicted_label,
            'detected_images': crop_obj_detected(img, boxes)
        }
    
    results['yolo11']['distances'], results['rtdetr']['distances'], results['yolov8']['distances'] = process_multi_distances(results['yolo11']['distances'], results['rtdetr']['distances'], results['yolov8']['distances'])

    max_list, sum_list, Gmax = calculate_belief_merging_base(
        results['yolo11']['distances'],
        results['rtdetr']['distances'],
        results['yolov8']['distances']
    )

    return jsonify({
        'labels': df['Food'].tolist(),
        'results': results,
        'max_list': max_list,
        'sum_list': sum_list,
        'Gmax': Gmax
    })

@app.route('/api/text-recognition', methods=['POST'])
@cross_origin(origins='*')
def text_recognition():
    data = request.get_json()  # Lấy dữ liệu JSON từ request
    input_ingredients = data.get('ingredients', '')

    tokenized_input = tokenize(input_ingredients)
    input_embedding = model.encode(tokenized_input)
    embeddings_dir = 'assets/ingredients_npy'

    distances = []
    for filename in os.listdir(embeddings_dir):
        if filename.endswith("_embeddings.npy"):
            temp = filename
            name = temp.replace("_embeddings.npy", "") 

            # Tải embedding từ file .npy
            embedding = np.load(os.path.join(embeddings_dir, filename))
            
            # Tính khoảng cách cosine
            distance = cosine_similarity([input_embedding], [embedding])
            
            # Lưu kết quả
            distances.append((name, float(distance[0][0])))
    
    distances = sorted(distances, key=lambda x: x[1], reverse=True)
    max_distance_item = distances[0] if distances else None  # Phần tử có khoảng cách lớn nhất

    return jsonify({
        'distances': distances,
        'max_distance_item': max_distance_item
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='9999')