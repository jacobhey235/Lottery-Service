import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const userId = ref(localStorage.getItem('userId') || null)
  const photoId = ref(localStorage.getItem('photoId') || null)

  function setUser(uid, pid) {
    userId.value = uid
    photoId.value = pid
    localStorage.setItem('userId', uid)
    localStorage.setItem('photoId', pid)
  }

  function clear() {
    userId.value = null
    photoId.value = null
    localStorage.removeItem('userId')
    localStorage.removeItem('photoId')
  }

  return { userId, photoId, setUser, clear }
})
