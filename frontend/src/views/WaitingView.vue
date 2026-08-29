<template>
  <div class="page">
    <div class="card" style="text-align:center">
      <div class="spinner"></div>
      <h2 class="card-title">{{ title }}</h2>
      <p class="card-subtitle">{{ subtitle }}</p>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  phase: { type: String, default: 'upload' },
  doneVoting: { type: Boolean, default: false },
})

const title = props.doneVoting
  ? 'Вы проголосовали!'
  : props.phase === 'upload'
    ? 'Ожидание начала конкурса'
    : 'Ожидание завершения'

const subtitle = props.doneVoting
  ? 'Ждём, пока остальные участники завершат голосование'
  : props.phase === 'upload'
    ? 'Администратор скоро запустит голосование'
    : 'Результаты появятся автоматически'
</script>
