<template>
  <div class="card" @click="$emit('click')">
    
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
</template>

<script setup>
const fallback = 'https://via.placeholder.com/300'

defineProps({
  recipe: Object
})
</script>

<style scoped>
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