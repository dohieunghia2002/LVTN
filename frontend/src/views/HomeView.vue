<template>
  <div class="home">
    <v-container>
      <v-row>
        <v-col cols="12">
          <h2 class="heading">Vietnamese Specialty Dishes</h2>
        </v-col>
      </v-row>

      <v-row v-if="jsonData">
        <v-col cols="3" v-for="item in jsonData" :key="item.id">
          <v-card class="card" variant="outlined">
            <router-link class="card__router" :to="{ name: 'detail', params: { id: item.id } }">
              <v-img :src="item.imgPath" alt="img" height="250px" cover></v-img>
              <v-card-title class="text-h6" style="text-align: center;">{{ item.name }}</v-card-title>
            </router-link>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>
<script>
export default {
  data() {
    return {
      jsonData: null,
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      try {
        const response = await fetch('/data.json');
        if (response.ok) {
          const data = await response.json();
          this.jsonData = data;
        } else {
          console.error('Error fetching data:', response.statusText);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    },
  },
}
</script>
<style scoped>
.heading {
  text-align: center;
  margin-top: 1rem;
  margin-bottom: 1rem;
}

.card {
  cursor: pointer;
}

.card:hover {
  opacity: 0.8;
  background-color: burlywood;
}

.card__router {
  text-decoration: none;
  color: #333;
}
</style>