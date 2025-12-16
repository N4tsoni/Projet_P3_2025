// Store Pinia pour gérer les conversations avec Jarvis

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ConversationMessage } from '@/types/api'
import { jarvisApi } from '@/services/api'

export const useConversationStore = defineStore('conversation', () => {
  // State
  const messages = ref<ConversationMessage[]>([])
  const isRecording = ref(false)
  const isProcessing = ref(false)
  const currentAudio = ref<HTMLAudioElement | null>(null)
  const error = ref<string | null>(null)

  // Getters
  const messageCount = computed(() => messages.value.length)
  const lastMessage = computed(() => messages.value[messages.value.length - 1])
  const isPlaying = computed(() => {
    return currentAudio.value && !currentAudio.value.paused
  })

  // Actions
  function addMessage(message: Omit<ConversationMessage, 'id' | 'timestamp'>) {
    const newMessage: ConversationMessage = {
      ...message,
      id: crypto.randomUUID(),
      timestamp: new Date(),
    }
    messages.value.push(newMessage)
  }

  function setRecording(recording: boolean) {
    isRecording.value = recording
  }

  function setProcessing(processing: boolean) {
    isProcessing.value = processing
  }

  function setError(errorMessage: string | null) {
    error.value = errorMessage
  }

  async function processVoiceMessage(audioBlob: Blob) {
    try {
      setProcessing(true)
      setError(null)

      const response = await jarvisApi.processVoice(audioBlob)

      // Ajouter le message de l'utilisateur
      addMessage({
        role: 'user',
        content: response.transcription,
      })

      // Ajouter la réponse de Jarvis
      addMessage({
        role: 'assistant',
        content: response.response,
        audioUrl: response.audioUrl,
      })

      // Jouer l'audio de la réponse automatiquement
      if (response.audioUrl) {
        await playAudio(response.audioUrl)
      }

      return response
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Erreur inconnue'
      setError(errorMsg)
      throw err
    } finally {
      setProcessing(false)
    }
  }

  async function playAudio(audioUrl: string) {
    try {
      // Arrêter l'audio en cours si nécessaire
      if (currentAudio.value) {
        currentAudio.value.pause()
        currentAudio.value = null
      }

      const audio = new Audio(audioUrl)
      currentAudio.value = audio

      return new Promise((resolve, reject) => {
        audio.onended = () => {
          currentAudio.value = null
          resolve(true)
        }
        audio.onerror = () => {
          currentAudio.value = null
          reject(new Error('Erreur lors de la lecture audio'))
        }
        audio.play()
      })
    } catch (err) {
      console.error('Erreur lors de la lecture audio:', err)
      throw err
    }
  }

  function stopAudio() {
    if (currentAudio.value) {
      currentAudio.value.pause()
      currentAudio.value = null
    }
  }

  function clearMessages() {
    messages.value = []
    stopAudio()
  }

  return {
    // State
    messages,
    isRecording,
    isProcessing,
    error,
    // Getters
    messageCount,
    lastMessage,
    isPlaying,
    // Actions
    addMessage,
    setRecording,
    setProcessing,
    setError,
    processVoiceMessage,
    playAudio,
    stopAudio,
    clearMessages,
  }
})
