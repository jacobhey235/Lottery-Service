<template>
  <div>
    <!-- Not uploaded yet -->
    <template v-if="!userStore.userId">
      <div v-if="phase === 'upload'">
        <UploadView @uploaded="onUploaded" />
      </div>
      <div v-else class="page">
        <div class="card" style="text-align:center">
          <div class="emoji-big">🔒</div>
          <h2 class="card-title">Приём фотографий завершён</h2>
          <p class="card-subtitle">Конкурс уже идёт, загрузка закрыта</p>
        </div>
      </div>
    </template>

    <!-- Uploaded, waiting for contest to start -->
    <WaitingView v-else-if="phase === 'upload'" :phase="phase" />

    <!-- Voting phase -->
    <template v-else-if="phase === 'voting'">
      <VotingView v-if="!contestStore.isDoneVoting()" />
      <WaitingView v-else :phase="phase" :done-voting="true" />
    </template>

    <!-- Results -->
    <ResultsView v-else-if="phase === 'finished'" />

    <!-- Fallback -->
    <WaitingView v-else :phase="phase" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useContestStore } from '../stores/contest'
import { useUserStore } from '../stores/user'
import { apiResults, apiStatus, apiVotingQueue } from '../composables/useApi'
import { useWebSocket } from '../composables/useWebSocket'
import UploadView from './UploadView.vue'
import WaitingView from './WaitingView.vue'
import VotingView from './VotingView.vue'
import ResultsView from './ResultsView.vue'

const userStore = useUserStore()
const contestStore = useContestStore()
const phase = ref('upload')

async function syncPhase(newPhase) {
  phase.value = newPhase
  contestStore.setPhase(newPhase)

  if (newPhase === 'voting' && userStore.userId) {
    try {
      const data = await apiVotingQueue(userStore.userId)
      contestStore.setQueue(data.queue)
    } catch (e) {
      console.error('Failed to load voting queue:', e)
    }
  }

  if (newPhase === 'finished') {
    try {
      const data = await apiResults()
      contestStore.setRankings(data.rankings)
    } catch (e) {
      console.error('Failed to load results:', e)
    }
  }
}

function handleWsMessage(msg) {
  if (msg.event === 'phase_sync') syncPhase(msg.phase)
  if (msg.event === 'contest_started') syncPhase('voting')
  if (msg.event === 'contest_finished') syncPhase('finished')
  if (msg.event === 'contest_restarted') {
    userStore.clear()
    contestStore.setPhase('upload')
    contestStore.setQueue([])
    contestStore.setRankings([])
    phase.value = 'upload'
    wsConnected = false
  }
  if (msg.event === 'photo_deleted') {
    contestStore.removeFromQueue(msg.photo_id)
  }
}

function handleWsAuthFailed() {
  userStore.clear()
  contestStore.setPhase('upload')
  contestStore.setQueue([])
  contestStore.setRankings([])
  phase.value = 'upload'
  wsConnected = false
}

// Pass a getter so connect() always uses the current userId
const { connect } = useWebSocket(() => userStore.userId, handleWsMessage, handleWsAuthFailed)

let wsConnected = false
function connectWs() {
  if (wsConnected || !userStore.userId) return
  wsConnected = true
  connect()
}

async function onUploaded() {
  const status = await apiStatus()
  await syncPhase(status.phase)
  connectWs()
}

onMounted(async () => {
  const status = await apiStatus()
  await syncPhase(status.phase)
  connectWs()
})
</script>
