<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElTabs, ElTabPane, ElBadge } from 'element-plus'
import { Headset, Microphone, ChatDotRound, Connection } from '@element-plus/icons-vue'
import { BaseIcon, BaseBadge } from './components/atoms'
import VoiceRecorder from './components/organisms/VoiceRecorder.vue'
import ConversationHistory from './components/organisms/ConversationHistory.vue'
import KnowledgeGraphViz from './components/organisms/KnowledgeGraphViz.vue'
import { jarvisApi } from './services/api'
import { useConversationStore } from './stores/conversation'

// Store
const conversationStore = useConversationStore()

// State
const activeTab = ref('conversation')
const isHealthy = ref(false)
const healthCheckError = ref<string | null>(null)

// Computed
const messageCount = computed(() => conversationStore.messageCount)

const healthBadgeType = computed(() => {
  if (healthCheckError.value) return 'error'
  return isHealthy.value ? 'success' : 'warning'
})

const healthText = computed(() => {
  if (healthCheckError.value) return 'Déconnecté'
  return isHealthy.value ? 'Opérationnel' : 'Connexion...'
})

// Methods
async function checkHealth() {
  try {
    const response = await jarvisApi.healthCheck()
    isHealthy.value = response.status === 'healthy'
    healthCheckError.value = null
  } catch (error: any) {
    isHealthy.value = false
    healthCheckError.value = error.message
    console.error('Health check failed:', error)
  }
}

// Lifecycle
onMounted(() => {
  checkHealth()
  setInterval(checkHealth, 30000)
})
</script>

<template>
  <div class="app-container relative w-full h-full bg-dark overflow-hidden">
    <!-- Animated Background -->
    <div class="background-animation absolute w-full h-full overflow-hidden z-0">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
    </div>

    <!-- Main Content -->
    <div class="main-content relative z-10 w-full h-full p-8 flex flex-col gap-8">
      <!-- Header -->
      <header class="app-header flex items-center justify-between p-6 glass-effect rounded-3xl">
        <div class="logo-section flex items-center gap-4">
          <div class="logo-icon w-12 h-12 gradient-primary rounded-xl flex items-center justify-center shadow-lg">
            <BaseIcon :size="32" color="white">
              <Headset />
            </BaseIcon>
          </div>
          <div class="logo-text">
            <h1 class="text-3xl font-bold gradient-text">J.A.R.V.I.S</h1>
            <p class="text-xs text-white/50 tracking-wider">Just A Rather Very Intelligent System</p>
          </div>
        </div>

        <BaseBadge :type="healthBadgeType" dot pulse size="md">
          {{ healthText }}
        </BaseBadge>
      </header>

      <!-- Main Interface -->
      <div class="interface-container flex-1 grid grid-cols-1 lg:grid-cols-[450px_1fr] gap-8 overflow-hidden">
        <!-- Voice Recorder Card -->
        <div class="recorder-card glass-effect rounded-3xl p-8 flex flex-col items-center justify-center gap-6">
          <div class="card-title flex items-center gap-3 text-lg font-semibold text-white/90">
            <BaseIcon :size="24" color="#667eea">
              <Microphone />
            </BaseIcon>
            <span>Assistant Vocal</span>
          </div>

          <VoiceRecorder
            size="large"
            :show-waveform="true"
            :icon-size="56"
          />

          <p class="recorder-hint text-sm text-white/50 text-center">
            Maintenez le bouton pour parler avec Jarvis
          </p>
        </div>

        <!-- Conversation & Graph Tabs -->
        <div class="content-tabs-container glass-effect rounded-3xl p-6 flex flex-col overflow-hidden">
          <ElTabs v-model="activeTab" class="modern-tabs flex-1 flex flex-col">
            <!-- Conversation Tab -->
            <ElTabPane name="conversation">
              <template #label>
                <div class="tab-label flex items-center gap-2">
                  <BaseIcon :size="20">
                    <ChatDotRound />
                  </BaseIcon>
                  <span>Conversations</span>
                  <ElBadge v-if="messageCount > 0" :value="messageCount" class="ml-2" />
                </div>
              </template>

              <div class="tab-content">
                <ConversationHistory />
              </div>
            </ElTabPane>

            <!-- Knowledge Graph Tab -->
            <ElTabPane name="knowledge">
              <template #label>
                <div class="tab-label flex items-center gap-2">
                  <BaseIcon :size="20">
                    <Connection />
                  </BaseIcon>
                  <span>Knowledge Graph</span>
                </div>
              </template>

              <div class="tab-content">
                <KnowledgeGraphViz />
              </div>
            </ElTabPane>
          </ElTabs>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
@import '@/styles/main.scss';
</style>

<style lang="scss" scoped>
@import '@/styles/main.scss';

.gradient-orb {
  @apply absolute rounded-full;
  filter: blur(100px);
  opacity: 0.6;
  animation: float 20s ease-in-out infinite;

  &.orb-1 {
    @apply w-[500px] h-[500px];
    background: radial-gradient(circle, rgba(99, 102, 241, 0.8) 0%, rgba(99, 102, 241, 0) 70%);
    top: -200px;
    left: -200px;
    animation-delay: 0s;
  }

  &.orb-2 {
    @apply w-96 h-96;
    background: radial-gradient(circle, rgba(168, 85, 247, 0.8) 0%, rgba(168, 85, 247, 0) 70%);
    bottom: -150px;
    right: -150px;
    animation-delay: 7s;
  }

  &.orb-3 {
    @apply w-[350px] h-[350px];
    background: radial-gradient(circle, rgba(59, 130, 246, 0.8) 0%, rgba(59, 130, 246, 0) 70%);
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    animation-delay: 14s;
  }
}

.gradient-text {
  background: linear-gradient(135deg, #667eea 0%, #a855f7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 2px;
}

.recorder-card,
.content-tabs-container {
  @apply transition-all duration-300;

  &:hover {
    @apply -translate-y-1;
    box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4);
  }
}

.modern-tabs {
  :deep(.el-tabs__header) {
    @apply mb-6 border-none;
  }

  :deep(.el-tabs__nav-wrap::after) {
    @apply hidden;
  }

  :deep(.el-tabs__nav) {
    @apply glass-effect rounded-xl p-1;
  }

  :deep(.el-tabs__item) {
    @apply text-white/60 px-6 py-3 rounded-lg transition-all border-none;

    &:hover {
      @apply text-white/90 bg-white/5;
    }

    &.is-active {
      @apply text-white;
      @include gradient-primary;
      box-shadow: 0 4px 12px rgba($primary, 0.4);
    }
  }

  :deep(.el-tabs__active-bar) {
    @apply hidden;
  }

  :deep(.el-tabs__content) {
    @apply flex-1 overflow-auto;
  }
}

.tab-label {
  @apply font-medium;
}

.tab-content {
  @apply h-full;
  animation: fadeIn 0.3s ease;
}

@media (max-width: 1024px) {
  .interface-container {
    @apply grid-cols-1 grid-rows-[auto_1fr];
  }

  .recorder-card {
    @apply h-auto;
  }
}
</style>
