<script setup>
defineProps({
  monologues: {
    type: Array,
    required: true,
    // Each: { id, title, text }
  },
  modelValue: {
    type: String,
    default: '',
  },
})

defineEmits(['update:modelValue'])
</script>

<template>
  <div class="space-y-2">
    <label class="text-psych-light text-sm font-semibold">Sample Monologues</label>
    <div class="flex flex-wrap gap-2">
      <button
        v-for="m in monologues"
        :key="m.id"
        @click="$emit('update:modelValue', m.id)"
        class="px-3 py-1.5 rounded-full text-sm transition-all"
        :class="modelValue === m.id
          ? 'bg-psych-light text-psych-purple font-semibold shadow-md'
          : 'bg-white/10 text-white/60 hover:bg-white/20'"
      >
        {{ m.title }}
      </button>
    </div>
    <p
      v-if="modelValue"
      class="text-white/50 text-sm italic bg-white/5 rounded-lg p-3 mt-2"
    >
      "{{ monologues.find(m => m.id === modelValue)?.text || '' }}"
    </p>
  </div>
</template>
