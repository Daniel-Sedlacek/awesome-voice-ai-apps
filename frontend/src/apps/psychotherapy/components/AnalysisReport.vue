<script setup>
defineProps({
  report: {
    type: Object,
    required: true,
  },
  transcription: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <div class="bg-white/10 rounded-2xl p-6 space-y-4">
    <h3 class="text-psych-light font-bold text-lg">Analysis Report</h3>

    <div>
      <p class="text-psych-light text-sm font-semibold mb-1">Summary</p>
      <p class="text-white/80">{{ report.summary }}</p>
    </div>

    <div>
      <p class="text-psych-light text-sm font-semibold mb-1">Key Emotions</p>
      <p class="text-white/80">{{ report.key_emotions }}</p>
    </div>

    <div>
      <p class="text-psych-light text-sm font-semibold mb-1">Concerns & Themes</p>
      <p class="text-white/80">{{ report.concerns_themes }}</p>
    </div>

    <div>
      <p class="text-psych-light text-sm font-semibold mb-1">Insights</p>
      <p class="text-white/80">{{ report.insights }}</p>
    </div>

    <div v-if="transcription" class="pt-3 border-t border-white/10">
      <p class="text-white/40 text-sm font-semibold mb-1">What you said</p>
      <p class="text-white/60 text-sm italic">"{{ transcription }}"</p>
    </div>
  </div>
</template>
