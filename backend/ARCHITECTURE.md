# Architecture Backend - Jarvis Voice Assistant

## 📐 Vue d'Ensemble

Le backend utilise une **architecture MVC modulaire** avec séparation claire des responsabilités.

```
FastAPI Request
     ↓
Middlewares (CORS, Error Handling, Logging)
     ↓
Routes (API Endpoints)
     ↓
Controllers (Business Logic Orchestration)
     ↓
Services (Core Business Logic)
     ↓
Repositories/Agents (Data Access / External APIs)
```

## 📁 Structure des Dossiers

```
backend/src/
├── app.py                      # Point d'entrée FastAPI (Application Factory)
├── main_new.py                 # Entry point Uvicorn
│
├── core/                       # Configuration et utilitaires core
│   ├── config.py              # Settings (Pydantic Settings)
│   └── logging.py             # Configuration Loguru
│
├── middlewares/               # Middlewares FastAPI
│   ├── cors.py               # Configuration CORS
│   └── error_handler.py      # Gestion globale des erreurs
│
├── api/                      # Layer API
│   └── routes/              # Routes FastAPI (Routers)
│       ├── health.py        # Health check endpoints
│       ├── voice.py         # Voice processing endpoints
│       └── knowledge.py     # Knowledge graph endpoints
│
├── controllers/             # Contrôleurs (Orchestration)
│   ├── health_controller.py
│   ├── voice_controller.py
│   └── knowledge_controller.py
│
├── services/               # Services (Business Logic)
│   ├── voice/
│   │   ├── stt_service.py  # Speech-to-Text
│   │   └── tts_service.py  # Text-to-Speech
│   ├── agent_service.py    # Agent conversationnel
│   └── knowledge_service.py # Knowledge graph
│
├── schemas/               # Pydantic Schemas (Request/Response)
│   ├── health.py
│   ├── voice.py
│   └── knowledge.py
│
├── models/               # Domain Models
│   └── (à venir)
│
├── repositories/        # Data Access Layer
│   └── (à venir)
│
├── agents/             # AI Agents
│   └── jarvis_agent.py
│
├── graph/              # GraphRAG
│   └── graphiti_client.py
│
└── utils/             # Utilitaires
    └── (à venir)
```

## 🏗️ Layers Architecture

### 1. Core Layer
**Responsabilité**: Configuration et utilitaires fondamentaux

- **config.py**: Centralise toute la configuration avec Pydantic Settings
  - Variables d'environnement
  - Settings de l'application
  - Configuration LLM, STT, TTS, Neo4j

- **logging.py**: Configuration du système de logging avec Loguru
  - Format personnalisé
  - Logs console et fichiers
  - Niveaux de log configurables

### 2. Middlewares Layer
**Responsabilité**: Traitement transversal des requêtes

- **cors.py**: Configuration CORS pour le frontend
- **error_handler.py**: Gestion globale et centralisée des erreurs
  - Validation errors (422)
  - Server errors (500)
  - Logging des exceptions

### 3. API Layer (Routes)
**Responsabilité**: Définition des endpoints et validation des entrées

- Définit les routes HTTP
- Utilise FastAPI Router
- Injecte les dépendances (Controllers via Depends)
- Retourne des réponses typées (Pydantic schemas)

**Exemple:**
```python
@router.post("/api/voice/process", response_model=VoiceProcessResponse)
async def process_voice(
    audio: UploadFile = File(...),
    controller: VoiceController = Depends(get_voice_controller)
):
    return await controller.process_voice(audio)
```

### 4. Controllers Layer
**Responsabilité**: Orchestration de la logique métier

- Coordonne l'appel de plusieurs services
- Gère le flux de traitement
- Transforme les données entre layers
- Gestion des erreurs métier

**Pattern Singleton**: Un seul controller par type

**Exemple:**
```python
class VoiceController:
    def __init__(self):
        self.stt_service = get_stt_service()
        self.tts_service = get_tts_service()
        self.agent_service = get_agent_service()

    async def process_voice(self, audio):
        # 1. STT
        transcription = await self.stt_service.transcribe(...)
        # 2. Agent
        response = await self.agent_service.process_message(...)
        # 3. TTS
        audio_url = await self.tts_service.synthesize(...)
        return VoiceProcessResponse(...)
```

### 5. Services Layer
**Responsabilité**: Logique métier core

- **Encapsule** la logique métier réutilisable
- **Indépendant** des détails HTTP/API
- **Testable** facilement
- **Singleton pattern** pour performance

**Services disponibles:**
- `stt_service.py`: Speech-to-Text (Whisper/Groq)
- `tts_service.py`: Text-to-Speech (Edge TTS/Coqui)
- `agent_service.py`: Gestion de l'agent Jarvis
- `knowledge_service.py`: Operations knowledge graph

### 6. Schemas Layer
**Responsabilité**: Validation et sérialisation des données

- **Pydantic Models** pour request/response
- Validation automatique
- Documentation OpenAPI automatique
- Type safety

**Types de schemas:**
- Request models (entrées API)
- Response models (sorties API)
- Domain models (entités métier)

### 7. Agents & Graph Layer
**Responsabilité**: Intelligence artificielle et données

- **agents/**: Agents conversationnels (Jarvis)
- **graph/**: GraphRAG et Graphiti
- **repositories/**: Accès données (Neo4j, etc.)

## 🔄 Flow d'une Requête

### Exemple: Process Voice

```
1. Client → POST /api/voice/process (audio file)
   ↓
2. Middlewares (CORS, Logging)
   ↓
3. Route: voice.py → process_voice()
   ↓
4. Controller: voice_controller.py → process_voice()
   ├─→ 4a. STT Service → transcribe()
   ├─→ 4b. Agent Service → process_message()
   └─→ 4c. TTS Service → synthesize()
   ↓
5. Return: VoiceProcessResponse
   ↓
6. Middlewares (Error Handling, Logging)
   ↓
7. Client ← JSON Response + Audio URL
```

## 🎯 Principes de Design

### 1. Separation of Concerns
Chaque layer a une responsabilité unique et claire.

### 2. Dependency Injection
Utilise FastAPI `Depends()` pour injection de dépendances.

### 3. Singleton Pattern
Services et controllers sont des singletons pour:
- Performance (modèles ML chargés une fois)
- State management (conversation history)
- Resource optimization

### 4. Type Safety
Utilise Pydantic et type hints partout:
```python
async def process_voice(self, audio: UploadFile) -> VoiceProcessResponse:
```

### 5. Error Handling
- Errors locales dans services/controllers
- Error handler global dans middleware
- Logging systématique

### 6. Configuration Centralisée
Toute la config dans `core/config.py`:
```python
settings = get_settings()
settings.OPENROUTER_API_KEY
settings.STT_PROVIDER
```

## 📝 Conventions de Code

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case()`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

### Structure d'un Module

```python
"""
Module docstring explaining purpose.
"""
# 1. Imports (grouped: stdlib, third-party, local)
import os
from typing import Optional

from fastapi import APIRouter
from loguru import logger

from src.schemas.voice import VoiceResponse
from src.services.stt_service import get_stt_service

# 2. Constants
DEFAULT_LANGUAGE = "fr"

# 3. Classes/Functions
class VoiceController:
    """Controller docstring."""

    def __init__(self):
        """Init docstring."""
        pass

# 4. Singleton/Factory Functions
_controller: Optional[VoiceController] = None

def get_voice_controller() -> VoiceController:
    """Get singleton instance."""
    global _controller
    if _controller is None:
        _controller = VoiceController()
    return _controller
```

### Docstrings

Utiliser Google style:

```python
async def process_voice(self, audio: UploadFile) -> VoiceProcessResponse:
    """
    Process voice input through STT -> Agent -> TTS pipeline.

    Args:
        audio: Uploaded audio file

    Returns:
        VoiceProcessResponse with transcription, response, and audio URL

    Raises:
        ValueError: If audio format is invalid
    """
```

## 🧪 Testing Strategy

### Unit Tests
- Tester chaque service indépendamment
- Mock dependencies
- Path: `tests/unit/services/`

### Integration Tests
- Tester controllers avec vrais services
- Path: `tests/integration/controllers/`

### API Tests
- Tester endpoints complets
- Path: `tests/api/`

## 🚀 Extensibilité

### Ajouter un Nouveau Endpoint

1. **Créer le schema** dans `schemas/`
```python
# schemas/new_feature.py
class NewFeatureRequest(BaseModel):
    param: str

class NewFeatureResponse(BaseModel):
    result: str
```

2. **Créer le service** dans `services/`
```python
# services/new_feature_service.py
class NewFeatureService:
    async def process(self, param: str) -> str:
        # Business logic
        return result
```

3. **Créer le controller** dans `controllers/`
```python
# controllers/new_feature_controller.py
class NewFeatureController:
    def __init__(self):
        self.service = get_new_feature_service()

    async def handle(self, request: NewFeatureRequest):
        result = await self.service.process(request.param)
        return NewFeatureResponse(result=result)
```

4. **Créer la route** dans `api/routes/`
```python
# api/routes/new_feature.py
router = APIRouter(prefix="/api/new-feature", tags=["NewFeature"])

@router.post("/", response_model=NewFeatureResponse)
async def new_feature_endpoint(
    request: NewFeatureRequest,
    controller = Depends(get_new_feature_controller)
):
    return await controller.handle(request)
```

5. **Inclure le router** dans `app.py`
```python
from src.api.routes import new_feature
app.include_router(new_feature.router)
```

## 📊 État Actuel

### ✅ Implémenté
- ✅ Architecture MVC complète
- ✅ Configuration centralisée (Pydantic Settings)
- ✅ Logging structuré (Loguru)
- ✅ Middlewares (CORS, Error Handling)
- ✅ Health checks
- ✅ Voice processing (STT, Agent, TTS)
- ✅ Knowledge graph endpoints (structure)
- ✅ Dependency injection
- ✅ Type safety (Pydantic + Type hints)

### 🔜 À Implémenter
- [ ] Repositories pour Neo4j
- [ ] Models pour entités métier
- [ ] Utils (file, audio, etc.)
- [ ] Tests unitaires et intégration
- [ ] GraphRAG complet
- [ ] Authentification/Authorization
- [ ] Rate limiting
- [ ] Caching
- [ ] Monitoring/Metrics

## 🔗 Ressources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Loguru](https://loguru.readthedocs.io/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
