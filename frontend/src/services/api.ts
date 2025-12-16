// Service API pour communiquer avec le backend Jarvis

import axios, { type AxiosInstance } from 'axios'
import type {
  VoiceProcessResponse,
  KnowledgeGraph,
  HealthCheckResponse,
} from '@/types/api'

class JarvisAPI {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      timeout: 60000, // 60 secondes pour le traitement vocal
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  /**
   * Vérifie l'état de santé du backend
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await this.client.get<HealthCheckResponse>('/health')
    return response.data
  }

  /**
   * Traite un message vocal
   */
  async processVoice(audioBlob: Blob): Promise<VoiceProcessResponse> {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.webm')

    const response = await this.client.post<VoiceProcessResponse>(
      '/voice/process',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    return response.data
  }

  /**
   * Récupère le knowledge graph
   */
  async getKnowledgeGraph(): Promise<KnowledgeGraph> {
    const response = await this.client.get<KnowledgeGraph>('/knowledge/graph')
    return response.data
  }

  /**
   * Recherche dans le knowledge graph
   */
  async queryKnowledge(query: string): Promise<any> {
    const response = await this.client.post('/knowledge/query', { query })
    return response.data
  }

  /**
   * Télécharge l'audio de la réponse
   */
  getAudioUrl(audioPath: string): string {
    return `${this.client.defaults.baseURL}${audioPath}`
  }
}

// Export une instance singleton
export const jarvisApi = new JarvisAPI()
export default jarvisApi
