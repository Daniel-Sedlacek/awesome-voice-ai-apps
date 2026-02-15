<script setup>
import { computed } from 'vue'

const props = defineProps({
  examData: {
    type: Object,
    required: true,
  },
  transcription: {
    type: String,
    default: '',
  },
  extractionNotes: {
    type: String,
    default: null,
  },
})

const teethCount = computed(() => Object.keys(props.examData?.teeth || {}).length)

const sitesWithBleeding = computed(() => {
  let count = 0
  for (const tooth of Object.values(props.examData?.teeth || {})) {
    for (const site of Object.values(tooth.sites || {})) {
      if (site.bop === true) count++
    }
  }
  return count
})

const maxPdOverall = computed(() => {
  let max = 0
  for (const tooth of Object.values(props.examData?.teeth || {})) {
    for (const site of Object.values(tooth.sites || {})) {
      if (site.pd != null && site.pd > max) max = site.pd
    }
  }
  return max
})
</script>

<template>
  <div class="bg-white/10 rounded-2xl p-6 space-y-4">
    <h3 class="text-dental-light font-bold text-lg">Exam Summary</h3>

    <div class="grid grid-cols-3 gap-4 text-center">
      <div>
        <p class="text-2xl font-bold text-white">{{ teethCount }}</p>
        <p class="text-white/50 text-sm">Teeth recorded</p>
      </div>
      <div>
        <p class="text-2xl font-bold text-white">{{ sitesWithBleeding }}</p>
        <p class="text-white/50 text-sm">Bleeding sites</p>
      </div>
      <div>
        <p class="text-2xl font-bold text-white" :class="maxPdOverall > 5 ? 'text-red-400' : ''">
          {{ maxPdOverall || '-' }}mm
        </p>
        <p class="text-white/50 text-sm">Max pocket depth</p>
      </div>
    </div>

    <div v-if="transcription" class="pt-3 border-t border-white/10">
      <p class="text-white/40 text-sm font-semibold mb-1">Transcription</p>
      <p class="text-white/80 text-sm">{{ transcription }}</p>
    </div>

    <div v-if="extractionNotes" class="pt-3 border-t border-white/10">
      <p class="text-dental-light text-sm font-semibold mb-1">Notes</p>
      <p class="text-white/70 text-sm">{{ extractionNotes }}</p>
    </div>
  </div>
</template>
