<script setup>
import { ref, onMounted } from 'vue'
import { fetchInbox, convertInboxItem, discardInboxItem } from '../composables/useApi.js'

const items = ref([])
const loading = ref(true)
const error = ref(null)
const notice = ref('')
const selected = ref(null)
const saving = ref(false)

const emptyForm = () => ({
  activity: '',
  type: 'LOG',
  status: 'LOG',
  owner: '',
  next_check: '',
  area: '',
  follow_up: ''
})

const form = ref(emptyForm())

const load = async () => {
  loading.value = true
  try {
    const result = await fetchInbox({ processed: 0 })
    items.value = result.items
    if (!selected.value || !items.value.some((i) => i.id === selected.value.id)) {
      select(items.value[0] || null)
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)

const firstLine = (text) => String(text || '').split('\n')[0].slice(0, 160)

const formatAge = (ts) => {
  if (!ts) return ''
  const diff = Date.now() - new Date(ts).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins}m`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h`
  return `${Math.floor(hours / 24)}d`
}

const photoUrl = (item) => `/api/inbox/${item.id}/photo`

const suggest = (item) => {
  const base = emptyForm()
  const text = (item && item.body ? item.body : '').trim()
  base.activity = text
  if (!text) return base

  const mark = text[0]
  const rest = text.slice(1).trim()

  const splitOwner = (value) => {
    const match = value.match(/^([^:]{1,40}):\s+([\s\S]+)$/)
    return match ? { owner: match[1].trim(), activity: match[2].trim() } : null
  }

  if (mark === '⇒' || mark === '=') {
    base.type = 'TASK'
    base.status = 'ASSIGNED'
    const parsed = splitOwner(rest)
    if (parsed) {
      base.owner = parsed.owner
      base.activity = parsed.activity
    } else {
      base.activity = rest
    }
  } else if (mark === '→') {
    base.type = 'TODO'
    base.status = 'PENDING'
    base.owner = 'me'
    base.activity = rest
  } else if (mark === '?') {
    base.type = 'TODO'
    base.status = 'PENDING'
    base.activity = rest
    base.follow_up = 'waiting: '
  } else if (mark === '•' || mark === '*' || mark === '-') {
    base.activity = rest
  }
  return base
}

const select = (item) => {
  selected.value = item
  form.value = item ? suggest(item) : emptyForm()
}

const convert = async () => {
  if (!selected.value) return
  if (!form.value.activity.trim()) {
    error.value = 'Add a line before converting'
    return
  }
  saving.value = true
  error.value = null
  try {
    await convertInboxItem(selected.value.id, { ...form.value, delete_after: true })
    notice.value = 'Converted'
    selected.value = null
    await load()
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

const discard = async () => {
  if (!selected.value) return
  if (!confirm('Discard this item without logging it?')) return
  try {
    await discardInboxItem(selected.value.id)
    notice.value = 'Discarded'
    selected.value = null
    await load()
  } catch (e) {
    error.value = e.message
  }
}
</script>

<template>
  <div class="view-container">
    <div class="view-header">
      <h2>Inbox <span class="muted" style="font-size: 0.9rem">{{ items.length }} to triage</span></h2>
      <button class="btn-secondary" @click="load">Refresh</button>
    </div>

    <div v-if="notice" class="success-banner">{{ notice }}</div>
    <div v-if="error" class="error-banner">{{ error }}</div>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="items.length === 0" class="empty-state">
      <i class="pi pi-inbox"></i>
      <p>Inbox empty. Send a line to the Telegram bot and it lands here.</p>
    </div>

    <div v-else class="split">
      <div class="card inbox-list">
        <div
          v-for="item in items"
          :key="item.id"
          class="inbox-item"
          :class="{ active: selected && selected.id === item.id }"
          @click="select(item)"
        >
          <div class="inbox-meta">
            <span>{{ formatAge(item.received_at) }}</span>
            <span v-if="item.kind === 'photo'">photo</span>
            <span v-if="item.source === 'telegram'">tg</span>
          </div>
          <div class="inbox-body">{{ firstLine(item.body) || '(photo, no caption)' }}</div>
        </div>
      </div>

      <div v-if="selected" class="card inbox-editor">
        <img v-if="selected.kind === 'photo'" :src="photoUrl(selected)" class="photo" alt="capture" />

        <div class="form-group">
          <label class="form-label">Line *</label>
          <textarea v-model="form.activity" class="form-textarea" rows="4"></textarea>
        </div>

        <div class="toolbar" style="flex-wrap: wrap">
          <select v-model="form.type" class="form-select" style="width: 110px">
            <option value="LOG">LOG</option>
            <option value="TODO">TODO (mine)</option>
            <option value="TASK">TASK (theirs)</option>
          </select>
          <select v-model="form.area" class="form-select" style="width: 110px">
            <option value="">Area</option>
            <option>AIR</option>
            <option>FIR</option>
            <option>QIR</option>
            <option>ICSS</option>
            <option>PTW</option>
            <option>LQ</option>
          </select>
          <input v-model="form.owner" class="form-input" style="width: 130px" placeholder="Owner" />
          <input v-model="form.next_check" type="date" class="form-input" style="width: 150px" />
        </div>

        <div class="form-group" style="margin-top: 12px">
          <label class="form-label">Follow up / note</label>
          <input v-model="form.follow_up" class="form-input" placeholder="waiting: SHI / context" />
        </div>

        <div class="modal-actions" style="margin-top: 8px">
          <button class="btn-secondary" @click="discard" :disabled="saving">Discard</button>
          <button class="btn-primary" @click="convert" :disabled="saving">
            {{ saving ? 'Converting...' : 'Convert' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
