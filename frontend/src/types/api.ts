// Types pour l'API Jarvis

export interface VoiceProcessRequest {
  audio: File | Blob
}

export interface VoiceProcessResponse {
  transcription: string
  response: string
  audioUrl: string
  processingTime?: number
}

export interface ConversationMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  audioUrl?: string
}

export interface KnowledgeNode {
  id: string
  label: string
  type: string
  properties: Record<string, any>
}

export interface KnowledgeEdge {
  id: string
  source: string
  target: string
  type: string
  properties: Record<string, any>
}

export interface KnowledgeGraph {
  nodes: KnowledgeNode[]
  edges: KnowledgeEdge[]
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy'
  version?: string
  services?: {
    neo4j: boolean
    whisper: boolean
    tts: boolean
  }
}
