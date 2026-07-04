<template>
  <div class="chat-page">
    <div class="navbar">
      <div class="nav-brand">
        <span class="logo-icon">💬</span>
        <span class="brand-text">聊天中心</span>
      </div>
      <div class="nav-actions">
        <span v-if="userStore.isLoggedIn" class="welcome-text">欢迎，{{ userStore.user?.username }}</span>
        <router-link to="/" class="back-btn">返回首页</router-link>
      </div>
    </div>

    <div class="chat-container">
      <div class="sidebar">
        <div class="sidebar-header">
          <h3>会话列表</h3>
          <button class="new-chat-btn" @click="showCreateModal = true" title="新建会话">+</button>
        </div>
        <div class="conversation-list">
          <div
            v-for="conv in chatStore.conversations"
            :key="conv.id"
            :class="['conversation-item', { active: chatStore.currentConversationId === conv.id }]"
            @click="chatStore.selectConversation(conv.id)"
          >
            <div class="conv-info">
              <div class="conv-title">
                {{ conv.title || conv.exam_title || '会话' }}
                <span v-if="conv.unread_count > 0" class="unread-badge">{{ conv.unread_count }}</span>
              </div>
              <div class="conv-preview">{{ conv.last_message }}</div>
            </div>
            <div class="conv-meta">
              <span class="conv-time">{{ conv.last_time }}</span>
            </div>
          </div>
          <div v-if="chatStore.conversations.length === 0" class="empty-state">
            <p>暂无会话</p>
          </div>
        </div>
      </div>

      <div class="chat-main">
        <div v-if="chatStore.currentConversation" class="chat-header">
          <h3>{{ chatStore.currentConversation.title || chatStore.currentConversation.exam_title || '聊天' }}</h3>
          <span v-if="chatStore.currentConversation.exam_title" class="exam-tag">考试聊天</span>
          <span :class="['ws-status', { online: chatStore.wsConnected }]">
            {{ chatStore.wsConnected ? '实时已连接' : '连接中...' }}
          </span>
        </div>
        
        <div v-else class="chat-empty">
          <div class="empty-content">
            <div class="empty-icon">💬</div>
            <p>请选择一个会话开始聊天</p>
          </div>
        </div>

        <div v-if="chatStore.currentConversation" class="messages-container" ref="messagesContainer">
          <div
            v-for="msg in chatStore.messages"
            :key="msg.id"
            :class="['message', { own: msg.is_own }]"
          >
            <div class="message-avatar">
              {{ msg.sender_username.charAt(0).toUpperCase() }}
            </div>
            <div class="message-content">
              <div class="message-info">
                <span class="sender-name">{{ msg.sender_username }}</span>
                <span class="message-time">{{ msg.created_at }}</span>
              </div>
              <div class="message-bubble">{{ msg.content }}</div>
            </div>
          </div>
        </div>

        <div v-if="chatStore.currentConversation" class="input-area">
          <div class="input-wrapper">
            <textarea
              v-model="messageInput"
              placeholder="输入消息..."
              @keydown="handleKeyDown"
              :disabled="chatStore.sending"
              rows="1"
            />
            <button
              @click="sendMessage"
              :disabled="!messageInput.trim() || chatStore.sending"
              class="send-btn"
            >
              <span v-if="chatStore.sending">发送中...</span>
              <span v-else>发送</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal-card">
        <h3>新建会话</h3>
        <div class="form-group">
          <label>会话类型</label>
          <select v-model="createForm.type">
            <option value="private">私聊</option>
            <option value="exam">考试聊天室</option>
          </select>
        </div>
        <div v-if="createForm.type === 'private'" class="form-group">
          <label>对方用户名</label>
          <input v-model="createForm.targetUsername" placeholder="请输入用户名" />
        </div>
        <div v-if="createForm.type === 'exam'" class="form-group">
          <label>考试 ID</label>
          <input v-model="createForm.examId" type="number" placeholder="请输入考试 ID" />
        </div>
        <div class="form-group">
          <label>会话标题（可选）</label>
          <input v-model="createForm.title" placeholder="留空则自动生成" />
        </div>
        <p v-if="createError" class="error-text">{{ createError }}</p>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showCreateModal = false">取消</button>
          <button class="btn-primary" :disabled="creating" @click="handleCreateConversation">
            {{ creating ? '创建中...' : '创建' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChatStore } from '../stores/chat'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const chatStore = useChatStore()
const messageInput = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const showCreateModal = ref(false)
const creating = ref(false)
const createError = ref('')
const createForm = ref({
  type: 'private',
  targetUsername: '',
  examId: '',
  title: '',
})

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const sendMessage = () => {
  if (messageInput.value.trim()) {
    chatStore.sendMessage(messageInput.value)
    messageInput.value = ''
    scrollToBottom()
  }
}

const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const autoResize = (e: Event) => {
  const target = e.target as HTMLTextAreaElement
  target.style.height = 'auto'
  target.style.height = Math.min(target.scrollHeight, 120) + 'px'
}

watch(() => chatStore.messages, () => {
  scrollToBottom()
}, { deep: true })

const handleCreateConversation = async () => {
  createError.value = ''
  creating.value = true
  try {
    let conversationId: number | null = null
    if (createForm.value.type === 'exam') {
      const examId = Number(createForm.value.examId)
      if (!examId) {
        createError.value = '请输入有效的考试 ID'
        return
      }
      conversationId = await chatStore.joinExamConversation(examId)
    } else {
      if (!createForm.value.targetUsername.trim()) {
        createError.value = '请输入对方用户名'
        return
      }
      conversationId = await chatStore.createConversation({
        type: 'private',
        title: createForm.value.title.trim() || undefined,
        target_username: createForm.value.targetUsername.trim(),
      })
      if (conversationId) {
        await chatStore.selectConversation(conversationId)
      }
    }
    if (conversationId) {
      showCreateModal.value = false
      createForm.value = { type: 'private', targetUsername: '', examId: '', title: '' }
    }
  } catch (error: unknown) {
    createError.value = error instanceof Error ? error.message : '创建失败'
  } finally {
    creating.value = false
  }
}

const bootstrapFromRoute = async () => {
  const examId = route.query.exam_id
  const conversationId = route.query.conversation

  if (examId) {
    await chatStore.joinExamConversation(Number(examId))
    router.replace({ path: '/chat' })
    return
  }

  if (conversationId) {
    await chatStore.selectConversation(Number(conversationId))
    router.replace({ path: '/chat' })
  }
}

onMounted(async () => {
  await chatStore.loadConversations()
  await bootstrapFromRoute()
  chatStore.startListPolling()
})

onUnmounted(() => {
  chatStore.stopRealtime()
})
</script>

<style scoped>
.chat-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  font-size: 1.75rem;
}

.brand-text {
  font-size: 1.5rem;
  font-weight: 700;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.welcome-text {
  font-size: 0.9rem;
}

.back-btn {
  padding: 0.5rem 1.25rem;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  text-decoration: none;
  border-radius: 20px;
  font-weight: 500;
  transition: all 0.3s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.chat-container {
  display: flex;
  height: calc(100vh - 70px);
}

.sidebar {
  width: 300px;
  background: white;
  border-right: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 1.25rem;
  border-bottom: 1px solid #e8e8e8;
  background: #fafafa;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.new-chat-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: #667eea;
  color: white;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  width: 420px;
  max-width: calc(100vw - 2rem);
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.modal-card h3 {
  margin: 0 0 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.form-group label {
  font-size: 0.9rem;
  color: #666;
}

.form-group input,
.form-group select {
  padding: 0.65rem 0.75rem;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 0.95rem;
}

.error-text {
  color: #ff4d4f;
  font-size: 0.85rem;
  margin-bottom: 0.75rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
}

.conversation-item {
  padding: 1rem 1.25rem;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}

.conversation-item:hover {
  background: #f5f5f5;
}

.conversation-item.active {
  background: #e6f7ff;
  border-left: 3px solid #667eea;
}

.conv-info {
  flex: 1;
}

.conv-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.unread-badge {
  background: #ff4d4f;
  color: white;
  font-size: 0.75rem;
  padding: 0.1rem 0.5rem;
  border-radius: 10px;
}

.conv-preview {
  font-size: 0.85rem;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conv-meta {
  margin-top: 0.5rem;
}

.conv-time {
  font-size: 0.75rem;
  color: #999;
}

.empty-state {
  padding: 3rem 1rem;
  text-align: center;
  color: #999;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
}

.chat-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #fafafa;
}

.chat-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
}

.exam-tag {
  font-size: 0.75rem;
  padding: 0.25rem 0.75rem;
  background: #e6f7ff;
  color: #1890ff;
  border-radius: 4px;
}

.ws-status {
  margin-left: auto;
  font-size: 0.75rem;
  color: #999;
}

.ws-status.online {
  color: #52c41a;
}

.chat-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}

.empty-content {
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.messages-container {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  background: #f5f7fa;
}

.message {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  align-items: flex-start;
}

.message.own {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
}

.message-info {
  margin-bottom: 0.25rem;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.message.own .message-info {
  justify-content: flex-end;
}

.sender-name {
  font-size: 0.85rem;
  font-weight: 500;
  color: #666;
}

.message-time {
  font-size: 0.75rem;
  color: #999;
}

.message-bubble {
  padding: 0.75rem 1rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
}

.message.own .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.input-area {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e8e8e8;
  background: white;
}

.input-wrapper {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
}

.input-wrapper textarea {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #d9d9d9;
  border-radius: 20px;
  font-size: 0.95rem;
  resize: none;
  outline: none;
  transition: border-color 0.3s;
  max-height: 120px;
  overflow-y: auto;
  line-height: 1.5;
}

.input-wrapper textarea:focus {
  border-color: #667eea;
}

.send-btn {
  padding: 0.75rem 1.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 20px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
