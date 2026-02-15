<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

const navItems = [
  { to: '/', label: 'Home' },
  { to: '/mcdonalds', label: "McDonald's" },
  { to: '/transport', label: 'Transport' },
  { to: '/dental', label: 'Dental' },
  { to: '/psychotherapy', label: 'Psychotherapy' },
]
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <!-- Top Nav Bar -->
    <nav class="bg-gray-900 text-white px-4 py-3 flex items-center gap-6 shadow-lg">
      <RouterLink
        to="/"
        class="text-lg font-bold text-white hover:text-blue-300 transition-colors"
      >
        Voice AI Apps
      </RouterLink>
      <div class="flex gap-1">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
          :class="route.path === item.to
            ? 'bg-white/20 text-white'
            : 'text-white/60 hover:text-white hover:bg-white/10'"
        >
          {{ item.label }}
        </RouterLink>
      </div>
    </nav>

    <!-- App Content -->
    <main class="flex-1">
      <RouterView />
    </main>
  </div>
</template>
