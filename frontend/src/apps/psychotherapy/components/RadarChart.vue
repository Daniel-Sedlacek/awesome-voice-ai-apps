<script setup>
import { computed } from 'vue'

const props = defineProps({
  metrics: {
    type: Object,
    required: true,
  },
})

const metricLabels = ['Anxiety', 'Depression', 'Stress', 'Stability', 'Positivity', 'Energy']
const metricKeys = ['anxiety', 'depression', 'stress', 'emotional_stability', 'positive_affect', 'energy_level']
const metricColors = {
  anxiety: '#EF4444',
  depression: '#6366F1',
  stress: '#F59E0B',
  emotional_stability: '#10B981',
  positive_affect: '#EC4899',
  energy_level: '#8B5CF6',
}

const size = 200
const center = size / 2
const maxRadius = 80
const levels = 5

// Generate polygon points for each level
function getPolygonPoints(radius) {
  return metricKeys.map((_, i) => {
    const angle = (Math.PI * 2 * i) / metricKeys.length - Math.PI / 2
    return `${center + radius * Math.cos(angle)},${center + radius * Math.sin(angle)}`
  }).join(' ')
}

const dataPoints = computed(() => {
  return metricKeys.map((key, i) => {
    const value = props.metrics[key] || 0
    const radius = (value / 10) * maxRadius
    const angle = (Math.PI * 2 * i) / metricKeys.length - Math.PI / 2
    return {
      x: center + radius * Math.cos(angle),
      y: center + radius * Math.sin(angle),
      value,
      label: metricLabels[i],
      color: metricColors[key],
      labelX: center + (maxRadius + 20) * Math.cos(angle),
      labelY: center + (maxRadius + 20) * Math.sin(angle),
    }
  })
})

const dataPolygon = computed(() => {
  return dataPoints.value.map(p => `${p.x},${p.y}`).join(' ')
})
</script>

<template>
  <div class="bg-white/10 rounded-2xl p-6">
    <h3 class="text-psych-light font-bold text-lg mb-4 text-center">Psychological Metrics</h3>

    <svg :viewBox="`0 0 ${size} ${size}`" class="w-full max-w-xs mx-auto">
      <!-- Grid levels -->
      <polygon
        v-for="l in levels"
        :key="l"
        :points="getPolygonPoints((maxRadius / levels) * l)"
        fill="none"
        stroke="white"
        :stroke-opacity="0.1"
        stroke-width="0.5"
      />

      <!-- Axes -->
      <line
        v-for="(_, i) in metricKeys"
        :key="`axis-${i}`"
        :x1="center"
        :y1="center"
        :x2="center + maxRadius * Math.cos((Math.PI * 2 * i) / metricKeys.length - Math.PI / 2)"
        :y2="center + maxRadius * Math.sin((Math.PI * 2 * i) / metricKeys.length - Math.PI / 2)"
        stroke="white"
        stroke-opacity="0.1"
        stroke-width="0.5"
      />

      <!-- Data polygon -->
      <polygon
        :points="dataPolygon"
        fill="rgba(167, 139, 250, 0.2)"
        stroke="#A78BFA"
        stroke-width="1.5"
      />

      <!-- Data points -->
      <circle
        v-for="(point, i) in dataPoints"
        :key="`point-${i}`"
        :cx="point.x"
        :cy="point.y"
        r="3"
        :fill="point.color"
      />

      <!-- Labels -->
      <text
        v-for="(point, i) in dataPoints"
        :key="`label-${i}`"
        :x="point.labelX"
        :y="point.labelY"
        text-anchor="middle"
        dominant-baseline="central"
        fill="white"
        fill-opacity="0.7"
        font-size="7"
      >
        {{ point.label }} ({{ point.value }})
      </text>
    </svg>

    <!-- Metric bars -->
    <div class="mt-4 space-y-2">
      <div v-for="(key, i) in metricKeys" :key="key" class="flex items-center gap-2">
        <span class="text-white/60 text-xs w-16 text-right">{{ metricLabels[i] }}</span>
        <div class="flex-1 bg-white/10 rounded-full h-2">
          <div
            class="h-2 rounded-full transition-all"
            :style="{ width: `${(metrics[key] || 0) * 10}%`, backgroundColor: metricColors[key] }"
          />
        </div>
        <span class="text-white/80 text-xs w-4">{{ metrics[key] || 0 }}</span>
      </div>
    </div>
  </div>
</template>
