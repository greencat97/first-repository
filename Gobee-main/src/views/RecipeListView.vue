<template>
  <div class="page">
    <div class="header">
      <button class="back-btn" @click="goBack">← Back</button>
    </div>

    <h1 class="title">Recipes</h1>

    <!-- loading -->
    <p v-if="loading">Loading...</p>

    <!-- no result -->
    <p v-else-if="recipes.length === 0">No recipes found</p>

    <!-- list -->
    <div v-else class="list">
      <div
        v-for="recipe in recipes"
        :key="recipe.recipe_id"
        class="card"
        @click="goToDetail(recipe.recipe_id)"
      >
        <img
          class="image"
          :src="recipe.image_url || fallback"
        />

        <div class="content">
          <h3 class="name">{{ recipe.title }}</h3>
          <p class="meta">
            {{ recipe.category }} • {{ recipe.area }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getRecipesByIngredient } from '@/services/recipeService'

const route = useRoute()
const router = useRouter()

const recipes = ref([])
const loading = ref(true)

const fallback = 'https://via.placeholder.com/300'

const goBack = () => {
  window.history.back()
}

onMounted(async () => {
  try {
    const ingredient = route.query.ingredients || 'egg'

    const data = await getRecipesByIngredient(ingredient)

    // 🔥 核心：取 items
    recipes.value = data.items || []
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})

const goToDetail = (id) => {
  router.push(`/recipe/${id}`)
}
</script>

<style scoped>
.page {
  max-width: 420px;
  margin: 0 auto;
  padding: 20px;
}

.title {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 16px;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;

  box-shadow: 0 6px 16px rgba(0,0,0,0.08);

  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 24px rgba(0,0,0,0.12);
}

.image {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.content {
  padding: 12px 14px;
}

.name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 6px;
}

.meta {
  font-size: 13px;
  color: #666;
}
</style>