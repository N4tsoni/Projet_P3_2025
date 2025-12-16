# Architecture Jarvis - Documentation Technique

> Documentation détaillée de l'architecture actuelle du projet Jarvis

**Date**: 2025-12-16
**Version**: 0.1.0
**État**: Phase 3 complétée (Voice Pipeline opérationnel)

---

## Table des Matières

- [Vue d'Ensemble](#vue-densemble)
- [Architecture des Modules](#architecture-des-modules)
- [Pipeline de Traitement](#pipeline-de-traitement)
- [Flux de Données](#flux-de-données)
- [Implémentation Actuelle](#implémentation-actuelle)
- [Modules À Implémenter](#modules-à-implémenter)
- [Décisions Architecturales](#décisions-architecturales)

---

## Vue d'Ensemble

### Principes d'Architecture

1. **Modularité**: Chaque composant (STT, TTS, Agent, Graph) est indépendant
2. **Async-first**: Toutes les opérations I/O utilisent async/await
3. **Singleton Pattern**: Providers chargés une seule fois (lazy loading)
4. **Configuration centralisée**: Environnement via `.env`
5. **Logging unifié**: Loguru pour tous les modules
6. **API-first**: FastAPI expose tous les services
7. **Containerisation**: Docker pour isolation et déploiement

### Stack Technologique Actuelle

```
┌─────────────────────────────────────────┐
│         Frontend (Browser)              │
│  HTML5 + CSS3 + Vanilla JavaScript      │
│  MediaRecorder + Canvas + Web Audio     │
└────────────────┬────────────────────────┘
                 │ HTTP/WebM
                 ▼
┌─────────────────────────────────────────┐
│         Backend (Docker Container)       │
│  ┌───────────────────────────────────┐  │
│  │  FastAPI (Python 3.11)            │  │
│  │  - Uvicorn ASGI Server            │  │
│  │  - CORS Middleware                │  │
│  │  - Static Files Serving           │  │
│  └───────────────┬───────────────────┘  │
│                  │                       │
│  ┌───────────────┼───────────────────┐  │
│  │               │                   │  │
│  ▼               ▼                   ▼  │
│  STT           Agent                TTS │
│  (Whisper)     (Claude)        (EdgeTTS)│
└─────────────────┬───────────────────────┘
                  │ Neo4j Bolt Protocol
                  ▼
┌─────────────────────────────────────────┐
│     Neo4j (Docker Container)            │
│  - Graph Database 5.15                  │
│  - APOC Plugin                          │
│  - Graphiti Framework                   │
└─────────────────────────────────────────┘
```

---

## Architecture des Modules

### 1. API Layer (`src/api/main.py`)

**Responsabilité**: Exposition HTTP des services

```python
FastAPI Application
├── Endpoints
│   ├── GET  /               # Serve web interface
│   ├── GET  /health         # Health check
│   ├── POST /api/voice/process  # Main voice pipeline
│   ├── GET  /api/knowledge/query  # Knowledge graph query (TODO)
│   └── POST /api/knowledge/add    # Add knowledge (TODO)
├── Middleware
│   └── CORS (allow all origins for ESP32)
└── Static Files
    └── /static/* (index.html, app.js, response_*.mp3)
```

**Implémentation**:
- 188 lignes de code
- Async request handlers
- Gestion fichiers temporaires (`/app/data/temp/`)
- UUID pour identifiants uniques de requêtes
- Error handling avec HTTPException

**Dépendances**:
```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.voice.stt import transcribe_audio
from src.voice.tts import synthesize_speech
from src.agents.jarvis_agent import get_agent
```

---

### 2. Voice Processing Layer

#### 2.1 Speech-to-Text (`src/voice/stt.py`)

**Responsabilité**: Conversion audio → texte

**Providers Implémentés**:

| Provider | Type | Avantages | Inconvénients |
|----------|------|-----------|---------------|
| **WhisperLocalSTT** | Local | Gratuit, privacy, multilangue | Lent (CPU), 1ère utilisation télécharge modèle |
| **GroqSTT** | Cloud | Rapide, gratuit | Requiert clé API, pas de privacy |

**Architecture**:
```python
class STTProvider(ABC):
    @abstractmethod
    async def transcribe(file_path, language) -> str
        # Interface commune

class WhisperLocalSTT(STTProvider):
    _model = None  # Singleton, lazy loading

    def _load_model(self):
        # Charge en mémoire une seule fois
        # Modèles: tiny, base, small, medium, large

    async def transcribe(self, file_path, language):
        # Conversion WebM → WAV → Transcription
        # ffmpeg requis pour conversion format

class GroqSTT(STTProvider):
    async def transcribe(self, file_path, language):
        # API call to Groq Whisper endpoint

# Factory function
async def transcribe_audio(file_path, language="fr") -> str:
    provider = get_stt_provider()  # Based on .env
    return await provider.transcribe(file_path, language)
```

**Configuration (.env)**:
```bash
STT_PROVIDER=whisper-local  # ou "groq"
STT_MODEL=base              # tiny, base, small, medium, large
GROQ_API_KEY=gsk_xxx        # si provider=groq
```

**Formats supportés**: WebM, WAV, MP3, M4A (via ffmpeg)

---

#### 2.2 Text-to-Speech (`src/voice/tts.py`)

**Responsabilité**: Conversion texte → audio

**Providers Implémentés**:

| Provider | Type | Avantages | Inconvénients |
|----------|------|-----------|---------------|
| **EdgeTTSProvider** | Cloud | Gratuit, haute qualité, voix naturelles | Requiert connexion internet |
| **CoquiTTSProvider** | Local | Privacy, offline | Qualité inférieure, lent |

**Architecture**:
```python
class TTSProvider(ABC):
    @abstractmethod
    async def synthesize(text, output_path) -> Path
        # Interface commune

class EdgeTTSProvider(TTSProvider):
    async def synthesize(self, text, output_path):
        # Utilise edge-tts package
        # Voix: fr-FR-DeniseNeural (femme), fr-FR-HenriNeural (homme)
        # Format: MP3 sortie

class CoquiTTSProvider(TTSProvider):
    _model = None  # Singleton

    async def synthesize(self, text, output_path):
        # TTS package local
        # Plus lent mais offline

# Factory function
async def synthesize_speech(text, output_path) -> Path:
    provider = get_tts_provider()  # Based on .env
    return await provider.synthesize(text, output_path)
```

**Configuration (.env)**:
```bash
TTS_PROVIDER=edge-tts               # ou "coqui-tts"
TTS_VOICE=fr-FR-DeniseNeural       # voix Edge TTS
```

**Voix disponibles (Edge TTS)**:
- Français: `fr-FR-DeniseNeural` (femme), `fr-FR-HenriNeural` (homme)
- Anglais: `en-US-AriaNeural`, `en-US-GuyNeural`

---

### 3. Agent Layer (`src/agents/jarvis_agent.py`)

**Responsabilité**: Logique conversationnelle et génération de réponses

**Architecture**:
```python
class JarvisAgent:
    def __init__(self):
        self.llm = self._initialize_llm()
        self.conversation_history = []  # Garde derniers 10 messages

    def _initialize_llm(self):
        # OpenRouter via OpenAI SDK
        return ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            model=os.getenv("LLM_MODEL", "anthropic/claude-3.5-sonnet"),
            temperature=0.7,
            max_tokens=500
        )

    async def chat(self, user_message: str) -> str:
        # 1. Ajouter message utilisateur à l'historique
        # 2. Construire prompt avec system + historique
        # 3. Appel LLM
        # 4. Ajouter réponse à l'historique
        # 5. Retourner réponse

    def clear_history(self):
        # Reset conversation

    def get_history(self) -> list:
        # Retourner historique pour debug/logging

# Singleton
_agent_instance = None
def get_agent() -> JarvisAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = JarvisAgent()
    return _agent_instance
```

**System Prompt**:
```
Tu es Jarvis, un assistant personnel vocal intelligent et amical.
Tu réponds de manière concise et naturelle pour une synthèse vocale.
Tu te souviens des conversations passées et tu aides l'utilisateur
dans ses tâches quotidiennes avec professionnalisme et courtoisie.
```

**Configuration (.env)**:
```bash
OPENROUTER_API_KEY=sk-or-v1-xxx
LLM_MODEL=anthropic/claude-3.5-sonnet
```

**Modèles supportés (OpenRouter)**:
- `anthropic/claude-3.5-sonnet` (défaut, excellent)
- `meta-llama/llama-3.1-70b-instruct` (gratuit)
- `google/gemini-flash-1.5` (rapide, gratuit)
- `openai/gpt-4o`

---

### 4. Knowledge Graph Layer (`src/graph/graphiti_client.py`)

**État**: Implémenté mais **non intégré** au pipeline actuel

**Responsabilité**: Gestion du knowledge graph avec Graphiti

**Architecture**:
```python
class GraphitiClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            uri=os.getenv("NEO4J_URI"),
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
        self.graphiti = Graphiti(
            neo4j_uri=NEO4J_URI,
            neo4j_user=NEO4J_USER,
            neo4j_password=NEO4J_PASSWORD
        )

    async def add_episode(self, text: str, metadata: dict):
        # Ajoute conversation/document au graphe
        # Graphiti extrait automatiquement entités et relations

    async def search(self, query: str, limit: int = 5):
        # Recherche sémantique dans le graphe

    async def close(self):
        # Ferme connexion Neo4j

# Singleton
def get_graphiti_client() -> GraphitiClient:
    # Retourne instance unique
```

**Configuration Graphiti** (`config/graphiti_config.yaml`):
```yaml
database:
  uri: ${NEO4J_URI}
  user: ${NEO4J_USER}
  password: ${NEO4J_PASSWORD}

llm_provider:
  provider: openai
  api_key: ${OPENROUTER_API_KEY}
  base_url: https://openrouter.ai/api/v1
  model: ${LLM_MODEL}

embedder:
  model: text-embedding-3-small
  dimensions: 1536

# TODO: Adapter pour domaine assistant personnel
entity_types:
  - Person
  - Event
  - Task
  - Preference
  - Note
  - Contact

relation_types:
  - KNOWS
  - SCHEDULED
  - PREFERS
  - RELATES_TO
```

**Intégration à faire**:
1. Appeler `add_episode()` après chaque conversation
2. Utiliser `search()` pour enrichir contexte agent
3. Définir schéma entités pour assistant personnel

---

### 5. Frontend Layer (`static/`)

#### 5.1 HTML Interface (`index.html`)

**Features**:
- Design moderne avec gradient background
- Bouton microphone push-to-talk (150x150px)
- Canvas pour waveform visualization
- Status indicator (Idle, Listening, Processing, Speaking)
- Zones d'affichage:
  - Transcription utilisateur
  - Réponse Jarvis
  - Lecteur audio

**Structure**:
```html
<body>
  <header>
    <h1>🤖 Jarvis</h1>
    <div id="status">Idle</div>
  </header>

  <main>
    <canvas id="waveform"></canvas>

    <button id="recordButton" class="mic-button">
      🎤
    </button>

    <div id="transcription"></div>
    <div id="response"></div>
    <audio id="audioPlayer"></audio>
    <div id="error"></div>
  </main>

  <script src="/static/app.js"></script>
</body>
```

#### 5.2 JavaScript Logic (`app.js`)

**Features**:
```javascript
// État global
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let audioContext = null;
let analyser = null;

// Initialisation
async function initAudio() {
  // Demande permission microphone
  // Crée MediaRecorder avec WebM 16kHz mono
  // Configure echo cancellation + noise suppression
}

// Recording
recordButton.addEventListener('mousedown', startRecording);
recordButton.addEventListener('mouseup', stopRecording);
recordButton.addEventListener('touchstart', startRecording);
recordButton.addEventListener('touchend', stopRecording);

async function startRecording() {
  // Démarre capture audio
  // Lance visualisation waveform
  // Update status: "Listening..."
}

async function stopRecording() {
  // Arrête capture
  // Construit blob WebM
  // Upload vers /api/voice/process
  // Update status: "Processing..."
}

// Visualisation
function drawWaveform() {
  // Canvas animation loop
  // Dessine waveform temps réel
  requestAnimationFrame(drawWaveform);
}

// Traitement réponse
async function processVoice(audioBlob) {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');

  const response = await fetch('/api/voice/process', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();

  // Afficher transcription et réponse
  // Jouer audio
  audioPlayer.src = data.audio_url;
  audioPlayer.play();
}
```

**Configuration Audio**:
```javascript
const constraints = {
  audio: {
    channelCount: 1,        // Mono
    sampleRate: 16000,      // 16kHz
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true
  }
};
```

---

## Pipeline de Traitement

### Flow Complet (Opérationnel)

```
1. USER ACTION
   └─> Maintenir bouton microphone

2. FRONTEND CAPTURE
   └─> MediaRecorder start
   └─> Visualisation waveform
   └─> Status: "Listening..."

3. USER ACTION
   └─> Relâcher bouton

4. FRONTEND PROCESSING
   └─> MediaRecorder stop
   └─> Créer blob WebM
   └─> POST /api/voice/process
   └─> Status: "Processing..."

5. BACKEND: STT PROCESSING
   └─> Sauvegarder fichier temporaire
   └─> Charger provider STT (Whisper)
   └─> Convertir WebM → WAV (ffmpeg)
   └─> Transcription → texte français
   └─> Log: "Transcription: {text}"

6. BACKEND: AGENT PROCESSING
   └─> Charger agent (singleton)
   └─> Ajouter message à historique
   └─> Construire prompt (system + history)
   └─> Appel OpenRouter/Claude
   └─> Recevoir réponse
   └─> Log: "Agent response: {response}"

7. BACKEND: TTS PROCESSING
   └─> Charger provider TTS (Edge TTS)
   └─> Synthèse texte → MP3
   └─> Sauvegarder dans /static/response_{uuid}.mp3
   └─> Log: "Audio response: {url}"

8. BACKEND: RESPONSE
   └─> Retourner JSON:
       {
         "success": true,
         "transcription": "...",
         "response": "...",
         "audio_url": "/static/response_xxx.mp3"
       }
   └─> Nettoyer fichier input temporaire

9. FRONTEND: DISPLAY
   └─> Afficher transcription
   └─> Afficher réponse texte
   └─> Charger audio player
   └─> Auto-play réponse
   └─> Status: "Speaking..."

10. FRONTEND: COMPLETE
    └─> Audio terminé
    └─> Status: "Idle"
    └─> Prêt pour nouvelle interaction
```

**Temps de traitement typique**:
- Capture audio: 2-5 secondes (durée utilisateur)
- Upload: <1 seconde
- STT (Whisper base): 2-4 secondes
- Agent (Claude): 1-2 secondes
- TTS (Edge): 1-2 secondes
- **Total**: ~5-10 secondes

---

## Flux de Données

### Formats de Données

**Audio Input (Frontend → Backend)**:
```
Format: WebM Opus
Sample Rate: 16kHz
Channels: Mono (1)
Duration: Variable (user input)
Size: ~10KB/seconde
```

**Transcription (STT → Agent)**:
```json
{
  "text": "Bonjour Jarvis, quelle heure est-il ?",
  "language": "fr",
  "confidence": 0.95
}
```

**Agent Response (Agent → TTS)**:
```json
{
  "response": "Il est actuellement 14h30. Comment puis-je vous aider ?",
  "model": "anthropic/claude-3.5-sonnet",
  "tokens_used": 45
}
```

**Audio Output (Backend → Frontend)**:
```
Format: MP3
Sample Rate: 24kHz
Channels: Mono (1)
Bitrate: 48kbps
URL: /static/response_abc12345.mp3
```

**API Response (Backend → Frontend)**:
```json
{
  "success": true,
  "transcription": "Bonjour Jarvis, quelle heure est-il ?",
  "response": "Il est actuellement 14h30...",
  "audio_url": "/static/response_abc12345.mp3",
  "processing_time_ms": 6432
}
```

---

## Implémentation Actuelle

### Modules Complets ✅

| Module | Fichier | Lignes | Tests | Documentation |
|--------|---------|--------|-------|---------------|
| API FastAPI | `src/api/main.py` | 188 | ❌ | ✅ |
| STT Provider | `src/voice/stt.py` | 177 | ❌ | ✅ |
| TTS Provider | `src/voice/tts.py` | 161 | ❌ | ✅ |
| Agent | `src/agents/jarvis_agent.py` | 144 | ❌ | ✅ |
| Graphiti Client | `src/graph/graphiti_client.py` | 170 | ⚠️ | ✅ |
| Web Interface | `static/index.html` | 244 | N/A | ✅ |
| Frontend JS | `static/app.js` | 237 | N/A | ✅ |

**Total code fonctionnel**: ~1321 lignes

---

## Modules À Implémenter

### Phase 4: Knowledge Graph Integration

**1. Entity Models** (`src/models/entities.py`)
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class Person(BaseModel):
    name: str
    relationship: Optional[str]
    notes: Optional[str]

class Event(BaseModel):
    title: str
    date: datetime
    location: Optional[str]
    participants: List[str]

class Task(BaseModel):
    description: str
    due_date: Optional[datetime]
    priority: str  # low, medium, high
    completed: bool = False

class Preference(BaseModel):
    category: str  # food, music, etc.
    item: str
    strength: float  # 0-1

class Note(BaseModel):
    content: str
    tags: List[str]
    created_at: datetime
```

**2. Entity Extraction** (`src/rag/entity_extractor.py`)
```python
class EntityExtractor:
    def __init__(self, llm):
        self.llm = llm

    async def extract_entities(self, conversation: str) -> dict:
        # Utilise LLM pour extraire entités structurées
        # Retourne dict avec Person, Event, Task, etc.

    async def extract_preferences(self, text: str) -> List[Preference]:
        # Détecte préférences utilisateur

    async def extract_tasks(self, text: str) -> List[Task]:
        # Détecte tâches à faire
```

**3. GraphRAG Implementation** (`src/rag/graphrag.py`)
```python
class GraphRAG:
    def __init__(self, graphiti_client, llm):
        self.graph = graphiti_client
        self.llm = llm

    async def enrich_context(self, user_query: str) -> str:
        # 1. Recherche sémantique dans graphe
        results = await self.graph.search(user_query, limit=5)

        # 2. Construire contexte enrichi
        context = self._build_context(results)

        # 3. Retourner pour injection dans agent prompt
        return context

    async def update_graph(self, conversation: str, entities: dict):
        # Mise à jour graphe avec nouvelles infos
        await self.graph.add_episode(conversation, entities)
```

**4. Integration dans Pipeline** (`src/api/main.py`)
```python
@app.post("/api/voice/process")
async def process_voice(audio: UploadFile):
    # ... STT ...

    # GraphRAG enrichment
    graphrag = get_graphrag()
    context = await graphrag.enrich_context(transcription)

    # Agent avec contexte enrichi
    agent = get_agent()
    response = await agent.chat(transcription, context=context)

    # ... TTS ...

    # Update knowledge graph
    entities = await extract_entities(transcription, response)
    await graphrag.update_graph(
        f"User: {transcription}\nJarvis: {response}",
        entities
    )

    # ... return ...
```

---

### Phase 5: ESP32 Hardware

**Firmware Architecture** (`esp32/src/main.cpp`)
```cpp
// 1. Wake Word Detection
void detectWakeWord() {
  // Porcupine ou Edge Impulse
  // Détecte "Hey Jarvis"
}

// 2. Audio Capture
void captureAudio() {
  // I2S microphone INMP441
  // Buffer audio 16kHz mono
}

// 3. WiFi Upload
void uploadAudio(uint8_t* buffer, size_t length) {
  // HTTP POST vers /api/voice/process
  // Multipart/form-data
}

// 4. Download & Play Response
void playResponse(String audioUrl) {
  // HTTP GET audio MP3
  // I2S speaker MAX98357A
}

// Main loop
void loop() {
  if (detectWakeWord()) {
    ledOn();
    captureAudio();
    uploadAudio();
    playResponse();
    ledOff();
  }
}
```

---

## Décisions Architecturales

### 1. Pourquoi Singleton Pattern ?

**Raison**: Éviter de charger modèles lourds (Whisper, TTS) à chaque requête

**Impact**: Première requête lente (~10s), suivantes rapides (~5s)

**Alternative**: Pool de workers pré-chargés (plus complexe)

---

### 2. Pourquoi OpenRouter ?

**Raison**: Accès à 100+ modèles via une seule API

**Avantages**:
- Switch entre Claude, GPT-4, Llama sans changer code
- Meilleurs prix (routing automatique)
- Pas de vendor lock-in

**Alternative**: Anthropic API direct, OpenAI direct (moins flexible)

---

### 3. Pourquoi FastAPI ?

**Raison**: Framework async moderne, documentation auto, performances

**Avantages**:
- Async/await natif (important pour I/O)
- Auto-génération OpenAPI docs
- Type hints Pydantic
- WebSocket support pour futur streaming

**Alternative**: Flask (sync, moins performant), Django (trop lourd)

---

### 4. Pourquoi Neo4j + Graphiti ?

**Raison**: Knowledge graph dynamique avec extraction auto

**Avantages Neo4j**:
- Graph database mature et performante
- Cypher query language puissant
- Visualisation graphe intégrée

**Avantages Graphiti**:
- Extraction entités automatique via LLM
- Gestion relations temporelles
- API simple

**Alternative**:
- PostgreSQL + pgvector (moins adapté aux relations)
- Custom graph implementation (réinventer la roue)

---

### 5. Pourquoi Whisper Local vs Cloud STT ?

**Raison**: Privacy + coût zéro

**Trade-offs**:
| | Whisper Local | Google STT | Groq |
|-|---------------|------------|------|
| **Coût** | Gratuit | $0.006/15s | Gratuit |
| **Privacy** | ✅ Total | ❌ Cloud | ❌ Cloud |
| **Vitesse** | ⚠️ Lent (CPU) | ✅ Rapide | ✅ Très rapide |
| **Qualité** | ✅ Excellent | ✅ Excellent | ✅ Excellent |
| **Offline** | ✅ Oui | ❌ Non | ❌ Non |

**Décision**: Local par défaut, Groq en option

---

### 6. Pourquoi Docker ?

**Raison**: Environnement reproductible, déploiement simplifié

**Avantages**:
- Même environnement dev/prod
- Isolation dépendances système (ffmpeg, etc.)
- Neo4j containerisé
- Scaling facile (futur: docker swarm, k8s)

**Alternative**:
- Virtualenv (problèmes dépendances système)
- Installation manuelle (non reproductible)

---

## Prochaines Étapes Techniques

### Priorité 1: GraphRAG Integration (Phase 4)

1. Créer `src/models/entities.py` avec Pydantic models
2. Implémenter `src/rag/entity_extractor.py`
3. Intégrer extraction dans `/api/voice/process`
4. Tester mise à jour automatique graphe
5. Implémenter recherche sémantique pour enrichir contexte agent

**Estimation**: 2-3 jours de développement

---

### Priorité 2: Tests (Phase 4)

1. Tests unitaires pour chaque provider (STT, TTS, Agent)
2. Tests d'intégration pipeline complet
3. Tests Graphiti (connexion, add_episode, search)
4. Mock LLM pour tests rapides
5. CI/CD GitHub Actions

**Estimation**: 1-2 jours

---

### Priorité 3: ESP32 (Phase 5)

*Attend réception matériel*

1. Setup PlatformIO
2. Test microphone I2S
3. Test speaker I2S
4. Implémentation wake word (Porcupine)
5. Communication WiFi avec backend
6. Optimisation latence

**Estimation**: 1 semaine après réception matériel

---

**Document maintenu à jour au fur et à mesure du développement**
