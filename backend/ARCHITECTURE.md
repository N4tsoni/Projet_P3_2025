# Architecture Backend - Jarvis Voice Assistant

> Documentation de l'architecture Layered du backend FastAPI

---

## 📐 Vue d'Ensemble

Le backend Jarvis suit une **Layered Architecture** (architecture en couches) qui sépare clairement les responsabilités :

```
┌─────────────────────────────────────────┐
│         API Layer (Routes)              │  ← Endpoints HTTP
├─────────────────────────────────────────┤
│      Business Logic (Services)          │  ← Logique métier
├─────────────────────────────────────────┤
│      Domain Logic (voice, agents...)    │  ← Modules métier
├─────────────────────────────────────────┤
│         Data Layer (Neo4j, etc.)        │  ← Persistance
└─────────────────────────────────────────┘
```

**Avantages** :
- ✅ Séparation des responsabilités (SoC)
- ✅ Testabilité accrue
- ✅ Maintenabilité améliorée
- ✅ Évolutivité facilitée

---

## 🗂️ Structure du Projet

```
backend/src/
├── api/                    # API Layer
│   ├── routes/            # Endpoints FastAPI
│   │   ├── voice.py       # Routes vocales (/api/voice/*)
│   │   ├── knowledge.py   # Routes knowledge graph (/api/knowledge/*)
│   │   └── health.py      # Health checks
│   ├── dependencies.py    # FastAPI dependencies (à créer si besoin)
│   └── main.py           # Application FastAPI (setup only)
│
├── services/              # Business Logic Layer
│   ├── voice_service.py   # Pipeline vocal (STT → Agent → TTS)
│   ├── graph_service.py   # Opérations knowledge graph
│   └── __init__.py
│
├── models/                # Data Models
│   ├── requests.py        # Pydantic request models
│   ├── responses.py       # Pydantic response models
│   └── code_entities.py   # (existant) Entités de code
│
├── core/                  # Configuration & Core
│   ├── config.py          # Settings centralisées
│   └── __init__.py
│
├── voice/                 # Domain Logic (inchangé)
│   ├── stt.py            # Speech-to-Text
│   └── tts.py            # Text-to-Speech
│
├── agents/                # Domain Logic (inchangé)
│   └── jarvis_agent.py   # Agent conversationnel
│
├── graph/                 # Domain Logic (inchangé)
│   └── graphiti_client.py # Client Graphiti
│
└── code_analysis/         # Domain Logic (inchangé)
    └── ...               # Analyseur de code Python
```

---

## 🔄 Flow de Requête

### Exemple : Traitement Vocal

```
1. Client (Frontend)
   ↓ POST /api/voice/process (audio file)

2. API Layer (routes/voice.py)
   ├─ Validation de la requête
   └─ Appel au service
      ↓

3. Service Layer (voice_service.py)
   ├─ Orchestration du pipeline:
   │  ├─ 1. Sauvegarde audio temporaire
   │  ├─ 2. STT (voice/stt.py) → transcription
   │  ├─ 3. Agent (agents/jarvis_agent.py) → réponse
   │  ├─ 4. TTS (voice/tts.py) → audio
   │  └─ 5. Nettoyage fichiers temporaires
   └─ Retour (transcription, response, audio_url)
      ↓

4. API Layer
   └─ Formatage response Pydantic
      ↓

5. Client
   └─ JSON response + audio URL
```

---

## 📦 Couches Détaillées

### **1. API Layer** (`api/`)

**Responsabilité** : Gérer les requêtes HTTP, validation, et formatage des réponses.

**Fichiers** :
- `routes/voice.py` - Endpoints vocaux
- `routes/knowledge.py` - Endpoints knowledge graph
- `routes/health.py` - Health checks
- `main.py` - Setup de l'application FastAPI

**Caractéristiques** :
- Routes déclaratives avec FastAPI
- Validation automatique via Pydantic
- Documentation auto-générée (Swagger/OpenAPI)
- Gestion des erreurs HTTP

**Exemple** :
```python
@router.post("/process", response_model=VoiceProcessResponse)
async def process_voice(audio: UploadFile = File(...)):
    voice_service = get_voice_service()
    transcription, response, audio_url = await voice_service.process_voice_input(audio)
    return VoiceProcessResponse(...)
```

---

### **2. Service Layer** (`services/`)

**Responsabilité** : Logique métier et orchestration des opérations.

**Fichiers** :
- `voice_service.py` - Pipeline vocal complet
- `graph_service.py` - Opérations sur le knowledge graph

**Caractéristiques** :
- Logique métier isolée des routes
- Orchestration de plusieurs modules domain
- Gestion des transactions et du flow
- Réutilisable et testable indépendamment

**Exemple** :
```python
class VoiceService:
    async def process_voice_input(self, audio_file):
        # 1. Save audio
        audio_path = await self._save_audio_file(audio_file)
        # 2. STT
        transcription = await self._transcribe(audio_path)
        # 3. Agent
        response = await self._process_with_agent(transcription)
        # 4. TTS
        audio_url = await self._synthesize_response(response)
        return transcription, response, audio_url
```

---

### **3. Domain Layer** (`voice/`, `agents/`, `graph/`)

**Responsabilité** : Logique métier spécifique à un domaine (STT, TTS, Agent, Graph).

**Fichiers** :
- `voice/stt.py` - Transcription audio (Whisper, Groq)
- `voice/tts.py` - Synthèse vocale (Edge TTS)
- `agents/jarvis_agent.py` - Agent conversationnel (OpenRouter)
- `graph/graphiti_client.py` - Client Graphiti pour Neo4j

**Caractéristiques** :
- Modules indépendants et réutilisables
- Logique pure (pas de dépendance FastAPI)
- Testable unitairement
- Peut être utilisé en dehors de l'API (CLI, notebooks, etc.)

---

### **4. Models Layer** (`models/`)

**Responsabilité** : Définition des structures de données (DTO).

**Fichiers** :
- `requests.py` - Modèles de requêtes Pydantic
- `responses.py` - Modèles de réponses Pydantic

**Caractéristiques** :
- Validation automatique des données
- Documentation des schémas
- Typage fort avec Python type hints
- Sérialisation/désérialisation automatique

**Exemple** :
```python
class VoiceProcessResponse(BaseModel):
    success: bool
    transcription: str
    response: str
    audio_url: str
```

---

### **5. Core Layer** (`core/`)

**Responsabilité** : Configuration et utilitaires centraux.

**Fichiers** :
- `config.py` - Settings centralisées (Pydantic Settings)

**Caractéristiques** :
- Configuration centralisée via `.env`
- Singleton pattern pour les settings
- Validation des variables d'environnement
- Création automatique des dossiers nécessaires

**Exemple** :
```python
settings = get_settings()
print(settings.stt_provider)  # "groq"
print(settings.neo4j_uri)      # "bolt://neo4j:7687"
```

---

## 🧪 Testing Strategy

### Tests Unitaires
- **Services** : Mocker les appels aux modules domain
- **Domain modules** : Tests isolés (STT, TTS, Agent)
- **Models** : Validation Pydantic

### Tests d'Intégration
- **Routes** : TestClient FastAPI
- **Pipeline complet** : End-to-end avec vrais services

### Exemple :
```python
# Test service
async def test_voice_service():
    service = VoiceService()
    # Mock dependencies
    with patch('src.voice.stt.transcribe_audio') as mock_stt:
        mock_stt.return_value = "Bonjour"
        result = await service.process_voice_input(mock_audio)
        assert result[0] == "Bonjour"
```

---

## 🔧 Bonnes Pratiques

### 1. **Dependency Injection**
Utiliser les singletons pattern avec `get_*` functions :
```python
voice_service = get_voice_service()
```

### 2. **Separation of Concerns**
- Routes → Validation HTTP
- Services → Logique métier
- Domain → Logique technique spécifique

### 3. **Error Handling**
- Services lèvent des exceptions Python
- Routes convertissent en HTTPException

### 4. **Logging**
- Loguru pour logs structurés
- Logs à tous les niveaux (Route, Service, Domain)

### 5. **Type Hints**
- Utiliser les type hints partout
- Pydantic pour validation runtime

---

## 🚀 Évolutions Futures

### Phase 1 (Actuel)
- ✅ Refactoring en Layered Architecture
- ✅ Séparation routes/services/domain
- ✅ Configuration centralisée

### Phase 2 (Court terme)
- [ ] Tests unitaires et d'intégration
- [ ] Repository pattern pour Neo4j
- [ ] Async context managers pour ressources

### Phase 3 (Moyen terme)
- [ ] Dependency injection avec FastAPI Depends
- [ ] Event-driven architecture pour knowledge graph
- [ ] Background tasks pour opérations longues

### Phase 4 (Long terme)
- [ ] Microservices (si nécessaire)
- [ ] CQRS pattern pour knowledge graph
- [ ] Event sourcing

---

## 📚 Ressources

### Documentation
- [FastAPI Best Practices](https://fastapi.tiangolo.com/advanced/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/usage/pydantic_settings/)
- [Layered Architecture](https://en.wikipedia.org/wiki/Multitier_architecture)

### Code Examples
- Voir `src/services/voice_service.py` pour un exemple complet
- Voir `src/api/routes/voice.py` pour les routes
- Voir `src/core/config.py` pour la configuration

---

**Dernière mise à jour** : 2026-01-06
**Version** : 1.0
**Auteur** : Refactoring Jarvis Backend
