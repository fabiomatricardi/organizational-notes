<script setup>
import { ref } from 'vue'
import Sidebar from './components/Sidebar.vue'
import Dashboard from './components/Dashboard.vue'
import LogTimeline from './components/LogTimeline.vue'
import NewEntry from './components/NewEntry.vue'
import TasksBoard from './components/TasksBoard.vue'
import Analysis from './components/Analysis.vue'
import Chat from './components/Chat.vue'
import Settings from './components/Settings.vue'
import Compaction from './components/Compaction.vue'
import Today from './components/Today.vue'
import FollowUp from './components/FollowUp.vue'
import Inbox from './components/Inbox.vue'

const currentView = ref('dashboard')
</script>

<template>
  <div class="app-layout">
    <Sidebar :currentView="currentView" @navigate="currentView = $event" />
    <main class="main-content">
      <Dashboard v-if="currentView === 'dashboard'" @navigate="currentView = $event" />
      <Today v-else-if="currentView === 'today'" />
      <Inbox v-else-if="currentView === 'inbox'" />
      <FollowUp v-else-if="currentView === 'follow-up'" />
      <LogTimeline v-else-if="currentView === 'timeline'" />
      <NewEntry v-else-if="currentView === 'new-entry'" />
      <TasksBoard v-else-if="currentView === 'tasks'" />
      <Analysis v-else-if="currentView === 'analysis'" />
      <Chat v-else-if="currentView === 'chat'" />
      <Settings v-else-if="currentView === 'settings'" />
      <Compaction v-else-if="currentView === 'compaction'" />
    </main>
  </div>
</template>
