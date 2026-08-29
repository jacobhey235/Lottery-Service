<template>
  <div class="page">
    <div class="card">
      <div class="emoji-big">📷</div>
      <h1 class="card-title">Фотоконкурс</h1>
      <p class="card-subtitle">Загрузите одну фотографию для участия</p>

      <div v-if="!uploading">
        <div class="field">
          <label class="label">Фотография</label>
          <div class="drop-zone" :class="{ active: dragOver }"
            @dragover.prevent="dragOver = true"
            @dragleave="dragOver = false"
            @drop.prevent="onDrop"
            @click="fileInput.click()">
            <div v-if="preview" class="preview-wrap">
              <img :src="preview" alt="preview" class="preview-img" />
            </div>
            <div v-else class="drop-hint">
              <span class="drop-icon">🖼️</span>
              <span>Нажмите или перетащите файл</span>
              <span class="drop-sub">JPEG, PNG, WebP, GIF — до 10 МБ</span>
            </div>
          </div>
          <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="onFileChange" />
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <button class="btn btn-primary" :disabled="!selectedFile" @click="submit">
          Участвовать
        </button>
      </div>

      <div v-else class="uploading">
        <div class="spinner"></div>
        <p style="text-align:center;color:var(--color-text-muted)">Загрузка…</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useUserStore } from '../stores/user'
import { apiUpload } from '../composables/useApi'

const emit = defineEmits(['uploaded'])
const userStore = useUserStore()

const fileInput = ref(null)
const selectedFile = ref(null)
const preview = ref(null)
const uploading = ref(false)
const error = ref('')
const dragOver = ref(false)

function onFileChange(e) {
  const file = e.target.files[0]
  if (file) setFile(file)
}

function onDrop(e) {
  dragOver.value = false
  const file = e.dataTransfer.files[0]
  if (file) setFile(file)
}

function setFile(file) {
  error.value = ''
  if (!file.type.startsWith('image/')) {
    error.value = 'Выберите файл изображения'
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    error.value = 'Файл слишком большой — максимум 10 МБ'
    return
  }
  selectedFile.value = file
  preview.value = URL.createObjectURL(file)
}

async function submit() {
  if (!selectedFile.value) return
  uploading.value = true
  error.value = ''
  try {
    const form = new FormData()
    form.append('photo', selectedFile.value)
    const data = await apiUpload(form)
    userStore.setUser(data.user_id, data.photo_id)
    emit('uploaded')
  } catch (e) {
    error.value = e?.detail || 'Ошибка загрузки, попробуйте ещё раз'
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.drop-zone {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius);
  padding: 24px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  margin-bottom: 16px;
  min-height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.drop-zone.active, .drop-zone:hover {
  border-color: var(--color-primary);
  background: rgba(124, 110, 240, 0.05);
}
.drop-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: var(--color-text-muted);
  font-size: 0.9rem;
  text-align: center;
}
.drop-icon { font-size: 2rem; }
.drop-sub { font-size: 0.78rem; }
.preview-wrap { width: 100%; }
.preview-img {
  width: 100%;
  max-height: 240px;
  object-fit: contain;
  border-radius: var(--radius-sm);
}
.uploading { padding: 16px 0; }
</style>
