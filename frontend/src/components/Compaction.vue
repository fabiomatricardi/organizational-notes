<script setup>
import { ref, onMounted } from 'vue'
import { marked } from 'marked'
import { fetchCompactionStats, detectDuplicates, mergeCompactionEntries } from '../composables/useApi.js'

const stats = ref(null)
const duplicateGroups = ref([])
const detecting = ref(false)
const merging = ref(false)
const dateFrom = ref('')
const dateTo = ref('')
const entryType = ref('')
const batchInfo = ref('')
const mergeResult = ref(null)
const showMergeConfirm = ref(false)
const selectedGroup = ref(null)

marked.setOptions({ breaks: true, gfm: true })

onMounted(async () => {
  await loadStats()
})

const loadStats = async () => {
  try {
    stats.value = await fetchCompactionStats()
  } catch (e) {
    console.error('Failed to load stats:', e)
  }
}

const handleDetect = async () => {
  detecting.value = true
  batchInfo.value = ''
  duplicateGroups.value = []
  mergeResult.value = null
  try {
    const result = await detectDuplicates(dateFrom.value, dateTo.value, entryType.value)
    duplicateGroups.value = result.groups
    batchInfo.value = result.batch_info
  } catch (e) {
    console.error('Detection failed:', e)
    batchInfo.value = 'Error: ' + (e.response?.data?.detail || e.message)
  } finally {
    detecting.value = false
  }
}

const confirmMerge = (group) => {
  selectedGroup.value = group
  showMergeConfirm.value = true
}

const cancelMerge = () => {
  showMergeConfirm.value = false
  selectedGroup.value = null
}

const executeMerge = async () => {
  if (!selectedGroup.value) return
  merging.value = true
  try {
    const group = selectedGroup.value
    const primaryId = group.entry_ids[0]
    const secondaryIds = group.entry_ids.slice(1)
    const result = await mergeCompactionEntries(primaryId, secondaryIds)
    mergeResult.value = result
    showMergeConfirm.value = false
    selectedGroup.value = null
    await loadStats()
    await handleDetect()
  } catch (e) {
    console.error('Merge failed:', e)
    batchInfo.value = 'Merge error: ' + (e.response?.data?.detail || e.message)
  } finally {
    merging.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  return dateStr.slice(0, 10)
}

const getConfidenceClass = (confidence) => {
  if (confidence >= 0.9) return 'high'
  if (confidence >= 0.7) return 'medium'
  return 'low'
}
</script>

<template>
  <div class="view-container">
    <div class="view-header">
      <h2>Database Compaction</h2>
    </div>

    <!-- Stats -->
    <div v-if="stats" class="stat-grid">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_entries }}</div>
        <div class="stat-label">Total Entries</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_logs }}</div>
        <div class="stat-label">Logs</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_todos }}</div>
        <div class="stat-label">TODOs</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_tasks }}</div>
        <div class="stat-label">Tasks</div>
      </div>
    </div>

    <!-- Detection Controls -->
    <div class="card">
      <div class="card-header">
        <h3>Duplicate Detection</h3>
      </div>
      <p style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 16px">
        AI-powered analysis to find entries that are duplicates or cover the same topic.
        Entries are analyzed in batches for optimal results.
      </p>
      <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end">
        <div class="form-group" style="margin-bottom: 0">
          <label class="form-label">Date From</label>
          <input type="date" v-model="dateFrom" class="form-input" style="width: 160px" />
        </div>
        <div class="form-group" style="margin-bottom: 0">
          <label class="form-label">Date To</label>
          <input type="date" v-model="dateTo" class="form-input" style="width: 160px" />
        </div>
        <div class="form-group" style="margin-bottom: 0">
          <label class="form-label">Entry Type</label>
          <select v-model="entryType" class="form-select" style="width: 120px">
            <option value="">All Types</option>
            <option value="LOG">Logs</option>
            <option value="TODO">TODOs</option>
            <option value="TASK">Tasks</option>
          </select>
        </div>
        <button class="btn-primary" @click="handleDetect" :disabled="detecting" style="height: 42px">
          {{ detecting ? 'Detecting...' : 'Detect Duplicates' }}
        </button>
      </div>
    </div>

    <!-- Batch Info -->
    <div v-if="batchInfo" class="card" style="border-left: 3px solid var(--info)">
      <p style="color: var(--text-secondary); font-size: 0.875rem; margin: 0">{{ batchInfo }}</p>
    </div>

    <!-- Merge Result -->
    <div v-if="mergeResult" class="card" style="border-left: 3px solid var(--success)">
      <h4 style="color: var(--success); margin-bottom: 8px">Merge Completed</h4>
      <p style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 8px">
        Merged into entry #{{ mergeResult.merged_entry.id }}.
        Deleted {{ mergeResult.deleted_ids.length }} entries: #{{ mergeResult.deleted_ids.join(', #') }}
      </p>
      <p style="color: var(--text-secondary); font-size: 0.8125rem; margin: 0">
        Backup saved: {{ mergeResult.backup_path }}
      </p>
    </div>

    <!-- Duplicate Groups -->
    <div v-if="duplicateGroups.length > 0" class="card">
      <div class="card-header">
        <h3>Potential Duplicates ({{ duplicateGroups.length }} groups)</h3>
      </div>
      <div class="duplicate-groups-list">
        <div v-for="group in duplicateGroups" :key="group.group_id" class="duplicate-group">
          <div class="duplicate-group-header">
            <span class="group-label">Group {{ group.group_id }}</span>
            <span class="confidence-badge" :class="getConfidenceClass(group.confidence)">
              {{ Math.round(group.confidence * 100) }}% confidence
            </span>
          </div>
          <div class="duplicate-group-reason">{{ group.reason }}</div>
          <div class="duplicate-entries">
            <div v-for="entry in group.entries" :key="entry.id" class="duplicate-entry">
              <div class="duplicate-entry-header">
                <span class="entry-type" :class="entry.type.toLowerCase()">{{ entry.type }}</span>
                <span class="duplicate-entry-id">#{{ entry.id }}</span>
                <span class="duplicate-entry-date">{{ formatDate(entry.timestamp) }}</span>
              </div>
              <div class="duplicate-entry-activity">{{ entry.activity }}</div>
              <div v-if="entry.follow_up" class="duplicate-entry-followup">
                Follow-up: {{ entry.follow_up }}
              </div>
            </div>
          </div>
          <div class="duplicate-group-actions">
            <button class="btn-primary" @click="confirmMerge(group)" :disabled="merging">
              Merge Group
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!detecting && duplicateGroups.length === 0 && batchInfo && !batchInfo.startsWith('Error')" class="empty-state">
      <i class="pi pi-check-circle" style="font-size: 3rem; opacity: 0.3"></i>
      <p style="color: var(--text-secondary); margin-top: 12px">No duplicates found</p>
    </div>

    <!-- Merge Confirmation Dialog -->
    <div v-if="showMergeConfirm" class="modal-overlay" @click.self="cancelMerge">
      <div class="modal">
        <div class="dialog-header">
          <h3>Confirm Merge</h3>
          <button class="btn-icon" @click="cancelMerge">
            <i class="pi pi-times"></i>
          </button>
        </div>
        <div style="margin-bottom: 16px">
          <p style="margin-bottom: 12px">
            You are about to merge <strong>{{ selectedGroup?.entry_ids.length }} entries</strong> into one.
          </p>
          <p style="color: var(--warning); font-size: 0.875rem; margin-bottom: 12px">
            <i class="pi pi-exclamation-triangle" style="margin-right: 4px"></i>
            A database backup will be created before merging. This action cannot be undone.
          </p>
          <p style="color: var(--text-secondary); font-size: 0.875rem">
            Entry #{{ selectedGroup?.entry_ids[0] }} will be kept and updated with merged content.
            Entries #{{ selectedGroup?.entry_ids.slice(1).join(', #') }} will be deleted.
          </p>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="cancelMerge" :disabled="merging">Cancel</button>
          <button class="btn-primary" @click="executeMerge" :disabled="merging">
            {{ merging ? 'Merging...' : 'Merge & Backup' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.duplicate-groups-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.duplicate-group {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
}

.duplicate-group-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.group-label {
  font-weight: 600;
  font-size: 0.9375rem;
}

.confidence-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.confidence-badge.high {
  background: rgba(34, 197, 94, 0.2);
  color: var(--success);
}

.confidence-badge.medium {
  background: rgba(245, 158, 11, 0.2);
  color: var(--warning);
}

.confidence-badge.low {
  background: rgba(148, 163, 184, 0.2);
  color: var(--text-secondary);
}

.duplicate-group-reason {
  color: var(--text-secondary);
  font-size: 0.8125rem;
  margin-bottom: 12px;
  font-style: italic;
}

.duplicate-entries {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.duplicate-entry {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 10px 12px;
}

.duplicate-entry-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.duplicate-entry-id {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.duplicate-entry-date {
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.duplicate-entry-activity {
  font-size: 0.875rem;
  line-height: 1.5;
  white-space: pre-wrap;
}

.duplicate-entry-followup {
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px solid var(--border);
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.duplicate-group-actions {
  display: flex;
  justify-content: flex-end;
}
</style>
