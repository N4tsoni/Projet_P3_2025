<template>
  <div class="conversation-history">
    <!-- Header avec actions -->
    <div v-if="messages.length > 0" class="history-header">
      <div class="header-title">
        <el-icon><ChatLineRound /></el-icon>
        <span>{{ messages.length }} messages</span>
      </div>
      <el-button
        size="small"
        type="danger"
        text
        @click="handleClear"
        class="clear-button"
      >
        <el-icon><Delete /></el-icon>
        Effacer
      </el-button>
    </div>

    <!-- Messages -->
    <el-scrollbar v-if="messages.length > 0" class="messages-scrollbar">
      <div class="messages-list">
        <div
          v-for="(message, index) in messages"
          :key="message.id"
          :class="['message-item', `message-${message.role}`]"
          :style="{ animationDelay: `${index * 0.05}s` }"
        >
          <div class="message-avatar">
            <div :class="['avatar-circle', `avatar-${message.role}`]">
              <el-icon :size="20">
                <User v-if="message.role === 'user'" />
                <Cpu v-else />
              </el-icon>
            </div>
          </div>

          <div class="message-content-wrapper">
            <div class="message-header-info">
              <span class="message-author">
                {{ message.role === 'user' ? 'Vous' : 'Jarvis' }}
              </span>
              <span class="message-time">
                {{ formatTime(message.timestamp) }}
              </span>
            </div>

            <div class="message-content">
              {{ message.content }}
            </div>

            <!-- Audio player pour Jarvis -->
            <div v-if="message.audioUrl && message.role === 'assistant'" class="message-audio">
              <button
                :class="['audio-button', { 'is-playing': isPlayingMessage(message.id) }]"
                @click="toggleAudio(message)"
              >
                <el-icon :size="16">
                  <VideoPlay v-if="!isPlayingMessage(message.id)" />
                  <VideoPause v-else />
                </el-icon>
                <span>{{ isPlayingMessage(message.id) ? 'Pause' : 'Écouter' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </el-scrollbar>

    <!-- Empty state -->
    <div v-else class="empty-state">
      <div class="empty-icon">
        <el-icon :size="64">
          <ChatDotRound />
        </el-icon>
      </div>
      <h3>Aucune conversation</h3>
      <p>Commencez à parler avec Jarvis pour voir l'historique apparaître ici</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  ElScrollbar,
  ElButton,
  ElIcon,
  ElMessageBox,
} from 'element-plus'
import {
  ChatLineRound,
  ChatDotRound,
  Delete,
  User,
  Cpu,
  VideoPlay,
  VideoPause,
} from '@element-plus/icons-vue'
import { useConversationStore } from '@/stores/conversation'
import type { ConversationMessage } from '@/types/api'

// Store
const conversationStore = useConversationStore()

// State
const playingMessageId = ref<string | null>(null)

// Computed
const messages = computed(() => conversationStore.messages)

// Methods
function formatTime(timestamp: Date): string {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

function isPlayingMessage(messageId: string): boolean {
  return playingMessageId.value === messageId
}

async function toggleAudio(message: ConversationMessage) {
  if (!message.audioUrl) return

  try {
    if (isPlayingMessage(message.id)) {
      conversationStore.stopAudio()
      playingMessageId.value = null
    } else {
      playingMessageId.value = message.id
      await conversationStore.playAudio(message.audioUrl)
      playingMessageId.value = null
    }
  } catch (error) {
    console.error('Erreur lecture audio:', error)
    playingMessageId.value = null
  }
}

async function handleClear() {
  try {
    await ElMessageBox.confirm(
      'Êtes-vous sûr de vouloir effacer tout l\'historique ?',
      'Confirmation',
      {
        confirmButtonText: 'Effacer',
        cancelButtonText: 'Annuler',
        type: 'warning',
      }
    )
    conversationStore.clearMessages()
  } catch {
    // Cancelled
  }
}
</script>

<style scoped>
.conversation-history {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 1rem;
}

/* Header */
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.header-title .el-icon {
  color: #667eea;
}

.clear-button {
  color: #ef4444 !important;
  transition: all 0.3s ease;
}

.clear-button:hover {
  background: rgba(239, 68, 68, 0.1) !important;
}

/* Scrollbar */
.messages-scrollbar {
  flex: 1;
  height: 100%;
}

.messages-scrollbar :deep(.el-scrollbar__wrap) {
  overflow-x: hidden;
}

/* Messages List */
.messages-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 0.5rem;
}

/* Message Item */
.message-item {
  display: flex;
  gap: 0.75rem;
  opacity: 0;
  animation: slideIn 0.3s ease forwards;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-user {
  flex-direction: row-reverse;
}

/* Avatar */
.message-avatar {
  flex-shrink: 0;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.avatar-user {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.avatar-assistant {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

/* Message Content Wrapper */
.message-content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 70%;
}

.message-user .message-content-wrapper {
  align-items: flex-end;
}

/* Message Header Info */
.message-header-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 12px;
}

.message-author {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.message-time {
  color: rgba(255, 255, 255, 0.4);
}

/* Message Content */
.message-content {
  padding: 0.875rem 1.125rem;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  word-wrap: break-word;
  transition: all 0.3s ease;
}

.message-user .message-content {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  color: rgba(255, 255, 255, 0.95);
  border-radius: 16px 16px 4px 16px;
}

.message-assistant .message-content {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.9);
  border-radius: 16px 16px 16px 4px;
}

.message-content:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-1px);
}

/* Audio Button */
.message-audio {
  display: flex;
  justify-content: flex-start;
}

.audio-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.audio-button:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: #667eea;
  color: #667eea;
  transform: translateX(2px);
}

.audio-button.is-playing {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  border-color: #667eea;
  color: #667eea;
}

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 3rem 2rem;
  text-align: center;
}

.empty-icon {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.empty-state p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  max-width: 300px;
}
</style>
