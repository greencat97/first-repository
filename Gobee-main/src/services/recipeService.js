const BASE_URL = 'http://127.0.0.1:8000'

export async function getRecipesByIngredient(ingredient) {
  const res = await fetch(`${BASE_URL}/recipes?ingredient=${ingredient}`)
  return await res.json()
}

export async function getRecipeById(id) {
  const res = await fetch(`${BASE_URL}/recipes/${id}`)
  return await res.json()
}