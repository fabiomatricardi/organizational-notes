<script setup>
import { ref, onMounted } from 'vue'
import { fetchToday, createEntry, updateEntry } from '../composables/useApi.js'

const data = ref({ date: '', entries: [], due: [], counts: {} })
const loading = ref(true)
const error = ref(null)
const notice = ref('')
const saving = ref(false)

const form = ref({ type: 'LOG', activity: '', owner: '', next_check: '', area: '' })

const load = async () => {
  loading.value = true
  try {
    data.value = await fetchToday()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)

const submit = async () => {
  if (!form.value.activity.trim()) return
  saving.value = true
  error.value = null
  try {
    const payload = {
      type: form.value.type,
      activity: form.value.activity.trim()
    }
    if (form.value.area) payload.area = form.value.area
    if (form.value.type !== 'LOG') {
      payload.status = form.value.type === 'TASK' ? 'ASSIGNED' : 'PENDING'
      if (form.value.owner) payload.owner = form.value.owner
      if (form.value.next_check) payload.next_check = form.value.next_check
    }
    await createEntry(payload)
    form.value.activity = ''
    notice.value = 'Saved'
    await load()
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

const closeItem = async (item) => {
  await updateEntry(item.id, { status: 'COMPLETED' })
  notice.value = `#${item.id} closed`
  await load()
}

const snooze = async (item) => {
  const d = new Date()
  d.setDate(d.getDate() + 3)
  const next = d.toISOString().slice(0, 10)
  await updateEntry(item.id, { next_check: next })
  notice.value = `#${item.id} -> ${next}`
  await load()
}

const firstLine = (text) => String(text || '').split('\n')[0].slice(0, 180)

const timeOf = (ts) => (ts ? new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '')
</script>

<template>
  <div class="view-container">
    <div class="view-header">
      <h2>Today <span class="muted" style="font-size: 0.9rem">{{ data.date }}</span></h2>
      <button class="btn-secondary" @click="load">Refresh</button>
    </div>

    <div v-if="notice" class="success-banner">{{ notice }}</div>
    <div v-if="error" class="error-banner">{{ error }}</div>

    <div class="count-row">
      <div class="count-chip"><b>{{ data.counts.entries || 0 }}</b><span>entries today</span></div>
      <div class="count-chip"><b>{{ data.counts.due || 0 }}</b><span>due / stale</span></div>
      <div class="count-chip"><b>{{ data.counts.open || 0 }}</b><span>open total</span></div>
    </div>

    <div class="card">
      <h3 style="margin-bottom: 12px">Quick add <span class="muted small">— one line, one thing</span></h3>
      <div class="toolbar" style="flex-wrap: wrap">
        <select v-model="form.type" class="form-select" style="width: 110px">
          <option value="LOG">LOG</option>
          <option value="TODO">TODO (mine)</option>
          <option value="TASK">TASK (theirs)</option>
        </select>
        <input
          v-model="form.activity"
          class="form-input"
          style="flex: 1; min-width: 280px"
          placeholder="• fact / → my action / ⇒ name: their action / ? waiting / ! risk"
          @keydown.enter.exact.prevent="submit"
        />
        <select v-model="form.area" class="form-select" style="width: 110px">
          <option value="">Area</option>
          <option>AIR</option>
          <option>FIR</option>
          <option>QIR</option>
          <option>ICSS</option>
          <option>PTW</option>
          <option>LQ</option>
        </select>
        <input v-if="form.type !== 'LOG'" v-model="form.owner" class="form-input" style="width: 140px" placeholder="Owner" />
        <input v-if="form.type !== 'LOG'" v-model="form.next_check" type="date" class="form-input" style="width: 150px" />
        <button class="btn-primary" :disabled="saving || !form.activity.trim()" @click="submit">
          {{ saving ? 'Saving...' : 'Add' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading...</div>
    <template v-else>
      <div class="card">
        <h3 style="margin-bottom: 12px">Due now <span class="muted small">— send the nudge before you close the laptop</span></h3>
        <div v-if="data.due.length === 0" class="muted small">Nothing due. Good.</div>
        <div v-for="item in data.due" :key="item.id" class="row-item">
          <span class="fu-id">#{{ item.id }}</span>
          <div class="row-main">
            <div class="row-title">{{ firstLine(item.activity) }}</div>
            <div class="row-meta">
              <span v-if="item.area" class="chip">{{ item.area }}</span>
              <span>{{ item.owner || 'no owner' }}</span>
              <span>due {{ item.due || 'TBC' }}</span>
              <span v-if="item.overdue" class="badge badge-danger">overdue</span>
              <span v-else class="badge badge-warning">stale</span>
            </div>
          </div>
          <div class="row-actions">
            <button class="btn-secondary mini" @click="snooze(item)">+3d</button>
            <button class="btn-primary mini" @click="closeItem(item)">Done</button>
          </div>
        </div>
      </div>

      <div class="card">
        <h3 style="margin-bottom: 12px">Written today</h3>
        <div v-if="data.entries.length === 0" class="muted small">Nothing yet.</div>
        <div v-for="entry in data.entries" :key="entry.id" class="row-item">
          <span class="fu-id">{{ timeOf(entry.timestamp) }}</span>
          <div class="row-main">
            <div class="row-title">
              <span class="entry-type" :class="(entry.type || '').toLowerCase()">{{ entry.type }}</span>
              {{ firstLine(entry.activity) }}
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
