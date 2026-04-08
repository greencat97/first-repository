<template>
  <div class="page">
    <div class="header">
      <button class="back-btn" @click="goBack">← Back</button>
    </div>

    <!-- loading -->
    <p v-if="loading">Loading...</p>

    <!-- content -->
    <div v-else-if="recipe">

      <img
        class="image"
        :src="recipe.image_url || fallback"
      />

      <h1 class="title">{{ recipe.title }}</h1>

      <p class="meta">
        {{ recipe.category }} • {{ recipe.area }}
      </p>

      <div class="section">
        <h3>Ingredients</h3>
        <p>{{ recipe.ingredients_text }}</p>
      </div>

      <div class="section">
        <h3>Instructions</h3>
        <p>{{ recipe.instructions_text }}</p>
      </div>

    </div>

    <!-- error -->
    <p v-else>Recipe not found</p>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getRecipeById } from '@/services/recipeService'

const route = useRoute()

const recipe = ref(null)
const loading = ref(true)

const fallback = 'https://via.placeholder.com/300'

const goBack = () => {
  window.history.back()
}

onMounted(async () => {
  try {
    const id = route.params.id

    const data = await getRecipeById(id)

    recipe.value = data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page {
  max-width: 420px;
  margin: 0 auto;
  padding: 20px;
}

.image {
  width: 100%;
  border-radius: 20px;
  margin-bottom: 16px;
}

.title {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 8px;
}

.meta {
  color: #666;
  margin-bottom: 16px;
}

.section {
  margin-bottom: 20px;
}

h3 {
  margin-bottom: 6px;
}
</style>