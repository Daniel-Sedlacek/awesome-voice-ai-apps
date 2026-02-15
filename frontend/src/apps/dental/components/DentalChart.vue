<script setup>
import { computed } from 'vue'

const props = defineProps({
  examData: {
    type: Object,
    required: true,
  },
})

const allTeeth = {
  upper: [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28],
  lower: [48, 47, 46, 45, 44, 43, 42, 41, 31, 32, 33, 34, 35, 36, 37, 38],
}

function getSeverityColor(pd) {
  if (pd == null) return '#374151' // gray-700
  if (pd <= 3) return '#10B981'   // green
  if (pd === 4) return '#F59E0B'  // amber
  if (pd <= 6) return '#F97316'   // orange
  return '#EF4444'                // red
}

function getMaxPd(toothData) {
  if (!toothData?.sites) return null
  let max = null
  for (const site of Object.values(toothData.sites)) {
    if (site.pd != null && (max == null || site.pd > max)) {
      max = site.pd
    }
  }
  return max
}

const teeth = computed(() => {
  const teethData = props.examData?.teeth || {}
  const result = { upper: [], lower: [] }

  for (const row of ['upper', 'lower']) {
    for (const num of allTeeth[row]) {
      const data = teethData[String(num)]
      const maxPd = data ? getMaxPd(data) : null
      result[row].push({
        number: num,
        color: getSeverityColor(maxPd),
        maxPd,
        hasBleeding: data ? Object.values(data.sites || {}).some(s => s.bop === true) : false,
        hasData: !!data,
      })
    }
  }
  return result
})
</script>

<template>
  <div class="bg-white/10 rounded-2xl p-6">
    <h3 class="text-dental-light font-bold text-lg mb-4">Dental Chart</h3>

    <!-- Upper arch -->
    <div class="flex justify-center gap-1 mb-2">
      <div
        v-for="tooth in teeth.upper"
        :key="tooth.number"
        class="flex flex-col items-center"
      >
        <span class="text-white/40 text-[10px] mb-1">{{ tooth.number }}</span>
        <div
          class="w-6 h-8 rounded-t-lg border transition-colors"
          :class="tooth.hasData ? 'border-white/30' : 'border-white/10'"
          :style="{ backgroundColor: tooth.color }"
        >
          <div
            v-if="tooth.hasBleeding"
            class="w-2 h-2 bg-red-500 rounded-full mx-auto mt-0.5"
          />
        </div>
        <span v-if="tooth.maxPd" class="text-white text-[10px] mt-0.5">{{ tooth.maxPd }}</span>
      </div>
    </div>

    <!-- Divider -->
    <div class="border-t border-white/20 my-2" />

    <!-- Lower arch -->
    <div class="flex justify-center gap-1 mt-2">
      <div
        v-for="tooth in teeth.lower"
        :key="tooth.number"
        class="flex flex-col items-center"
      >
        <span v-if="tooth.maxPd" class="text-white text-[10px] mb-0.5">{{ tooth.maxPd }}</span>
        <div
          class="w-6 h-8 rounded-b-lg border transition-colors"
          :class="tooth.hasData ? 'border-white/30' : 'border-white/10'"
          :style="{ backgroundColor: tooth.color }"
        >
          <div
            v-if="tooth.hasBleeding"
            class="w-2 h-2 bg-red-500 rounded-full mx-auto mt-4"
          />
        </div>
        <span class="text-white/40 text-[10px] mt-1">{{ tooth.number }}</span>
      </div>
    </div>

    <!-- Legend -->
    <div class="flex justify-center gap-4 mt-4 text-xs text-white/60">
      <div class="flex items-center gap-1">
        <div class="w-3 h-3 rounded-sm bg-[#10B981]" />
        <span>Healthy (1-3)</span>
      </div>
      <div class="flex items-center gap-1">
        <div class="w-3 h-3 rounded-sm bg-[#F59E0B]" />
        <span>Early (4)</span>
      </div>
      <div class="flex items-center gap-1">
        <div class="w-3 h-3 rounded-sm bg-[#F97316]" />
        <span>Moderate (5-6)</span>
      </div>
      <div class="flex items-center gap-1">
        <div class="w-3 h-3 rounded-sm bg-[#EF4444]" />
        <span>Severe (7+)</span>
      </div>
      <div class="flex items-center gap-1">
        <div class="w-2 h-2 rounded-full bg-red-500" />
        <span>Bleeding</span>
      </div>
    </div>
  </div>
</template>
