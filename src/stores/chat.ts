import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'
import { useUserStore } from './user'

export interface Message {
  id: number
  content: string
  type: string
  sender_id: number
  sender_username: string
  is_read: boolean
  is_own: boolean
  created_at: string
}

export interface Conversation {
  id: number
  type: string
  title: string
  last_message: string
  last_time: string
  unread_count: number
  other_users: Array<{ id: number; username: string }>
  exam_title?: string
  exam_id?: number
}

interface ConversationEventPayload {
  id: number
  last_message: string
  last_time: string
}

const LIST_POLL_INTERVAL_MS = 30000
const MAX_RECONNECT_DELAY_MS = 10000

function buildWebSocketUrl(conversationId: number) {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.host}/ws/chat/${conversationId}/`
}

export const useChatStore = defineStore('chat', () => {
  const conversations = ref<Conversation[]>([])
  const currentConversationId = ref<number | null>(null)
  const messages = ref<Message[]>([])
  const loading = ref(false)
  const sending = ref(false)
  const wsConnected = ref(false)

  let socket: WebSocket | null = null
  let listPollTimer: ReturnType<typeof setInterval> | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let reconnectAttempts = 0
  let activeSocketConversationId: number | null = null

  const currentConversation = computed(() => {
    return conversations.value.find(c => c.id === currentConversationId.value) || null
  })

  function upsertConversation(conversation: Conversation) {
    const index = conversations.value.findIndex(c => c.id === conversation.id)
    if (index >= 0) {
      conversations.value[index] = { ...conversations.value[index], ...conversation }
    } else {
      conversations.value.unshift(conversation)
    }
  }

  function applyConversationEvent(conversationId: number, payload?: ConversationEventPayload | null) {
    if (!payload) {
      return
    }
    const conv = conversations.value.find(c => c.id === conversationId)
    if (conv) {
      conv.last_message = payload.last_message
      conv.last_time = payload.last_time
      if (currentConversationId.value !== conversationId) {
        conv.unread_count += 1
      }
    }
  }

  function appendMessage(raw: Omit<Message, 'is_own'> & { is_own?: boolean }) {
    if (messages.value.some(message => message.id === raw.id)) {
      return false
    }

    const userStore = useUserStore()
    messages.value.push({
      ...raw,
      is_own: raw.is_own ?? raw.sender_id === userStore.user?.id,
    })
    return true
  }

  async function loadConversations() {
    loading.value = true
    try {
      const response = await api.get('chat/conversations/')
      if (response.data.success) {
        conversations.value = response.data.conversations
      }
    } catch (error) {
      console.error('加载会话列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  async function loadConversation(conversationId: number, silent = false) {
    if (!silent) {
      loading.value = true
    }
    try {
      const response = await api.get(`chat/conversations/${conversationId}/`)
      if (response.data.success) {
        messages.value = response.data.messages
        currentConversationId.value = conversationId

        const conv = conversations.value.find(c => c.id === conversationId)
        if (conv) {
          conv.unread_count = 0
          if (response.data.messages.length > 0) {
            const last = response.data.messages[response.data.messages.length - 1]
            conv.last_message = last.content.length > 50 ? `${last.content.slice(0, 50)}...` : last.content
            conv.last_time = last.created_at.slice(0, 16).replace('T', ' ')
          }
        } else if (response.data.conversation) {
          upsertConversation({
            id: response.data.conversation.id,
            type: response.data.conversation.type,
            title: response.data.conversation.title,
            last_message: '',
            last_time: '',
            unread_count: 0,
            other_users: [],
            exam_title: response.data.conversation.exam_title,
            exam_id: response.data.conversation.exam_id,
          })
        }
      }
    } catch (error) {
      console.error('加载会话详情失败:', error)
    } finally {
      if (!silent) {
        loading.value = false
      }
    }
  }

  function scheduleReconnect(conversationId: number) {
    if (activeSocketConversationId !== conversationId) {
      return
    }
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
    }
    const delay = Math.min(1000 * (2 ** reconnectAttempts), MAX_RECONNECT_DELAY_MS)
    reconnectAttempts += 1
    reconnectTimer = setTimeout(() => {
      connectWebSocket(conversationId)
    }, delay)
  }

  function disconnectWebSocket() {
    activeSocketConversationId = null
    wsConnected.value = false
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    reconnectAttempts = 0
    if (socket) {
      socket.onopen = null
      socket.onmessage = null
      socket.onclose = null
      socket.onerror = null
      socket.close()
      socket = null
    }
  }

  function connectWebSocket(conversationId: number) {
    if (activeSocketConversationId === conversationId && socket && socket.readyState === WebSocket.OPEN) {
      return
    }

    disconnectWebSocket()
    activeSocketConversationId = conversationId

    socket = new WebSocket(buildWebSocketUrl(conversationId))

    socket.onopen = () => {
      wsConnected.value = true
      reconnectAttempts = 0
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'new_message' && data.message) {
          if (currentConversationId.value === conversationId) {
            appendMessage(data.message)
          }
          applyConversationEvent(conversationId, data.conversation)
        }
      } catch (error) {
        console.error('解析 WebSocket 消息失败:', error)
      }
    }

    socket.onclose = async () => {
      wsConnected.value = false
      if (activeSocketConversationId === conversationId) {
        scheduleReconnect(conversationId)
        if (currentConversationId.value === conversationId) {
          await loadConversation(conversationId, true)
        }
      }
    }

    socket.onerror = () => {
      wsConnected.value = false
    }
  }

  async function sendMessage(content: string) {
    if (!currentConversationId.value || !content.trim()) {
      return false
    }

    sending.value = true
    try {
      const response = await api.post(`chat/conversations/${currentConversationId.value}/send/`, {
        content: content.trim(),
        type: 'text'
      })
      if (response.data.success) {
        appendMessage(response.data.message)
        const conv = conversations.value.find(c => c.id === currentConversationId.value)
        if (conv) {
          conv.last_message = content.length > 50 ? `${content.slice(0, 50)}...` : content
          conv.last_time = new Date().toLocaleString('zh-CN', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
          }).replace(/\//g, '-')
        }
        return true
      }
    } catch (error) {
      console.error('发送消息失败:', error)
    } finally {
      sending.value = false
    }
    return false
  }

  async function createConversation(data: {
    type: string
    title?: string
    exam_id?: number
    participants?: number[]
    target_username?: string
  }) {
    try {
      const response = await api.post('chat/conversations/create/', data)
      if (response.data.success) {
        if (response.data.conversation) {
          upsertConversation(response.data.conversation)
        } else {
          await loadConversations()
        }
        return response.data.conversation_id as number
      }
    } catch (error: unknown) {
      const err = error as { response?: { data?: { error?: string } } }
      console.error('创建会话失败:', err.response?.data?.error || error)
      throw new Error(err.response?.data?.error || '创建会话失败')
    }
    return null
  }

  async function joinExamConversation(examId: number) {
    try {
      const response = await api.post(`chat/exams/${examId}/conversation/`)
      if (response.data.success) {
        if (response.data.conversation) {
          upsertConversation(response.data.conversation)
        } else {
          await loadConversations()
        }
        const conversationId = response.data.conversation_id as number
        await selectConversation(conversationId)
        return conversationId
      }
    } catch (error: unknown) {
      const err = error as { response?: { data?: { error?: string } } }
      console.error('进入考试聊天室失败:', err.response?.data?.error || error)
      throw new Error(err.response?.data?.error || '进入考试聊天室失败')
    }
    return null
  }

  async function selectConversation(conversationId: number) {
    if (currentConversationId.value !== conversationId) {
      disconnectWebSocket()
    }
    currentConversationId.value = conversationId
    await loadConversation(conversationId)
    connectWebSocket(conversationId)
  }

  function startListPolling() {
    stopListPolling()
    listPollTimer = setInterval(() => {
      loadConversations()
    }, LIST_POLL_INTERVAL_MS)
  }

  function stopListPolling() {
    if (listPollTimer) {
      clearInterval(listPollTimer)
      listPollTimer = null
    }
  }

  function stopRealtime() {
    stopListPolling()
    disconnectWebSocket()
  }

  return {
    conversations,
    currentConversationId,
    messages,
    loading,
    sending,
    wsConnected,
    currentConversation,
    loadConversations,
    loadConversation,
    sendMessage,
    createConversation,
    joinExamConversation,
    selectConversation,
    connectWebSocket,
    disconnectWebSocket,
    startListPolling,
    stopListPolling,
    stopRealtime,
  }
})
