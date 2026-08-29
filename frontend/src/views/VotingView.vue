<template>
  <div class="page voting-page">
    <div class="voting-header">
      <span class="counter">{{ current }} / {{ total }}</span>
      <div class="progress-bar" style="flex:1;margin:0 12px">
        <div class="progress-bar-fill" :style="{ width: progressPct + '%' }"></div>
      </div>
    </div>

    <div class="photo-card" v-if="photoId && !loading">
      <img
        :src="imgSrc"
        :key="photoId"
        class="photo-img"
        alt="Фото участника"
        @load="imgLoaded = true"
        @error="imgLoaded = true"
      />
    </div>

    <div class="photo-card loading-card" v-else-if="loading">
      <div class="spinner"></div>
    </div>

    <div v-if="error" class="error-msg" style="margin: 8px 0">{{ error }}</div>

    <div class="vote-buttons" v-if="photoId">
      <button class="btn btn-danger vote-btn" :disabled="voting" @click="vote(false)">
        <span>👎</span> Пропустить
      </button>
      <button class="btn btn-success vote-btn" :disabled="voting" @click="vote(true)">
        <span>❤️</span> Нравится
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useUserStore } from '../stores/user'
import { useContestStore } from '../stores/contest'
import { apiVote, photoUrl } from '../composables/useApi'

const userStore = useUserStore()
const contestStore = useContestStore()
const voting = ref(false)
const error = ref('')
const imgLoaded = ref(false)
const loading = ref(false)

const BASE = import.meta.env.VITE_API_BASE_URL || ''

const photoId = computed(() => contestStore.currentPhotoId())
const total = computed(() => contestStore.queue.length)
const current = computed(() => Math.min(contestStore.currentIndex + 1, total.value))
const progressPct = computed(() => total.value > 0 ? (contestStore.currentIndex / total.value) * 100 : 0)

const imgSrc = computed(() => {
  if (!photoId.value) return ''
  return `${BASE}/api/photos/${photoId.value}/image?user_id=${userStore.userId}`
})

watch(photoId, () => {
  imgLoaded.value = false
  error.value = ''
})

async function vote(liked) {
  if (voting.value || !photoId.value) return
  voting.value = true
  error.value = ''
  try {
    await apiVote(userStore.userId, photoId.value, liked)
    contestStore.advance()
  } catch (e) {
    error.value = e?.detail || 'Ошибка голосования'
  } finally {
    voting.value = false
  }
}
</script>

<style scoped>
.voting-page {
  padding: 16px;
  gap: 16px;
}
.voting-header {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 480px;
}
.counter {
  color: var(--color-text-muted);
  font-size: 0.9rem;
  white-space: nowrap;
}
.photo-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  overflow: hidden;
  width: 100%;
  max-width: 480px;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.photo-img {
  width: 100%;
  max-height: 60vh;
  object-fit: contain;
  display: block;
}
.loading-card { min-height: 300px; }
.vote-buttons {
  display: flex;
  gap: 12px;
  width: 100%;
  max-width: 480px;
}
.vote-btn {
  flex: 1;
  font-size: 1rem;
  padding: 16px;
}
</style>
