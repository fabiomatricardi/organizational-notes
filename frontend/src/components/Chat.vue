<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { marked } from 'marked'
import { searchChat, searchChatByDate, sendChatMessage, fetchConversations, fetchConversation, deleteConversation } from '../composables/useApi.js'

const conversations = ref([])
const currentConversationId = ref(null)
const messages = ref([])
const userInput = ref('')
const sending = ref(false)

const ragEnabled = ref(false)
const ragQuery = ref('')
const ragResults = ref([])
const selectedEntryIds = ref(new Set())
const searching = ref(false)
const topK = ref(10)
const searchMode = ref('text')
const dateFrom = ref('')
const dateTo = ref('')

const sidebarOpen = ref(true)
const messagesContainer = ref(null)

marked.setOptions({ breaks: true, gfm: true })

onMounted(async () => {
  await loadConversations()
})

const loadConversations = async () => {
  try {
    const result = await fetchConversations()
    conversations.value = result.conversations
  } catch (e) {
    console.error('Failed to load conversations:', e)
  }
}

const newChat = () => {
  currentConversationId.value = null
  messages.value = []
  ragResults.value = []
  selectedEntryIds.value = new Set()
  ragQuery.value = ''
}

const openConversation = async (id) => {
  try {
    const conv = await fetchConversation(id)
    currentConversationId.value = conv.id
    messages.value = conv.history || []
    ragEnabled.value = conv.rag_used
    selectedEntryIds.value = new Set(conv.entry_ids || [])
    await scrollToBottom()
  } catch (e) {
    console.error('Failed to load conversation:', e)
  }
}

const handleSearch = async () => {
  if (searchMode.value === 'text' && !ragQuery.value.trim()) return
  if (searchMode.value === 'date' && (!dateFrom.value || !dateTo.value)) return

  searching.value = true
  try {
    let result
    if (searchMode.value === 'date') {
      result = await searchChatByDate(dateFrom.value, dateTo.value)
    } else {
      result = await searchChat(ragQuery.value, topK.value)
    }
    ragResults.value = result.results
    selectedEntryIds.value = new Set(result.results.map(r => r.id))
  } catch (e) {
    console.error('Search failed:', e)
  } finally {
    searching.value = false
  }
}

const toggleEntry = (id) => {
  if (selectedEntryIds.value.has(id)) {
    selectedEntryIds.value.delete(id)
  } else {
    selectedEntryIds.value.add(id)
  }
}

const selectAll = () => {
  selectedEntryIds.value = new Set(ragResults.value.map(r => r.id))
}

const clearSelection = () => {
  selectedEntryIds.value = new Set()
}

const sendMessage = async () => {
  if (!userInput.value.trim() || sending.value) return

  const userMsg = userInput.value.trim()
  userInput.value = ''

  messages.value.push({ role: 'user', content: userMsg })
  await scrollToBottom()

  sending.value = true
  try {
    const ragIds = ragEnabled.value && selectedEntryIds.value.size > 0
      ? Array.from(selectedEntryIds.value)
      : null

    const result = await sendChatMessage(currentConversationId.value, userMsg, ragIds)
    currentConversationId.value = result.conversation_id

    messages.value.push({ role: 'assistant', content: result.assistant_message })
    await loadConversations()
    await scrollToBottom()
  } catch (e) {
    messages.value.push({ role: 'assistant', content: '**Error:** ' + e.message })
    await scrollToBottom()
  } finally {
    sending.value = false
  }
}

const handleDeleteConversation = async (id) => {
  if (!confirm('Delete this conversation?')) return
  try {
    await deleteConversation(id)
    if (currentConversationId.value === id) {
      newChat()
    }
    await loadConversations()
  } catch (e) {
    console.error('Failed to delete conversation:', e)
  }
}

const handleKeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const renderMarkdown = (text) => {
  return marked.parse(text || '')
}

const formatTime = (dateStr) => {
  if (!dateStr) return ''
  return dateStr
}
</script>

<template>
  <div class="chat-layout">
    <!-- Sidebar: conversation list -->
    <div class="chat-sidebar" :class="{ collapsed: !sidebarOpen }">
      <div class="chat-sidebar-header">
        <h3 v-if="sidebarOpen">Conversations</h3>
        <button class="btn-icon" @click="sidebarOpen = !sidebarOpen" :title="sidebarOpen ? 'Collapse' : 'Expand'">
          <i :class="sidebarOpen ? 'pi pi-chevron-left' : 'pi pi-chevron-right'"></i>
        </button>
      </div>
      <div v-if="sidebarOpen" class="chat-sidebar-content">
        <button class="btn-primary" style="width: 100%; margin-bottom: 12px" @click="newChat">
          <i class="pi pi-plus" style="margin-right: 6px"></i> New Chat
        </button>
        <div v-if="conversations.length === 0" style="color: var(--text-secondary); font-size: 0.875rem; text-align: center; padding: 20px 0">
          No conversations yet
        </div>
        <div v-for="conv in conversations" :key="conv.id"
             class="conv-item"
             :class="{ active: currentConversationId === conv.id }"
             @click="openConversation(conv.id)">
          <div class="conv-item-title">{{ conv.title }}</div>
          <div class="conv-item-meta">
            <span v-if="conv.rag_used" class="conv-rag-badge">RAG</span>
            <span>{{ conv.message_count }} msgs</span>
          </div>
          <button class="conv-delete" @click.stop="handleDeleteConversation(conv.id)" title="Delete">
            <i class="pi pi-trash"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Main chat area -->
    <div class="chat-main">
      <!-- RAG bar -->
      <div class="rag-bar">
        <label class="rag-toggle">
          <input type="checkbox" v-model="ragEnabled" />
          <span>RAG</span>
        </label>
        <div v-if="ragEnabled" class="rag-controls">
          <div class="search-mode-toggle">
            <button :class="{ active: searchMode === 'text' }" @click="searchMode = 'text'" title="Text search">
              <i class="pi pi-search"></i> Text
            </button>
            <button :class="{ active: searchMode === 'date' }" @click="searchMode = 'date'" title="Date range search">
              <i class="pi pi-calendar"></i> Date
            </button>
          </div>
          <template v-if="searchMode === 'text'">
            <input v-model="ragQuery" class="form-input" placeholder="Search entries..." style="flex: 1"
                   @keydown.enter.prevent="handleSearch" />
            <select v-model.number="topK" class="form-select" style="width: 80px">
              <option :value="5">5</option>
              <option :value="10">10</option>
              <option :value="15">15</option>
              <option :value="20">20</option>
              <option :value="30">30</option>
              <option :value="40">40</option>
            </select>
          </template>
          <template v-if="searchMode === 'date'">
            <input type="date" v-model="dateFrom" class="form-input" style="width: 150px" />
            <span style="color: var(--text-secondary); font-size: 0.8125rem">to</span>
            <input type="date" v-model="dateTo" class="form-input" style="width: 150px" />
          </template>
          <button class="btn-secondary" @click="handleSearch" :disabled="searching">
            {{ searching ? 'Searching...' : 'Search' }}
          </button>
        </div>
      </div>

      <!-- RAG results panel -->
      <div v-if="ragEnabled && ragResults.length > 0" class="rag-results">
        <div class="rag-results-header">
          <span>{{ selectedEntryIds.size }} / {{ ragResults.length }} selected</span>
          <div>
            <button class="btn-icon" @click="selectAll" title="Select all">All</button>
            <button class="btn-icon" @click="clearSelection" title="Clear">None</button>
          </div>
        </div>
        <div class="rag-results-list">
          <label v-for="result in ragResults" :key="result.id" class="rag-result-item">
            <input type="checkbox" :checked="selectedEntryIds.has(result.id)" @change="toggleEntry(result.id)" />
            <div class="rag-result-info">
              <span class="entry-type" :class="result.type.toLowerCase()">{{ result.type }}</span>
              <span class="rag-result-id">#{{ result.id }}</span>
              <span class="rag-result-score">score: {{ result.score }}</span>
            </div>
            <div class="rag-result-text">{{ result.activity }}</div>
          </label>
        </div>
      </div>

      <!-- Messages area -->
      <div class="chat-messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="chat-empty">
          <i class="pi pi-comments" style="font-size: 3rem; opacity: 0.3"></i>
          <p style="color: var(--text-secondary); margin-top: 12px">Start a conversation</p>
          <p style="color: var(--text-secondary); font-size: 0.8125rem; margin-top: 4px">
            Toggle RAG to search your log entries for context
          </p>
        </div>
        <div v-for="(msg, idx) in messages" :key="idx" class="chat-message" :class="msg.role">
          <div class="chat-message-role">{{ msg.role === 'user' ? 'You' : 'Assistant' }}</div>
          <div class="chat-message-content" v-html="renderMarkdown(msg.content)"></div>
        </div>
        <div v-if="sending" class="chat-message assistant">
          <div class="chat-message-role">Assistant</div>
          <div class="chat-message-content typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <!-- Input bar -->
      <div class="chat-input-bar">
        <textarea
          v-model="userInput"
          class="form-input chat-input"
          placeholder="Type a message... (Enter to send, Shift+Enter for newline)"
          rows="1"
          @keydown="handleKeydown"
          :disabled="sending"
        ></textarea>
        <button class="btn-primary" @click="sendMessage" :disabled="sending || !userInput.trim()">
          <i class="pi pi-send"></i>
        </button>
      </div>
    </div>
  </div>
</template>
