<script setup>
const apps = [
  {
    to: '/mcdonalds',
    title: "McDonald's Voice Menu",
    description: 'Order food using your voice. Speak naturally to search, add items to your basket, and manage your order.',
    icon: 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707',
    gradient: 'from-red-600 to-red-800',
    accent: 'text-yellow-400',
  },
  {
    to: '/transport',
    title: 'Public Transport Voice',
    description: 'Speak in one language and get instant translations with audio playback in two other languages.',
    icon: 'M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129',
    gradient: 'from-blue-600 to-blue-800',
    accent: 'text-blue-300',
  },
  {
    to: '/dental',
    title: 'Dental Dictation',
    description: 'Dictate periodontal exam findings and get structured data extracted automatically with a visual dental chart.',
    icon: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z',
    gradient: 'from-teal-600 to-teal-800',
    accent: 'text-teal-300',
  },
  {
    to: '/psychotherapy',
    title: 'Psychotherapy Tracker',
    description: 'Record voice monologues and get AI-powered emotional wellness analysis with metrics and insights.',
    icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
    gradient: 'from-purple-600 to-purple-800',
    accent: 'text-purple-300',
  },
]
</script>

<template>
  <div class="min-h-screen bg-gray-950 py-12 px-4">
    <div class="max-w-4xl mx-auto">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-white mb-3">Voice AI Applications</h1>
        <p class="text-gray-400 text-lg max-w-2xl mx-auto">
          A collection of voice-powered AI applications demonstrating real-time speech recognition,
          natural language processing, and intelligent responses.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <RouterLink
          v-for="app in apps"
          :key="app.to"
          :to="app.to"
          class="group block"
        >
          <div
            class="rounded-2xl p-6 bg-gradient-to-br transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl"
            :class="app.gradient"
          >
            <div class="flex items-start gap-4">
              <div class="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center shrink-0">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="w-6 h-6 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="1.5"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" :d="app.icon" />
                </svg>
              </div>
              <div>
                <h2 class="text-xl font-bold text-white mb-2 group-hover:underline">
                  {{ app.title }}
                </h2>
                <p class="text-white/70 text-sm leading-relaxed">
                  {{ app.description }}
                </p>
              </div>
            </div>
          </div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>
