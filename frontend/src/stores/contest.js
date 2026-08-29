import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useContestStore = defineStore('contest', () => {
  const phase = ref('upload')
  const queue = ref([])
  const currentIndex = ref(0)
  const rankings = ref([])

  function setPhase(p) {
    phase.value = p
  }

  function setQueue(q) {
    queue.value = q
    currentIndex.value = 0
  }

  function advance() {
    currentIndex.value++
  }

  function removeFromQueue(photoId) {
    const idx = queue.value.indexOf(photoId)
    if (idx !== -1) {
      queue.value.splice(idx, 1)
      if (currentIndex.value > idx) {
        currentIndex.value = Math.max(0, currentIndex.value - 1)
      }
    }
  }

  function setRankings(r) {
    rankings.value = r
  }

  const currentPhotoId = () => queue.value[currentIndex.value] || null
  const isDoneVoting = () => currentIndex.value >= queue.value.length

  return { phase, queue, currentIndex, rankings, setPhase, setQueue, advance, removeFromQueue, setRankings, currentPhotoId, isDoneVoting }
})
