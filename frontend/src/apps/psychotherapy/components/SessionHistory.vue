<script setup>
defineProps({
  sessions: {
    type: Array,
    required: true,
  },
})

const metricColors = {
  anxiety: '#EF4444',
  depression: '#6366F1',
  stress: '#F59E0B',
  emotional_stability: '#10B981',
  positive_affect: '#EC4899',
  energy_level: '#8B5CF6',
}

const metricLabels = {
  anxiety: 'Anx',
  depression: 'Dep',
  stress: 'Str',
  emotional_stability: 'Stab',
  positive_affect: 'Pos',
  energy_level: 'Eng',
}
</script>

<template>
  <div class="bg-white/10 rounded-2xl p-6">
    <h3 class="text-psych-light font-bold text-lg mb-4">Today's Sessions</h3>

    <div v-if="sessions.length === 0" class="text-white/40 text-sm text-center py-4">
      No sessions yet. Record your first one above.
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="session in sessions"
        :key="session.session_number"
        class="bg-white/5 rounded-xl p-3"
      >
        <div class="flex justify-between items-center mb-2">
          <span class="text-white font-semibold text-sm">Session {{ session.session_number }}</span>
          <span class="text-white/40 text-xs">{{ session.timestamp?.split('T')[1]?.slice(0, 5) || '' }}</span>
        </div>
        <div class="flex gap-1">
          <div
            v-for="(key, label) in metricLabels"
            :key="key"
            class="flex-1 text-center"
          >
            <div
              class="text-xs font-bold mb-0.5"
              :style="{ color: metricColors[key] }"
            >
              {{ session.metrics[key] || '-' }}
            </div>
            <div class="text-white/30 text-[9px]">{{ label }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
