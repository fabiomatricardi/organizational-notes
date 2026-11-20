<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { fetchInboxCount } from '../composables/useApi.js'

const props = defineProps({
  currentView: String
})

const emit = defineEmits(['navigate'])

const inboxCount = ref(0)
let timer = null

const refreshCount = async () => {
  try {
    const result = await fetchInboxCount()
    inboxCount.value = result.pending || 0
  } catch (e) {
    // offline or backend restarting - keep the last value
  }
}

onMounted(() => {
  refreshCount()
  timer = setInterval(refreshCount, 60000)
})
onUnmounted(() => { if (timer) clearInterval(timer) })

watch(() => props.currentView, (view) => {
  if (view !== 'inbox') refreshCount()
})

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: 'pi pi-home' },
  { id: 'today', label: 'Today', icon: 'pi pi-sun' },
  { id: 'inbox', label: 'Inbox', icon: 'pi pi-inbox' },
  { id: 'follow-up', label: 'Follow-up', icon: 'pi pi-flag' },
  { id: 'timeline', label: 'Log Timeline', icon: 'pi pi-list' },
  { id: 'new-entry', label: 'New Entry', icon: 'pi pi-plus' },
  { id: 'tasks', label: 'Tasks Board', icon: 'pi pi-columns' },
  { id: 'analysis', label: 'Analysis', icon: 'pi pi-chart-bar' },
  { id: 'chat', label: 'Chat', icon: 'pi pi-comments' },
  { id: 'compaction', label: 'Compaction', icon: 'pi pi-heart' },
  { id: 'settings', label: 'Settings', icon: 'pi pi-cog' }
]
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h1>Personal Log</h1>
    </div>
    <nav class="sidebar-nav">
      <div
        v-for="item in navItems"
        :key="item.id"
        class="nav-item"
        :class="{ active: currentView === item.id }"
        @click="emit('navigate', item.id)"
      >
        <i :class="item.icon"></i>
        <span>{{ item.label }}</span>
        <span v-if="item.id === 'inbox' && inboxCount > 0" class="nav-badge">{{ inboxCount }}</span>
      </div>
    </nav>
  </aside>
</template>
