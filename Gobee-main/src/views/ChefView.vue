<template>
  <div class="page">

    <div class="card">

      <h1 class="title">Chef Cam</h1>

      <img
        class="hero-img"
        src="@/assets/ChefCamPhoto.png"
      />

      <p class="desc">
        Get healthy recipe ideas based on the ingredients at you have in the fridge
      </p>

      <input
        v-model="input"
        placeholder="e.g. egg tomato rice"
        class="input"
      />

      <button class="btn" @click="go">
        Get Recipes
      </button>

    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const input = ref('')
const router = useRouter()

const go = () => {
  router.push({
    name: 'recipes',
    query: { ingredients: input.value }
  })
}
</script>

<style scoped>
.page {
  display: flex;
  justify-content: center;
  padding: 20px;
}

.card {
  width: 100%;
  max-width: 380px;

  border-radius: 24px;

  padding: 20px;

  text-align: center;
}

.title {
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 12px;
}

.hero-img {
  width: 100%;
  border-radius: 16px;
  margin-bottom: 16px;
}

.desc {
  font-size: 14px;
  color: #444;
  margin-bottom: 16px;
}

.input {
  width: 100%;
  padding: 12px;

  border-radius: 12px;
  border: 1px solid #ddd;

  margin-bottom: 12px;

  font-size: 14px;
}

.btn {
  width: 100%;
  padding: 14px;

  border-radius: 20px;
  border: none;

  background: #ffb347;
  color: #333;

  font-weight: 600;
  font-size: 14px;

  cursor: pointer;
  transition: all 0.2s;
}

.btn:hover {
  transform: translateY(-2px);
  background: #ffa726;
}
</style>