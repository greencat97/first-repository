import { createRouter, createWebHistory } from 'vue-router'

import ChefView from '@/views/ChefView.vue'
import HomeView from '@/views/HomeView.vue'
import QuestView from '@/views/QuestView.vue'
import RecipeDetailView from '@/views/RecipeDetailView.vue'
import RecipeListView from '@/views/RecipeListView.vue'
import AccountView from '@/views/AccountView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView},
    { path: '/quest', name: 'quest', component: QuestView},
    { path: '/chef', name: 'chef', component: ChefView},
    { path: '/account', name: 'account', component: AccountView},
    {
      path: '/recipes',
      name: 'recipes',
      component: RecipeListView
    },
    {
      path: '/recipe/:id',
      name: 'recipe-detail',
      component: RecipeDetailView
    }
  ],
})

export default router
