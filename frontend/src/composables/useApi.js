import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export async function fetchEntries(params = {}) {
  const { data } = await api.get('/entries', { params })
  return data
}

export async function fetchEntry(id) {
  const { data } = await api.get(`/entries/${id}`)
  return data
}

export async function createEntry(entry) {
  const { data } = await api.post('/entries', entry)
  return data
}

export async function updateEntry(id, entry) {
  const { data } = await api.put(`/entries/${id}`, entry)
  return data
}

export async function deleteEntry(id) {
  const { data } = await api.delete(`/entries/${id}`)
  return data
}

export async function fetchDashboardStats() {
  const { data } = await api.get('/entries/stats/dashboard')
  return data
}

export async function fetchFollowUps() {
  const { data } = await api.get('/entries/follow-up')
  return data
}

export async function fetchToday() {
  const { data } = await api.get('/entries/today')
  return data
}

export async function fetchInbox(params = {}) {
  const { data } = await api.get('/inbox', { params })
  return data
}

export async function fetchInboxCount() {
  const { data } = await api.get('/inbox/count')
  return data
}

export async function convertInboxItem(id, payload) {
  const { data } = await api.post(`/inbox/${id}/convert`, payload)
  return data
}

export async function discardInboxItem(id) {
  const { data } = await api.delete(`/inbox/${id}`)
  return data
}

export async function fetchTelegramStatus() {
  const { data } = await api.get('/inbox/telegram/status')
  return data
}

export async function fetchHandover() {
  const { data } = await api.get('/data/export/handover', { responseType: 'text' })
  return data
}

export async function fetchTags() {
  const { data } = await api.get('/tags')
  return data
}

export async function createTag(tag) {
  const { data } = await api.post('/tags', tag)
  return data
}

export async function deleteTag(id) {
  const { data } = await api.delete(`/tags/${id}`)
  return data
}

export async function generateAnalysis(request) {
  const { data } = await api.post('/analysis/generate', request)
  return data
}

export async function fetchReports(limit = 20) {
  const { data } = await api.get('/analysis/reports', { params: { limit } })
  return data
}

export async function fetchReport(id) {
  const { data } = await api.get(`/analysis/reports/${id}`)
  return data
}

export async function deleteReport(id) {
  const { data } = await api.delete(`/analysis/reports/${id}`)
  return data
}

export async function updateReport(id, reportData) {
  const { data } = await api.put(`/analysis/reports/${id}`, reportData)
  return data
}

export async function deleteAllReports() {
  const { data } = await api.delete('/analysis/reports')
  return data
}

export async function importExcel(file) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/data/import/excel', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export async function exportExcel() {
  const response = await api.get('/data/export/excel', { responseType: 'blob' })
  return response.data
}

export async function backupDatabase() {
  const response = await api.post('/data/backup', {}, { responseType: 'blob' })
  return response.data
}

export async function restoreDatabase(file) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/data/restore', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export async function fetchDatabaseInfo() {
  const { data } = await api.get('/data/info')
  return data
}

export async function fetchSettings() {
  const { data } = await api.get('/settings')
  return data
}

export async function updateSettings(config) {
  const { data } = await api.post('/settings', config)
  return data
}

export async function shutdownApp() {
  await api.post('/shutdown')
}

export async function searchChat(query, top_k = 10) {
  const { data } = await api.post('/chat/search', { query, top_k })
  return data
}

export async function searchChatByDate(dateFrom, dateTo, limit = 50) {
  const { data } = await api.post('/chat/search-by-date', {
    date_from: dateFrom,
    date_to: dateTo,
    limit
  })
  return data
}

export async function sendChatMessage(conversation_id, message, rag_entry_ids = null) {
  const payload = { message }
  if (conversation_id) payload.conversation_id = conversation_id
  if (rag_entry_ids) payload.rag_entry_ids = rag_entry_ids
  const { data } = await api.post('/chat/send', payload)
  return data
}

export async function fetchConversations() {
  const { data } = await api.get('/chat/conversations')
  return data
}

export async function fetchConversation(id) {
  const { data } = await api.get(`/chat/conversations/${id}`)
  return data
}

export async function deleteConversation(id) {
  const { data } = await api.delete(`/chat/conversations/${id}`)
  return data
}

export async function fetchCompactionStats() {
  const { data } = await api.get('/compaction/stats')
  return data
}

export async function detectDuplicates(dateFrom, dateTo, entryType) {
  const { data } = await api.post('/compaction/detect', {
    date_from: dateFrom || null,
    date_to: dateTo || null,
    entry_type: entryType || null
  })
  return data
}

export async function mergeCompactionEntries(primaryId, secondaryIds) {
  const { data } = await api.post('/compaction/merge', {
    primary_id: primaryId,
    secondary_ids: secondaryIds
  })
  return data
}
