import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/apps/home/HomePage.vue'),
    },
    {
      path: '/mcdonalds',
      name: 'mcdonalds',
      component: () => import('@/apps/mcdonalds/McdonaldsApp.vue'),
    },
    {
      path: '/transport',
      name: 'transport',
      component: () => import('@/apps/transport/TransportApp.vue'),
    },
    {
      path: '/dental',
      name: 'dental',
      component: () => import('@/apps/dental/DentalApp.vue'),
    },
    {
      path: '/psychotherapy',
      name: 'psychotherapy',
      component: () => import('@/apps/psychotherapy/PsychotherapyApp.vue'),
    },
  ],
})

export default router
