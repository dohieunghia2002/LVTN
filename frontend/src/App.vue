<template>
  <div class="app-container">
    <Header />
    <router-view></router-view>
    <footer class="footer">
      <p>Copyright 2024: Hieu-Nghia Do, Truong-Thanh Ma</p>
    </footer>
  </div>
</template>

<script>
import Header from './components/Header.vue'

export default {
  components: {
    Header
  }
}
</script>

<style>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.footer {
  margin-top: auto;
  text-align: center;
  padding: 20px;
  background-color: #333;
  color: #fff;
}
</style>
