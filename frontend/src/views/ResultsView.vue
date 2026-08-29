<template>
  <div class="page results-page">
    <div class="results-header">
      <div class="emoji-big">🏆</div>
      <h1 class="card-title">Результаты конкурса</h1>
    </div>

    <!-- Podium: top 3 -->
    <div v-if="top3.length" class="podium">
      <!-- 2nd place (left) -->
      <div v-if="top3[1]" class="podium-slot" @click="openLightbox(top3[1])">
        <div class="podium-medal">🥈</div>
        <div class="podium-photo-wrap silver">
          <img :src="imgSrc(top3[1].photo_id)" class="podium-photo" alt="" loading="lazy" />
        </div>
        <div class="podium-stats">❤️ {{ top3[1].like_count }} · 👎 {{ top3[1].skip_count }}</div>
        <div class="podium-block pb-silver">2</div>
      </div>

      <!-- 1st place (center) -->
      <div class="podium-slot" @click="openLightbox(top3[0])">
        <div class="podium-medal">🥇</div>
        <div class="podium-photo-wrap gold">
          <img :src="imgSrc(top3[0].photo_id)" class="podium-photo" alt="" loading="lazy" />
        </div>
        <div class="podium-stats">❤️ {{ top3[0].like_count }} · 👎 {{ top3[0].skip_count }}</div>
        <div class="podium-block pb-gold">1</div>
      </div>

      <!-- 3rd place (right) -->
      <div v-if="top3[2]" class="podium-slot" @click="openLightbox(top3[2])">
        <div class="podium-medal">🥉</div>
        <div class="podium-photo-wrap bronze">
          <img :src="imgSrc(top3[2].photo_id)" class="podium-photo" alt="" loading="lazy" />
        </div>
        <div class="podium-stats">❤️ {{ top3[2].like_count }} · 👎 {{ top3[2].skip_count }}</div>
        <div class="podium-block pb-bronze">3</div>
      </div>
    </div>

    <!-- 4th place and below -->
    <div v-if="rest.length" class="rest-list">
      <div
        v-for="item in rest"
        :key="item.photo_id"
        class="rest-row"
        @click="openLightbox(item)"
      >
        <span class="rest-rank">{{ item.rank }}</span>
        <img :src="imgSrc(item.photo_id)" class="rest-thumb" alt="" loading="lazy" />
        <div class="rest-stats">
          <span>❤️ {{ item.like_count }}</span>
          <span>👎 {{ item.skip_count }}</span>
        </div>
      </div>
    </div>

    <!-- Lightbox -->
    <Teleport to="body">
      <div
        v-if="lightboxItem"
        class="lightbox"
        @click.self="lightboxItem = null"
        @keydown.esc="lightboxItem = null"
        tabindex="0"
        ref="lightboxEl"
      >
        <button class="lightbox-close" @click="lightboxItem = null">✕</button>
        <img :src="imgSrc(lightboxItem.photo_id)" class="lightbox-img" alt="" />
        <div class="lightbox-info">
          <span>{{ lightboxItem.rank === 1 ? '🥇' : lightboxItem.rank === 2 ? '🥈' : lightboxItem.rank === 3 ? '🥉' : `#${lightboxItem.rank}` }}</span>
          <span>❤️ {{ lightboxItem.like_count }}</span>
          <span>👎 {{ lightboxItem.skip_count }}</span>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useContestStore } from '../stores/contest'

const contestStore = useContestStore()
const BASE = import.meta.env.VITE_API_BASE_URL || ''

function imgSrc(photoId) {
  return `${BASE}/api/photos/${photoId}/image`
}

const top3 = computed(() => contestStore.rankings.slice(0, 3))
const rest = computed(() => contestStore.rankings.slice(3))

const lightboxItem = ref(null)
const lightboxEl = ref(null)

watch(lightboxItem, (val) => {
  if (val) nextTick(() => lightboxEl.value?.focus())
})

function openLightbox(item) {
  lightboxItem.value = item
}
</script>

<style scoped>
.results-page {
  padding: 24px 16px 48px;
  justify-content: flex-start;
  gap: 24px;
}
.results-header { text-align: center; padding-top: 8px; }

/* ── Podium ── */
.podium {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 8px;
  width: 100%;
  max-width: 480px;
}

.podium-slot {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}
.podium-slot:hover .podium-photo { filter: brightness(1.08); }

.podium-medal {
  font-size: 1.6rem;
  line-height: 1;
  margin-bottom: 6px;
}

.podium-photo-wrap {
  width: 100%;
  border-radius: 10px 10px 0 0;
  overflow: hidden;
  border-width: 2px;
  border-style: solid;
}
.podium-photo-wrap.gold   { border-color: #f5c518; }
.podium-photo-wrap.silver { border-color: #aaa; }
.podium-photo-wrap.bronze { border-color: #cd7f32; }

.podium-photo {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  display: block;
  transition: filter 0.15s;
}

.podium-stats {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--color-text-muted);
  padding: 5px 4px;
  text-align: center;
  white-space: nowrap;
}

.podium-block {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  font-weight: 900;
  color: rgba(255, 255, 255, 0.55);
  border-radius: 0 0 6px 6px;
}
.pb-gold   { background: #b8900a; height: 80px; }
.pb-silver { background: #808080; height: 55px; }
.pb-bronze { background: #9c5c1a; height: 36px; }

/* ── Rest list ── */
.rest-list {
  width: 100%;
  max-width: 480px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rest-row {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 10px 14px;
  cursor: pointer;
  transition: background 0.15s;
}
.rest-row:hover { background: var(--color-surface2); }

.rest-rank {
  font-size: 1rem;
  font-weight: 700;
  min-width: 28px;
  text-align: center;
  color: var(--color-text-muted);
}

.rest-thumb {
  width: 56px;
  height: 56px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.rest-stats {
  display: flex;
  gap: 16px;
  font-size: 0.9rem;
  font-weight: 600;
}

/* ── Lightbox ── */
.lightbox {
  position: fixed;
  inset: 0;
  z-index: 99999;
  background: rgba(0, 0, 0, 0.88);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  outline: none;
}

.lightbox-close {
  position: absolute;
  top: 16px;
  right: 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 1rem;
  cursor: pointer;
}
.lightbox-close:hover { background: rgba(255, 255, 255, 0.2); }

.lightbox-img {
  max-width: 90vw;
  max-height: 78vh;
  object-fit: contain;
  border-radius: 12px;
  box-shadow: 0 8px 48px rgba(0, 0, 0, 0.6);
}

.lightbox-info {
  display: flex;
  gap: 20px;
  font-size: 1.1rem;
  font-weight: 700;
  color: #fff;
}
</style>
