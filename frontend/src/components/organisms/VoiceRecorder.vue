<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Microphone, Loading, VideoPlay } from '@element-plus/icons-vue'
import { BaseIcon, BaseSpinner, BaseBadge } from '../atoms'
import { useConversationStore } from '@/stores/conversation'

// Props
interface Props {
  size?: 'large' | 'default' | 'small'
  showWaveform?: boolean
  iconSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  size: 'large',
  showWaveform: true,
  iconSize: 48,
})

// Store
const conversationStore = useConversationStore()

// State
const mediaRecorder = ref<MediaRecorder | null>(null)
const audioChunks = ref<Blob[]>([])
const stream = ref<MediaStream | null>(null)
const waveformCanvas = ref<HTMLCanvasElement | null>(null)
const animationFrame = ref<number | null>(null)
const audioContext = ref<AudioContext | null>(null)
const analyser = ref<AnalyserNode | null>(null)

// Computed
const isRecording = computed(() => conversationStore.isRecording)
const isProcessing = computed(() => conversationStore.isProcessing)

const buttonClasses = computed(() => {
  const classes = ['mic-button']
  if (isRecording.value) classes.push('is-recording')
  if (isProcessing.value) classes.push('is-processing')
  return classes
})

// Methods
async function startRecording() {
  if (isRecording.value || isProcessing.value) return

  try {
    stream.value = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 16000,
      }
    })

    const options = { mimeType: 'audio/webm' }
    mediaRecorder.value = new MediaRecorder(stream.value, options)
    audioChunks.value = []

    mediaRecorder.value.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data)
      }
    }

    if (props.showWaveform && waveformCanvas.value) {
      setupWaveform()
    }

    mediaRecorder.value.start()
    conversationStore.setRecording(true)

  } catch (error: any) {
    console.error('Erreur microphone:', error)
    ElMessage.error(`Impossible d'accéder au microphone`)
  }
}

async function stopRecording() {
  if (!isRecording.value || !mediaRecorder.value) return

  return new Promise<void>((resolve) => {
    if (!mediaRecorder.value) {
      resolve()
      return
    }

    mediaRecorder.value.onstop = async () => {
      try {
        const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' })
        cleanup()
        await conversationStore.processVoiceMessage(audioBlob)
        resolve()
      } catch (error: any) {
        console.error('Erreur traitement:', error)
        ElMessage.error('Erreur lors du traitement')
        conversationStore.setRecording(false)
        resolve()
      }
    }

    mediaRecorder.value.stop()
  })
}

function setupWaveform() {
  if (!stream.value || !waveformCanvas.value) return

  audioContext.value = new AudioContext()
  const source = audioContext.value.createMediaStreamSource(stream.value)
  analyser.value = audioContext.value.createAnalyser()
  analyser.value.fftSize = 2048
  source.connect(analyser.value)

  drawWaveform()
}

function drawWaveform() {
  if (!waveformCanvas.value || !analyser.value) return

  const canvas = waveformCanvas.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const bufferLength = analyser.value.frequencyBinCount
  const dataArray = new Uint8Array(bufferLength)

  function draw() {
    if (!analyser.value || !ctx) return

    animationFrame.value = requestAnimationFrame(draw)
    analyser.value.getByteTimeDomainData(dataArray)

    ctx.fillStyle = 'rgba(10, 14, 39, 0.3)'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    ctx.lineWidth = 2
    ctx.strokeStyle = '#667eea'
    ctx.beginPath()

    const sliceWidth = canvas.width / bufferLength
    let x = 0

    for (let i = 0; i < bufferLength; i++) {
      const v = dataArray[i] / 128.0
      const y = (v * canvas.height) / 2

      if (i === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }

      x += sliceWidth
    }

    ctx.lineTo(canvas.width, canvas.height / 2)
    ctx.stroke()
  }

  draw()
}

function cleanup() {
  if (animationFrame.value) {
    cancelAnimationFrame(animationFrame.value)
    animationFrame.value = null
  }

  if (audioContext.value) {
    audioContext.value.close()
    audioContext.value = null
  }

  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop())
    stream.value = null
  }

  audioChunks.value = []
  mediaRecorder.value = null
  conversationStore.setRecording(false)
}

onUnmounted(() => {
  cleanup()
})
</script>

<template>
  <div class="voice-recorder flex flex-col items-center gap-6">
    <!-- Microphone Button -->
    <div class="relative flex items-center justify-center w-32 h-32">
      <!-- Recording Rings -->
      <div v-if="isRecording" class="absolute inset-0 pointer-events-none">
        <div class="ring ring-1"></div>
        <div class="ring ring-2"></div>
        <div class="ring ring-3"></div>
      </div>

      <!-- Button -->
      <button
        :class="buttonClasses"
        :disabled="isProcessing"
        @mousedown="startRecording"
        @mouseup="stopRecording"
        @touchstart.prevent="startRecording"
        @touchend.prevent="stopRecording"
        class="relative z-10"
      >
        <BaseIcon v-if="!isRecording && !isProcessing" :size="iconSize">
          <Microphone />
        </BaseIcon>
        <BaseSpinner v-else-if="isProcessing" size="lg" color="white" />
        <BaseIcon v-else :size="iconSize" class="pulsing">
          <VideoPlay />
        </BaseIcon>
      </button>
    </div>

    <!-- Waveform -->
    <div v-if="showWaveform && isRecording" class="w-full max-w-md p-4 glass-effect rounded-2xl">
      <canvas ref="waveformCanvas" class="w-full h-20 rounded-lg" width="400" height="80"></canvas>
    </div>

    <!-- Status Badge -->
    <BaseBadge
      v-if="isRecording"
      type="error"
      dot
      pulse
      size="md"
    >
      Enregistrement...
    </BaseBadge>
    <BaseBadge
      v-else-if="isProcessing"
      type="warning"
      dot
      pulse
      size="md"
    >
      Traitement en cours...
    </BaseBadge>
  </div>
</template>

<style lang="scss" scoped>
@import '@/styles/main.scss';

.mic-button {
  @apply w-32 h-32 rounded-full flex items-center justify-center
         text-white cursor-pointer border-none transition-all duration-300;
  @include gradient-primary;
  box-shadow: 0 8px 24px rgba($primary, 0.4);

  &:hover:not(:disabled) {
    transform: scale(1.05);
    box-shadow: 0 12px 32px rgba($primary, 0.6);
  }

  &:active:not(:disabled) {
    transform: scale(0.95);
  }

  &.is-recording {
    background: linear-gradient(135deg, $error 0%, darken($error, 10%) 100%);
    box-shadow: 0 8px 24px rgba($error, 0.6);
    animation: pulse-glow 1.5s ease-in-out infinite;
  }

  &.is-processing {
    background: linear-gradient(135deg, $warning 0%, darken($warning, 10%) 100%);
    @apply cursor-wait opacity-80;
  }

  &:disabled {
    @apply cursor-not-allowed opacity-60;
  }
}

.ring {
  @apply absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
         border-2 border-primary rounded-full;
  animation: ripple 2s ease-out infinite;

  &.ring-1 {
    animation-delay: 0s;
  }

  &.ring-2 {
    animation-delay: 0.6s;
  }

  &.ring-3 {
    animation-delay: 1.2s;
  }
}

.pulsing {
  animation: pulse-icon 1s ease-in-out infinite;
}

@keyframes pulse-icon {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 8px 24px rgba($error, 0.6);
  }
  50% {
    box-shadow: 0 8px 32px rgba($error, 0.9);
  }
}
</style>
