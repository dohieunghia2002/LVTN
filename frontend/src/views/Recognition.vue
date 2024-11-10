<template>
  <div class="home">
    <v-container>
      <v-row>
        <v-col cols="12">
          <h2 class="heading">Vietnamese Specialty Dish Recognition System</h2>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="6">
          <v-btn variant="flat" color="blue-darken-4" @click="clickInput()">
            Upload an image
          </v-btn>

          <input type="file" id="upload" accept="image/png, image/jpeg, image/jpg" hidden @change="displayUploadImg()">

          <v-btn class="btn--recognize" variant="flat" color="green-accent-4" @click="recognizeImg()">
            <span>Recognize</span>
          </v-btn>

          <div class="img__wrapper">
            <img class="img" src="../assets/images/logo_ctu.png" alt="ảnh upload">
          </div>
        </v-col>
        <v-col cols="6" class="result-detect__wrapper">
          <h2>Detected ingredients include:</h2>

          <div class="detect_result">
            <h4>YOLO11:</h4>
            <p>{{ v11Detected }} => <strong>{{ v11Predicted }}</strong></p>
            <v-btn size="small" color="green-accent-3">
              <router-link :to="{ name: 'text-recognition', query: { ingredients: v11Detected } }"
                class="caterogy__link">
                Enter ingredient components
              </router-link>
            </v-btn>
          </div>

          <div class="detect_result">
            <h4>RT-DETR:</h4>
            <p>{{ rtdetrDetected }} => <strong>{{ rtdetrPredicted }}</strong></p>
            <v-btn size="small" color="green-accent-3">
              <router-link :to="{ name: 'text-recognition' }" class="caterogy__link">
                Enter ingredient components
              </router-link>
            </v-btn>
          </div>

          <div class="detect_result">
            <h4>YOLOV8:</h4>
            <p>{{ v8Detected }} => <strong>{{ v8Predicted }}</strong></p>
            <v-btn size="small" color="green-accent-3">
              <router-link :to="{ name: 'text-recognition' }" class="caterogy__link">
                Enter ingredient components
              </router-link>
            </v-btn>
          </div>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="1">
          <h4>YOLO11:</h4>
        </v-col>
        <v-col cols="1" v-for="(imgCropped, idx) in results.yolo11.detected_images" :key="idx">
          <div class="img__container">
            <img class="img--cropped" :src="'data:image/jpeg;base64,' + imgCropped" alt="ảnh được phát hiện">
          </div>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="1">
          <h4>RT-DETR:</h4>
        </v-col>
        <v-col cols="1" v-for="(img, i) in results.rtdetr.detected_images" :key="i">
          <div class="img__container">
            <img class="img--cropped" :src="'data:image/jpeg;base64,' + img" alt="ảnh được phát hiện">
          </div>
        </v-col>
      </v-row>

      <v-row style="margin-top: 2rem;">
        <v-col cols="1">
          <h4>YOLOV8:</h4>
        </v-col>
        <v-col cols="1" v-for="(cropped, index) in results.yolov8.detected_images" :key="index">
          <div class="img__container">
            <img class="img--cropped" :src="'data:image/jpeg;base64,' + cropped" alt="ảnh được phát hiện">
          </div>
        </v-col>
      </v-row>

      <v-row v-if="results.yolo11?.distances?.length > 0 && labels?.length > 0"
        :key="results.yolo11?.distances?.length">
        <v-col cols="12">
          <v-table class="border border-1 border-solid" theme="light">
            <thead>
              <tr>
                <th class="text-left"></th>
                <th class="text-left"><strong>Name</strong></th>
                <th class="text-center"><strong>YOLO11</strong></th>
                <th class="text-center"><strong>RT-DETR</strong></th>
                <th class="text-center"><strong>YOLOV8</strong></th>
                <th class="text-center"><strong>Max</strong></th>
                <th class="text-center"><strong>Sum</strong></th>
                <th class="text-center"><strong>Gmax</strong></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, idx) in labels" :key="idx">
                <td>{{ (idx + 1) }}</td>
                <td>{{ item }}</td>
                <td class="text-center v10--distance">{{ results.yolo11.distances[idx] }}</td>
                <td class="text-center rtdetr--distance">{{ results.rtdetr.distances[idx] }}</td>
                <td class="text-center v8--distance">{{ results.yolov8.distances[idx] }}</td>
                <td class="text-center max">{{ max_list[idx] }}</td>
                <td class="text-center">{{ sum_list[idx] }}</td>
                <td class="text-center">{{ Gmax[idx] }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import axios from 'axios';
import { useDishesStore } from '../stores/dishes.js';

export default {
  setup() {
    const dishesStore = useDishesStore();
    return {
      dishesStore
    }
  },
  data() {
    return {
      labels: [],
      results: {
        yolo11: {},
        rtdetr: {},
        yolov8: {}
      },

      v11Detected: "",
      rtdetrDetected: "",
      v8Detected: "",

      max_list: [],
      sum_list: [],
      Gmax: [],

      v11Predicted: "",
      rtdetrPredicted: "",
      v8Predicted: "",
    }
  },

  methods: {
    async displayUploadImg() {
      const inputElement = document.getElementById("upload");
      const file = inputElement.files[0];
      const imgElement = document.getElementsByClassName("img")[0];
      imgElement.src = URL.createObjectURL(file)
    },

    async clickInput() {
      const inputElement = document.getElementById("upload");
      inputElement.click();
    },

    async normalized_ingre(detected, mapping) {
      const normalizedList = detected.map(item => mapping[item] || item);
      return normalizedList
    },

    async recognizeImg() {
      const inputElement = document.getElementById("upload");
      const file = inputElement.files[0];

      const form = new FormData()
      form.append('file', file)
      const res = await axios.post('http://127.0.0.1:9999/api/predict', form, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      this.results.yolo11 = await res.data.results.yolo11;
      this.results.rtdetr = await res.data.results.rtdetr;
      this.results.yolov8 = await res.data.results.yolov8;
      this.labels = await res.data.labels;

      this.max_list = await res.data.max_list;
      this.sum_list = await res.data.sum_list;
      this.Gmax = await res.data.Gmax;

      const jsonResponse = await axios.get('/ingredients.json');
      const ingredientMap = jsonResponse.data;
      let temp1 = await this.results.yolo11.detected_cls;
      let temp2 = await this.results.rtdetr.detected_cls;
      let temp3 = await this.results.yolov8.detected_cls;
      temp1 = await this.normalized_ingre(temp1, ingredientMap);
      temp2 = await this.normalized_ingre(temp2, ingredientMap);
      temp3 = await this.normalized_ingre(temp3, ingredientMap);

      this.v11Detected = await temp1.join(", ");
      this.rtdetrDetected = await temp2.join(", ");
      this.v8Detected = await temp3.join(", ");

      this.v11Predicted = await this.results.yolo11.predicted_label.join("/ ");
      this.rtdetrPredicted = await this.results.rtdetr.predicted_label.join("/ ");
      this.v8Predicted = await this.results.yolov8.predicted_label.join("/ ");

      for (let i = 0; i < this.Gmax.length; i++) {
        this.Gmax[i] = this.Gmax[i].join(" ");
      }
    }
  }
}
</script>

<style>
.heading {
  text-align: center;
  color: rgb(247, 37, 37);
}

.btn--recognize {
  margin-left: 20px;
}

.btn--recognize span {
  color: aliceblue;
}

.img__wrapper {
  margin-top: 2rem;
  width: 65%;
}

.img,
.img--cropped {
  width: 100%;
}

.detect_result {
  margin-top: 1rem;
}

.result-detect__wrapper {
  background-color: rgb(243, 242, 236);
}
</style>