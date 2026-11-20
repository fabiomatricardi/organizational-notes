<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchFollowUps, updateEntry, fetchHandover } from '../composables/useApi.js'

const data = ref({ items: [], groups: {}, counts: {} })
const loading = ref(true)
const error = ref(null)
const notice = ref('')
const search = ref('')
const ownerFilter = ref('')
const flag = ref('all')

const load = async () => {
  loading.value = true
  try {
    data.value = await fetchFollowUps()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)

const owners = computed(() => Object.keys(data.value.groups || {}))

const chips = computed(() => {
  const c = data.value.counts || {}
  return [
    { key: 'all', label: 'open', count: c.open || 0 },
    { key: 'overdue', label: 'overdue', count: c.overdue || 0 },
    { key: 'stale', label: 'stale', count: c.stale || 0 },
    { key: 'orphan', label: 'no owner', count: c.orphan || 0 },
    { key: 'waiting', label: 'waiting', count: c.waiting || 0 }
  ]
})

const filteredGroups = computed(() => {
  const out = {}
  const term = search.value.trim().toLowerCase()
  for (const [owner, items] of Object.entries(data.value.groups || {})) {
    if (ownerFilter.value && owner !== ownerFilter.value) continue
    const keep = items.filter((item) => {
      if (flag.value === 'overdue' && !item.overdue) return false
      if (flag.value === 'stale' && !item.stale) return false
      if (flag.value === 'orphan' && !item.orphan) return false
      if (flag.value === 'waiting' && !item.waiting) return false
      if (term) {
        const hay = `${item.activity} ${item.follow_up || ''} ${item.area || ''}`.toLowerCase()
        if (!hay.includes(term)) return false
      }
      return true
    })
    if (keep.length) out[owner] = keep
  }
  return out
})

const visibleCount = computed(() =>
  Object.values(filteredGroups.value).reduce((n, items) => n + items.length, 0)
)

const firstLine = (text) => String(text || '').split('\n')[0].slice(0, 220)

const isoInDays = (days) => {
  const d = new Date()
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}

const copy = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (e) {
    error.value = 'Clipboard unavailable: ' + e.message
    return false
  }
}

const nudgeText = (item) =>
  `#${item.id} — ${firstLine(item.activity)} — due ${item.due || 'TBC'} — status?`

const closeItem = async (item) => {
  await updateEntry(item.id, { status: 'COMPLETED' })
  notice.value = `#${item.id} closed`
  await load()
}

const snooze = async (item, days) => {
  const next = isoInDays(days)
  await updateEntry(item.id, { next_check: next })
  notice.value = `#${item.id} -> next check ${next}`
  await load()
}

const nudge = async (item) => {
  if (await copy(nudgeText(item))) notice.value = 'Nudge copied — paste it now, do not wait'
}

const copyOwner = async (owner, items) => {
  if (await copy(items.map(nudgeText).join('\n'))) {
    notice.value = `Copied ${items.length} nudge(s) for ${owner}`
  }
}

const copyHandover = async () => {
  try {
    const markdown = await fetchHandover()
    if (await copy(markdown)) notice.value = 'Handover copied to clipboard'
  } catch (e) {
    error.value = e.message
  }
}
</script>

<template>
  <div class="view-container">
    <div class="view-header">
      <h2>Follow-up</h2>
      <div style="display: flex; gap: 8px">
        <button class="btn-secondary" @click="copyHandover">Copy handover</button>
        <button class="btn-secondary" @click="load">Refresh</button>
      </div>
    </div>

    <div v-if="notice" class="success-banner">{{ notice }}</div>
    <div v-if="error" class="error-banner">{{ error }}</div>

    <div class="count-row">
      <button
        v-for="chip in chips"
        :key="chip.key"
        class="count-chip"
        :class="{ active: flag === chip.key }"
        @click="flag = chip.key"
      >
        <b>{{ chip.count }}</b><span>{{ chip.label }}</span>
      </button>
    </div>

    <div class="card toolbar">
      <input v-model="search" class="form-input" placeholder="Search open items, owners, areas..." style="flex: 1" />
      <select v-model="ownerFilter" class="form-select" style="width: 200px">
        <option value="">All owners</option>
        <option v-for="owner in owners" :key="owner" :value="owner">{{ owner }}</option>
      </select>
      <span class="muted">{{ visibleCount }} shown</span>
    </div>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="visibleCount === 0" class="empty-state">
      <i class="pi pi-check-circle"></i>
      <p>Nothing open in this filter.</p>
    </div>
    <template v-else>
      <div v-for="(items, owner) in filteredGroups" :key="owner" class="card owner-group">
        <div class="owner-head">
          <h3>{{ owner }} <span class="muted">({{ items.length }})</span></h3>
          <button class="btn-secondary mini" @click="copyOwner(owner, items)">
            Copy {{ items.length }} nudge(s)
          </button>
        </div>

        <div v-for="item in items" :key="item.id" class="row-item">
          <span class="fu-id">#{{ item.id }}</span>
          <div class="row-main">
            <div class="row-title">{{ firstLine(item.activity) }}</div>
            <div class="row-meta">
              <span v-if="item.area" class="chip">{{ item.area }}</span>
              <span>due {{ item.due || 'TBC' }}</span>
              <span>{{ item.age_days }}d old</span>
              <span v-if="item.waiting" class="badge badge-muted">waiting</span>
              <span v-if="item.overdue" class="badge badge-danger">overdue</span>
              <span v-else-if="item.stale" class="badge badge-warning">stale</span>
              <span v-if="item.orphan" class="badge badge-warning">no owner</span>
            </div>
            <div v-if="item.follow_up" class="muted small">{{ item.follow_up }}</div>
          </div>
          <div class="row-actions">
            <button class="btn-secondary mini" @click="snooze(item, 3)">+3d</button>
            <button class="btn-secondary mini" @click="nudge(item)">Nudge</button>
            <button class="btn-primary mini" @click="closeItem(item)">Done</button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
