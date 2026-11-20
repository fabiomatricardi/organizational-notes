<script setup>
import { ref, onMounted } from 'vue'
import { createEntry, fetchEntries } from '../composables/useApi.js'

const emit = defineEmits(['navigate'])

const emptyForm = () => ({
  activity: '',
  type: 'LOG',
  follow_up: '',
  status: '',
  reference_id: null,
  eta: '',
  owner: '',
  next_check: '',
  area: ''
})

const form = ref(emptyForm())

const entries = ref([])
const success = ref(false)
const error = ref(null)
const loading = ref(false)

onMounted(async () => {
  const result = await fetchEntries({ limit: 50 })
  entries.value = result.entries
})

const handleLoadFile = (event) => {
  const file = event.target.files[0]
  if (!file) return

  if (form.value.activity.trim()) {
    if (!confirm('This will replace the current activity content. Continue?')) {
      event.target.value = ''
      return
    }
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    form.value.activity = e.target.result
  }
  reader.readAsText(file)
  event.target.value = ''
}

const handleSubmit = async () => {
  if (!form.value.activity.trim()) {
    error.value = 'Activity is required'
    return
  }

  loading.value = true
  error.value = null
  success.value = false

  try {
    const data = { ...form.value }
    if (!data.status) {
      data.status = data.type === 'LOG' ? 'LOG' : 'PENDING'
    }
    if (!data.reference_id) delete data.reference_id
    if (!data.eta) delete data.eta
    if (!data.follow_up) delete data.follow_up
    if (!data.owner) delete data.owner
    if (!data.next_check) delete data.next_check
    if (!data.area) delete data.area

    await createEntry(data)
    success.value = true
    form.value = emptyForm()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="view-container">
    <div class="view-header">
      <h2>New Entry</h2>
    </div>

    <div v-if="success" class="success-banner">Entry created successfully!</div>
    <div v-if="error" class="error-banner">{{ error }}</div>

    <div class="card">
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label class="form-label">Type</label>
          <select v-model="form.type" class="form-select">
            <option value="LOG">LOG</option>
            <option value="TODO">TODO</option>
            <option value="TASK">TASK</option>
          </select>
        </div>

        <div class="form-group">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px">
            <label class="form-label" style="margin-bottom: 0">Activity *</label>
            <label class="btn-secondary" style="cursor: pointer; font-size: 0.75rem; padding: 4px 10px; margin: 0">
              <i class="pi pi-file-import" style="margin-right: 4px"></i> Load from file
              <input type="file" accept=".txt,.md" @change="handleLoadFile" style="display: none" />
            </label>
          </div>
          <textarea
            v-model="form.activity"
            class="form-textarea"
            rows="5"
            placeholder="Describe the activity or load content from a .txt/.md file..."
            required
          ></textarea>
        </div>

        <div class="form-group">
          <label class="form-label">Follow Up</label>
          <input
            v-model="form.follow_up"
            class="form-input"
            placeholder="Who/what to follow up on"
          />
        </div>

        <div class="form-group" v-if="form.type !== 'LOG'">
          <label class="form-label">Status</label>
          <select v-model="form.status" class="form-select">
            <option value="">Auto</option>
            <option value="PENDING">Pending</option>
            <option value="ASSIGNED">Assigned</option>
            <option value="ONGOING">Ongoing</option>
            <option value="COMPLETED">Completed</option>
          </select>
        </div>

        <div class="form-group" v-if="form.type !== 'LOG'">
          <label class="form-label">ETA</label>
          <input
            v-model="form.eta"
            class="form-input"
            type="datetime-local"
          />
        </div>

        <div style="display: flex; gap: 12px">
          <div class="form-group" style="flex: 1">
            <label class="form-label">Owner</label>
            <input v-model="form.owner" class="form-input" placeholder="who owes the action (never your own name)" />
          </div>
          <div class="form-group" style="flex: 1">
            <label class="form-label">Next check</label>
            <input type="date" v-model="form.next_check" class="form-input" />
          </div>
          <div class="form-group" style="flex: 1">
            <label class="form-label">Area</label>
            <select v-model="form.area" class="form-select">
              <option value="">-</option>
              <option>AIR</option>
              <option>FIR</option>
              <option>QIR</option>
              <option>ICSS</option>
              <option>PTW</option>
              <option>LQ</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Reference Entry</label>
          <select v-model="form.reference_id" class="form-select">
            <option :value="null">None</option>
            <option v-for="entry in entries" :key="entry.id" :value="entry.id">
              #{{ entry.id }} - {{ entry.activity.substring(0, 50) }}...
            </option>
          </select>
        </div>

        <div style="display: flex; gap: 12px; justify-content: flex-end">
          <button type="button" class="btn-secondary" @click="form = emptyForm()">
            Reset
          </button>
          <button type="submit" class="btn-primary" :disabled="loading">
            {{ loading ? 'Creating...' : 'Create Entry' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
