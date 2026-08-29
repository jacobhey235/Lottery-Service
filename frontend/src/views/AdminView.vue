<template>
  <div class="page admin-page">
    <!-- Login form -->
    <div v-if="!token" class="card">
      <div class="emoji-big">🔐</div>
      <h1 class="card-title">Панель администратора</h1>
      <p class="card-subtitle">Введите пароль для входа</p>
      <div class="field">
        <label class="label">Пароль</label>
        <input
          v-model="password"
          class="input"
          type="password"
          placeholder="Пароль администратора"
          @keydown.enter="login"
        />
      </div>
      <p v-if="loginError" class="error-msg">{{ loginError }}</p>
      <button class="btn btn-primary" :disabled="loggingIn" @click="login">
        {{ loggingIn ? 'Входим…' : 'Войти' }}
      </button>
    </div>

    <!-- Admin panel -->
    <div v-else class="admin-content">
      <div class="admin-top-bar">
        <h1 class="admin-title">Панель администратора</h1>
        <span class="phase-badge" :class="phase">
          {{ phaseLabel }}
        </span>
        <button class="btn btn-ghost btn-fullscreen" @click="showFullscreen = true" title="Полноэкранный режим">
          ⛶ На весь экран
        </button>
      </div>

      <!-- Controls -->
      <div class="controls card" style="margin-bottom:16px">
        <div class="controls-row">
          <button
            v-if="phase === 'upload'"
            class="btn btn-primary"
            :disabled="actionLoading || photos.length < 2"
            :title="photos.length < 2 ? 'Нужно хотя бы 2 фотографии' : ''"
            @click="startContest"
          >
            🚀 Начать конкурс
          </button>
          <span v-if="phase === 'upload' && photos.length < 2 && photos.length > 0" class="hint-msg">
            Загружено {{ photos.length }} из 2 необходимых фото
          </span>
          <button
            v-if="phase === 'voting'"
            class="btn btn-danger"
            :disabled="actionLoading"
            @click="endContest"
          >
            🏁 Завершить конкурс
          </button>
          <button
            v-if="phase === 'finished'"
            class="btn btn-ghost"
            :disabled="actionLoading"
            @click="restartContest"
          >
            🔄 Начать заново
          </button>
          <span v-if="actionError" class="error-msg" style="margin:0">{{ actionError }}</span>
        </div>
      </div>

      <!-- Photos grid -->
      <div class="photos-section card">
        <h2 class="section-title">
          Фотографии ({{ photos.length }})
        </h2>

        <div v-if="photosLoading" class="spinner" style="margin:24px auto"></div>

        <div v-else-if="photos.length === 0" class="empty-state">
          Пока нет загруженных фотографий
        </div>

        <div v-else class="photos-grid">
          <div v-for="p in photos" :key="p.photo_id" class="photo-item">
            <img
              :src="adminPhotoSrc(p.photo_id)"
              class="admin-photo"
              alt=""
              loading="lazy"
            />
            <div class="photo-meta">
              <span class="photo-stats">❤️ {{ p.like_count }} / 👎 {{ p.skip_count }}</span>
              <button
                v-if="phase === 'upload' || phase === 'voting'"
                class="btn btn-danger btn-sm delete-btn"
                @click="deletePhoto(p.photo_id)"
              >
                🗑️
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Results (when finished) -->
      <div v-if="phase === 'finished'" class="results-section card">
        <h2 class="section-title">Итоги</h2>
        <div class="rankings-list">
          <div v-for="p in sortedPhotos" :key="p.photo_id" class="result-row">
            <span class="result-rank">{{ p._rank }}</span>
            <img :src="adminPhotoSrc(p.photo_id)" class="result-thumb" alt="" />
            <div class="result-stats">
              <span>❤️ {{ p.like_count }}</span>
              <span>👎 {{ p.skip_count }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Fullscreen overlay -->
    <Teleport to="body">
      <div v-if="showFullscreen" class="fs-overlay" @keydown.esc="showFullscreen = false" tabindex="0" ref="fsOverlay">
        <button class="fs-close" @click="showFullscreen = false">✕ Закрыть</button>

        <div class="fs-header">
          <span class="fs-phase-badge" :class="phase">{{ phaseLabel }}</span>
          <h1 class="fs-title">
            {{ phase === 'finished' ? '🏆 Результаты конкурса' : phase === 'voting' ? '🗳️ Идёт голосование' : '📷 Загруженные фотографии' }}
          </h1>
        </div>

        <div v-if="sortedPhotos.length === 0" class="fs-empty">
          Нет фотографий
        </div>

        <div v-else class="fs-grid" :class="{ 'fs-grid-few': sortedPhotos.length <= 3 }">
          <div
            v-for="(p, idx) in sortedPhotos"
            :key="p.photo_id"
            class="fs-card"
            :class="{ 'fs-card-gold': idx === 0, 'fs-card-silver': idx === 1, 'fs-card-bronze': idx === 2 }"
          >
            <div class="fs-rank">{{ p._rank }}</div>
            <img :src="adminPhotoSrc(p.photo_id)" class="fs-photo" alt="" />
            <div class="fs-stats">
              <span class="fs-likes">❤️ {{ p.like_count }}</span>
              <span class="fs-skips">👎 {{ p.skip_count }}</span>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import {
  adminDeletePhoto, adminEndContest, adminListPhotos,
  adminLogin, adminRestartContest, adminStartContest,
} from '../composables/useApi'
import { useAdminWebSocket } from '../composables/useWebSocket'

const BASE = import.meta.env.VITE_API_BASE_URL || ''

const password = ref('')
const token = ref(sessionStorage.getItem('adminToken') || '')
const loggingIn = ref(false)
const loginError = ref('')

const phase = ref('upload')
const photos = ref([])
const photosLoading = ref(false)
const actionLoading = ref(false)
const actionError = ref('')

const showFullscreen = ref(false)
const fsOverlay = ref(null)

watch(showFullscreen, (val) => {
  if (val) {
    nextTick(() => fsOverlay.value?.focus())
  }
})

const phaseLabel = computed(() => ({
  upload: 'Приём фотографий',
  voting: 'Голосование',
  finished: 'Завершён',
}[phase.value] || phase.value))

const sortedPhotos = computed(() =>
  [...photos.value]
    .sort((a, b) => b.like_count - a.like_count)
    .map((p, i) => ({ ...p, _rank: i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : i + 1 }))
)

function adminPhotoSrc(photoId) {
  return `${BASE}/api/photos/${photoId}/image?admin_token=${token.value}`
}

const { connect } = useAdminWebSocket(
  () => token.value,
  handleWsMessage,
)

function handleWsMessage(msg) {
  if (msg.event === 'phase_sync') phase.value = msg.phase
  if (msg.event === 'contest_started') { phase.value = 'voting'; loadPhotos() }
  if (msg.event === 'contest_finished') { phase.value = 'finished'; loadPhotos() }
  if (msg.event === 'contest_restarted') { phase.value = 'upload'; photos.value = [] }

  if (msg.event === 'photo_uploaded') {
    photos.value.push({
      photo_id: msg.photo_id,
      like_count: msg.like_count,
      skip_count: msg.skip_count,
    })
  }

  if (msg.event === 'photo_deleted') {
    photos.value = photos.value.filter(p => p.photo_id !== msg.photo_id)
  }

  if (msg.event === 'vote_updated') {
    const photo = photos.value.find(p => p.photo_id === msg.photo_id)
    if (photo) {
      photo.like_count = msg.like_count
      photo.skip_count = msg.skip_count
    }
  }
}

async function login() {
  loggingIn.value = true
  loginError.value = ''
  try {
    const data = await adminLogin(password.value)
    token.value = data.token
    sessionStorage.setItem('adminToken', data.token)
    await init()
  } catch (e) {
    loginError.value = e?.detail || 'Неверный пароль'
  } finally {
    loggingIn.value = false
  }
}

async function init() {
  await loadPhotos()
  connect()
}

async function loadPhotos() {
  photosLoading.value = true
  try {
    const data = await adminListPhotos(token.value)
    photos.value = data.photos
  } catch {
    photos.value = []
  } finally {
    photosLoading.value = false
  }
}

async function deletePhoto(photoId) {
  try {
    await adminDeletePhoto(token.value, photoId)
    photos.value = photos.value.filter(p => p.photo_id !== photoId)
  } catch (e) {
    actionError.value = e?.detail || 'Ошибка удаления'
    setTimeout(() => { actionError.value = '' }, 3000)
  }
}

async function startContest() {
  actionLoading.value = true
  actionError.value = ''
  try {
    await adminStartContest(token.value)
    phase.value = 'voting'
  } catch (e) {
    actionError.value = e?.detail || 'Ошибка'
  } finally {
    actionLoading.value = false
  }
}

async function endContest() {
  actionLoading.value = true
  actionError.value = ''
  try {
    await adminEndContest(token.value)
    phase.value = 'finished'
    await loadPhotos()
  } catch (e) {
    actionError.value = e?.detail || 'Ошибка'
  } finally {
    actionLoading.value = false
  }
}

async function restartContest() {
  if (!confirm('Удалить все данные и начать заново?')) return
  actionLoading.value = true
  actionError.value = ''
  try {
    await adminRestartContest(token.value)
    phase.value = 'upload'
    photos.value = []
  } catch (e) {
    actionError.value = e?.detail || 'Ошибка'
  } finally {
    actionLoading.value = false
  }
}

onMounted(async () => {
  if (token.value) await init()
})
</script>

<style scoped>
.admin-page {
  justify-content: flex-start;
  padding: 16px;
  align-items: stretch;
}
.admin-content {
  width: 100%;
  max-width: 860px;
  margin: 0 auto;
  padding-bottom: 40px;
}
.admin-top-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0 16px;
  flex-wrap: wrap;
}
.admin-title { font-size: 1.3rem; font-weight: 700; flex: 1; }
.phase-badge {
  font-size: 0.78rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 100px;
  background: var(--color-surface2);
  border: 1px solid var(--color-border);
}
.phase-badge.voting { background: rgba(82, 183, 136, 0.15); border-color: var(--color-success); color: var(--color-success); }
.phase-badge.finished { background: rgba(124, 110, 240, 0.15); border-color: var(--color-primary); color: var(--color-primary); }

.btn-fullscreen {
  width: auto;
  padding: 6px 14px;
  font-size: 0.85rem;
  white-space: nowrap;
}

.controls-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.controls-row .btn { width: auto; }
.section-title { font-size: 1rem; font-weight: 700; margin-bottom: 16px; }
.photos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}
.photo-item {
  background: var(--color-surface2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  overflow: hidden;
}
.admin-photo {
  width: 100%;
  height: 120px;
  object-fit: cover;
  display: block;
}
.photo-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 8px;
}
.photo-stats { font-size: 0.78rem; color: var(--color-text-muted); }
.delete-btn { width: auto; padding: 4px 8px; }
.hint-msg {
  font-size: 0.82rem;
  color: var(--color-text-muted);
}
.empty-state {
  color: var(--color-text-muted);
  text-align: center;
  padding: 32px 0;
  font-size: 0.9rem;
}
.results-section { margin-top: 16px; }
.rankings-list { display: flex; flex-direction: column; gap: 8px; }
.result-row {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--color-surface2);
  border-radius: var(--radius-sm);
  padding: 8px;
}
.result-rank { font-size: 1.4rem; min-width: 32px; text-align: center; }
.result-thumb {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: var(--radius-sm);
}
.result-stats { display: flex; gap: 12px; font-size: 0.9rem; font-weight: 600; }

@media (min-width: 600px) {
  .photos-grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); }
}

/* ── Fullscreen overlay ── */
.fs-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: #08080f;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 24px 32px;
  overflow-y: auto;
  outline: none;
}

.fs-close {
  position: fixed;
  top: 16px;
  right: 20px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  color: var(--color-text-muted);
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  z-index: 10000;
}
.fs-close:hover { background: rgba(255,255,255,0.15); color: var(--color-text); }

.fs-header {
  text-align: center;
  margin-bottom: 36px;
  margin-top: 8px;
}
.fs-title {
  font-size: clamp(1.8rem, 4vw, 3rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-top: 10px;
}
.fs-phase-badge {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 100px;
  background: var(--color-surface2);
  border: 1px solid var(--color-border);
}
.fs-phase-badge.voting { background: rgba(82, 183, 136, 0.2); border-color: var(--color-success); color: var(--color-success); }
.fs-phase-badge.finished { background: rgba(124, 110, 240, 0.2); border-color: var(--color-primary); color: var(--color-primary); }

.fs-empty {
  color: var(--color-text-muted);
  font-size: 1.2rem;
  margin-top: 80px;
}

.fs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
  width: 100%;
  max-width: 1200px;
}
.fs-grid.fs-grid-few {
  grid-template-columns: repeat(auto-fit, minmax(260px, 340px));
  justify-content: center;
}

.fs-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s;
}
.fs-card:hover { transform: translateY(-3px); }

.fs-card-gold  { border-color: #f0c040; box-shadow: 0 0 24px rgba(240,192,64,0.25); }
.fs-card-silver { border-color: #b0b8c8; box-shadow: 0 0 16px rgba(176,184,200,0.2); }
.fs-card-bronze { border-color: #c87840; box-shadow: 0 0 16px rgba(200,120,64,0.2); }

.fs-rank {
  text-align: center;
  font-size: clamp(2rem, 4vw, 3rem);
  padding: 12px 0 4px;
  line-height: 1;
}

.fs-photo {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  display: block;
}

.fs-stats {
  display: flex;
  justify-content: center;
  gap: 24px;
  padding: 14px 12px;
  font-size: clamp(1.1rem, 2.5vw, 1.5rem);
  font-weight: 700;
}
.fs-likes { color: #f07070; }
.fs-skips { color: var(--color-text-muted); }
</style>
