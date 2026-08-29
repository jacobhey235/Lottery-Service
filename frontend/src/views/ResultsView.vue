<template>
  <div class="page results-page">
    <div class="results-header">
      <div class="emoji-big">🏆</div>
      <h1 class="card-title">Результаты конкурса</h1>
    </div>

    <div class="rankings">
      <div
        v-for="item in contestStore.rankings"
        :key="item.photo_id"
        class="rank-card"
        :class="{ gold: item.rank === 1, silver: item.rank === 2, bronze: item.rank === 3 }"
      >
        <div class="rank-medal">
          {{ item.rank === 1 ? '🥇' : item.rank === 2 ? '🥈' : item.rank === 3 ? '🥉' : item.rank }}
        </div>

        <div class="rank-photo-wrap">
          <img
            :src="imgSrc(item.photo_id)"
            class="rank-photo"
            alt=""
            loading="lazy"
          />
        </div>

        <div class="rank-stats">
          <div class="stat like">
            <span class="stat-icon">❤️</span>
            <span class="stat-num">{{ item.like_count }}</span>
          </div>
          <div class="stat skip">
            <span class="stat-icon">👎</span>
            <span class="stat-num">{{ item.skip_count }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useContestStore } from '../stores/contest'
import { useUserStore } from '../stores/user'

const contestStore = useContestStore()
const userStore = useUserStore()
const BASE = import.meta.env.VITE_API_BASE_URL || ''

function imgSrc(photoId) {
  return `${BASE}/api/photos/${photoId}/image`
}
</script>

<style scoped>
.results-page {
  padding: 24px 16px;
  justify-content: flex-start;
  gap: 16px;
}
.results-header { text-align: center; padding-top: 16px; }
.rankings {
  width: 100%;
  max-width: 520px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 32px;
}
.rank-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  overflow: hidden;
}
.rank-card.gold { border-color: #f5c518; }
.rank-card.silver { border-color: #aaa; }
.rank-card.bronze { border-color: #cd7f32; }

.rank-medal {
  font-size: 1.6rem;
  min-width: 36px;
  text-align: center;
}
.rank-photo-wrap {
  flex: 1;
  max-height: 80px;
  overflow: hidden;
  border-radius: var(--radius-sm);
}
.rank-photo {
  width: 100%;
  height: 80px;
  object-fit: cover;
  display: block;
}
.rank-stats {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 64px;
  align-items: flex-end;
}
.stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
}
.stat-icon { font-size: 1rem; }
.stat-num { font-size: 1.1rem; }
</style>
