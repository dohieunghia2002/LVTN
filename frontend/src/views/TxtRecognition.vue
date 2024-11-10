<template>
  <div class="txt-recognition">
    <h2 class="heading" style="text-align: center; margin-top: 1.5rem;">
      Vietnamese Specialty Dish Recognition System through Text
    </h2>

    <!-- Input form -->
    <v-container>
      <v-row justify="center">
        <v-col cols="12" md="6">
          <v-text-field v-model="ingredients" label="Enter ingredient components"
            placeholder="Ví dụ: gạo, thịt heo, hành tây, tiêu" outlined dense>
          </v-text-field>
          <v-btn @click="submitIngredients" color="primary" class="mt-4" block>Predict</v-btn>
        </v-col>
      </v-row>
    </v-container>

    <!-- Display max distance item -->
    <v-container v-if="maxDistanceItem">
      <v-alert type="info" class="mb-4">
        <strong>Closest Match:</strong> {{ maxDistanceItem[0] }} with Cosine Similarity: {{
          maxDistanceItem[2].toFixed(4) }}
      </v-alert>
    </v-container>

    <v-container v-if="distances.length">
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title>
              <span class="headline">Distance Results</span>
            </v-card-title>
            <v-card-text>
              <table class="table">
                <thead>
                  <tr>
                    <th>Dish Name</th>
                    <th>Dish Detail</th>
                    <th>Cosine Similarity</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in distances" :key="index">
                    <td>{{ item[0] }}</td>
                    <td>
                      <router-link :to="{ name: 'detail', params: { id: item[1] } }">
                        View detail
                      </router-link>
                    </td>
                    <td>{{ item[2] }}</td>
                  </tr>
                </tbody>
              </table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      ingredients: this.$route.query.ingredients || '',
      distances: [],
      maxDistanceItem: null
    };
  },
  watch: {
    // Theo dõi sự thay đổi trong query nếu người dùng quay lại trang
    '$route.query': {
      immediate: true,
      handler(newQuery) {
        this.ingredients = newQuery.ingredients || '';
      }
    }
  },
  methods: {
    async normalized_name() {
      const jsonResponse = await axios.get('/data.json');
      const jsonData = jsonResponse.data;

      // Tạo một object mapping slug với cả name và id
      const dishMapping = {};
      jsonData.forEach(dish => {
        dishMapping[dish.slug] = { name: dish.name, id: dish.id };
      });

      // Tạo danh sách mới kết hợp cả slug và id
      this.distances = this.distances.map(item => {
        const slug = item[0];
        const mappedDish = dishMapping[slug];
        const originalName = mappedDish ? mappedDish.name : slug;
        const id = mappedDish ? mappedDish.id : null;
        return [originalName, id, item[1]];
      });
    },

    async submitIngredients() {
      const payload = { ingredients: this.ingredients };
      try {
        const response = await axios.post('http://127.0.0.1:9999/api/text-recognition', payload);
        const data = response.data;

        this.distances = await data.distances;

        this.maxDistanceItem = await data.max_distance_item;

        await this.normalized_name();

        this.maxDistanceItem = this.distances[0];
      } catch (error) {
        console.error('Error sending data to backend:', error);
      }
    }
  }
}
</script>

<style>
.heading {
  font-weight: bold;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
}

.table th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.table tr:nth-child(even) {
  background-color: #f9f9f9;
}

.table tr:hover {
  background-color: #f1f1f1;
}
</style>
