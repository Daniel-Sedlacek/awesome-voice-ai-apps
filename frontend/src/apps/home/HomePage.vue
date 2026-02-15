<script setup>
const apps = [
  {
    to: '/mcdonalds',
    title: "McDonald's Voice Menu",
    description: 'Order food using your voice — search, add items, and manage your basket.',
    tech: ['STT', 'LLM', 'RAG', 'Embeddings', 'Reranker'],
  },
  {
    to: '/transport',
    title: 'Public Transport Voice',
    description: 'Speak in one language, get instant translations with audio in two others.',
    tech: ['STT', 'TTS', 'Translation'],
  },
  {
    to: '/dental',
    title: 'Dental Dictation',
    description: 'Dictate periodontal findings and get structured data extracted automatically.',
    tech: ['STT', 'LLM', 'Structured Extraction'],
  },
  {
    to: '/psychotherapy',
    title: 'Psychotherapy Tracker',
    description: 'Record voice monologues and get AI-powered emotional wellness analysis.',
    tech: ['STT', 'LLM', 'Sentiment Analysis'],
  },
]
</script>

<template>
  <div class="min-h-screen bg-gray-950 py-12 px-4">
    <div class="max-w-4xl mx-auto">
      <div class="text-center mb-10">
        <h1 class="text-4xl font-bold text-white mb-3">Voice AI Applications</h1>
        <p class="text-gray-400 text-lg max-w-2xl mx-auto">
          A collection of voice-powered AI apps demonstrating real-time speech recognition,
          NLP, and intelligent responses.
        </p>
      </div>

      <table class="w-full border-collapse">
        <thead>
          <tr class="border-b border-white/10 text-left text-xs uppercase tracking-wider text-gray-500">
            <th class="pb-3 pl-2 font-medium">App</th>
            <th class="pb-3 font-medium hidden sm:table-cell">Description</th>
            <th class="pb-3 pr-2 font-medium">Technologies</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="app in apps"
            :key="app.to"
            class="border-b border-white/5 hover:bg-white/[0.03] transition-colors"
          >
            <td class="py-4 pl-2 pr-4">
              <RouterLink
                :to="app.to"
                class="text-white font-semibold hover:text-blue-400 transition-colors whitespace-nowrap"
              >
                {{ app.title }}
              </RouterLink>
              <p class="text-gray-500 text-sm mt-1 sm:hidden">{{ app.description }}</p>
            </td>
            <td class="py-4 pr-4 text-gray-400 text-sm hidden sm:table-cell">
              {{ app.description }}
            </td>
            <td class="py-4 pr-2">
              <div class="flex flex-wrap gap-1.5">
                <span
                  v-for="t in app.tech"
                  :key="t"
                  class="px-2 py-0.5 rounded-full text-xs font-medium bg-white/5 text-gray-400 border border-white/10"
                >
                  {{ t }}
                </span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
