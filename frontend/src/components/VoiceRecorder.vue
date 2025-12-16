<template>
  <div class="voice-recorder">
    <!-- Bouton microphone avec effet -->
    <div class="mic-button-container">
      <div v-if="isRecording" class="recording-rings">
        <div class="ring ring-1"></div>
        <div class="ring ring-2"></div>
        <div class="ring ring-3"></div>
      </div>

      <button
        :class="['mic-button', { 'is-recording': isRecording, 'is-processing': isProcessing }]"
        :disabled="isProcessing"
        @mousedown="startRecording"
        @mouseup="stopRecording"
        @touchstart.prevent="startRecording"
        @touchend.prevent="stopRecording"
      >
        <el-icon v-if="!isRecording && !isProcessing" :size="iconSize">
          <Microphone />
        </el-icon>
        <el-icon v-else-if="isProcessing" :size="iconSize" class="spinning">
          <Loading />
        </el-icon>
        <el-icon v-else :size="iconSize" class="pulsing">
          <VideoPlay />
        </el-icon>
      </button>
    </div>

    <!-- Visualisation waveform -->
    <div v-if="showWaveform && isRecording" class="waveform-container">
      <canvas ref="waveformCanvas" class="waveform-canvas" width="400" height="80"></canvas>
    </div>

    <!-- État -->
    <div v-if="statusMessage" class="status-container">
      <div :class="['status-message', statusType]">
        {{ statusMessage }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { ElIcon, ElMessage } from 'element-plus'
import { Microphone, Loading, VideoPlay } from '@element-plus/icons-vue'
import { useConversationStore } from '@/stores/conversation'

// Props
interface Props {
  size?: 'large' | 'default' | 'small'
  circle?: boolean
  showWaveform?: boolean
  iconSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  size: 'large',
  circle: true,
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

const statusMessage = computed(() => {
  if (isProcessing.value) return 'Traitement en cours...'
  if (isRecording.value) return 'Enregistrement...'
  return ''
})

const statusType = computed(() => {
  if (isProcessing.value) return 'processing'
  if (isRecording.value) return 'recording'
  return 'idle'
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

    // Background
    ctx.fillStyle = 'rgba(10, 14, 39, 0.3)'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    // Waveform
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

<style scoped>
.voice-recorder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

/* Microphone Button Container */
.mic-button-container {
  position: relative;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Recording Rings Animation */
.recording-rings {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border: 2px solid #667eea;
  border-radius: 50%;
  animation: ripple 2s ease-out infinite;
}

.ring-1 {
  animation-delay: 0s;
}

.ring-2 {
  animation-delay: 0.6s;
}

.ring-3 {
  animation-delay: 1.2s;
}

@keyframes ripple {
  0% {
    width: 100%;
    height: 100%;
    opacity: 1;
  }
  100% {
    width: 200%;
    height: 200%;
    opacity: 0;
  }
}

/* Microphone Button */
.mic-button {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
  position: relative;
  z-index: 1;
}

.mic-button:hover {
  transform: scale(1.05);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.6);
}

.mic-button:active {
  transform: scale(0.95);
}

.mic-button.is-recording {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  box-shadow: 0 8px 24px rgba(239, 68, 68, 0.6);
  animation: pulse-glow 1.5s ease-in-out infinite;
}

.mic-button.is-processing {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  cursor: not-allowed;
  opacity: 0.8;
}

.mic-button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 8px 24px rgba(239, 68, 68, 0.6);
  }
  50% {
    box-shadow: 0 8px 32px rgba(239, 68, 68, 0.9);
  }
}

/* Icon Animations */
.spinning {
  animation: spin 1s linear infinite;
}

.pulsing {
  animation: pulse-icon 1s ease-in-out infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse-icon {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

/* Waveform */
.waveform-container {
  width: 100%;
  max-width: 400px;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

.waveform-canvas {
  width: 100%;
  height: 80px;
  border-radius: 8px;
}

/* Status */
.status-container {
  text-align: center;
}

.status-message {
  font-size: 14px;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.status-message.recording {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.status-message.processing {
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
}
</style>
