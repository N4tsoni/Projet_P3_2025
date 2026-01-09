# CLAUDE.md

Instructions pour Claude Code lors du travail sur ce projet.

---

## Vue d'Ensemble du Projet

**Jarvis** - Assistant vocal intelligent avec knowledge graph dynamique utilisant un pipeline d'agents IA (Claude) et Neo4j.

### Architecture

**Frontend:**
- Vue.js 3 + TypeScript + Vite
- Element Plus pour UI
- Atomic Design pattern
- Port: 5173

**Backend:**
- FastAPI + Python 3.11
- Groq Whisper large-v3 (STT)
- Edge TTS (synthèse vocale gratuite)
- OpenRouter (LLM - Claude 3.5 Sonnet)
- Pipeline KG avec agents IA + Neo4j
- PostgreSQL (conversations)
- Port: 8000

**Infrastructure:**
- Docker + Docker Compose (4 services)
- Poetry pour dépendances Python
- Neo4j sur port 7474/7687
- PostgreSQL sur port 5432

### Technologies Clés

- **STT**: Groq Whisper large-v3 (rapide et gratuit)
- **TTS**: Edge TTS Microsoft (voix fr-FR-DeniseNeural)
- **LLM**: OpenRouter - Claude 3.5 Sonnet (agent principal)
- **Knowledge Graph**: Pipeline d'agents IA + Neo4j (sans Graphiti)
- **Pipeline Vocal**: Audio → Groq STT → Agent → Edge TTS → Audio
- **Pipeline KG**: Document → Parser → Entity Extractor → Relation Extractor → Neo4j

---

## État Actuel

### ✅ Opérationnel (Phases 1-5)

**Pipeline Vocal:**
- Pipeline vocal complet fonctionnel
- Interface Vue.js moderne avec glassmorphism
- Enregistrement push-to-talk avec visualisation audio
- Historique des conversations (PostgreSQL)
- API REST complète
- Docker Compose avec 4 services

**Knowledge Graph Builder (NOUVEAU - Phase 5):**
- Pipeline d'agents IA pour extraction entités/relations
- Interface KG Builder (upload, stats, graph viewer)
- Support CSV (JSON, PDF, TXT à venir)
- Neo4j direct (sans Graphiti Enterprise)
- Gestion idempotente des duplicates (MERGE)
- 5 stages: Parsing → Extraction → Validation → Storage

### 🔄 En Développement (Phase 6)

- Graph viewer interactif visuel (D3.js/vis.js)
- Support multi-formats (JSON, PDF, TXT)
- GraphRAG: intégration KG dans contexte conversationnel
- Enrichissement automatique via LLM

### 📦 Planifié (Phase 7+)

- Firmware ESP32 (matériel en commande)
- Wake word detection ("Hey Jarvis")
- Mémoire conversationnelle enrichie par KG

---

## Structure du Projet

```
Projet_P3/
├── frontend/          # Vue.js 3 + TypeScript
│   ├── src/
│   │   ├── components/    # Atomic Design
│   │   ├── stores/        # Pinia
│   │   ├── services/      # API client
│   │   └── types/         # TypeScript
│   └── Dockerfile
│
├── backend/           # FastAPI
│   ├── src/
│   │   ├── api/          # Routes REST
│   │   ├── agents/       # jarvis_agent.py
│   │   ├── voice/        # stt.py + tts.py
│   │   ├── kg/           # Knowledge Graph Pipeline (NOUVEAU)
│   │   │   ├── agents/       # Entity/Relation extractors
│   │   │   ├── services/     # Neo4j, Orchestrator
│   │   │   ├── models/       # Entity, Relation, Document
│   │   │   ├── parsers/      # CSV, JSON, PDF, TXT
│   │   │   └── pipeline/     # Stages et Pipeline
│   │   ├── services/     # Voice, Conversation services
│   │   ├── repositories/ # Data access layer
│   │   └── models/       # Pydantic models
│   ├── config/
│   ├── data/
│   └── Dockerfile
│
├── esp32/             # Firmware (à développer)
├── docs/              # Documentation
├── docker-compose.yml
├── Makefile
└── TODO.md           # État et prochaines étapes
```

---

## Commandes Essentielles

### Démarrage
```bash
make build    # Build Docker images
make up       # Lancer tous les services
make down     # Arrêter
make logs     # Voir logs
```

### Accès Services
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Neo4j: http://localhost:7474

### Développement
```bash
# Backend - Ajouter dépendance
docker-compose exec backend poetry add package-name

# Backend - Tests
docker-compose exec backend poetry run pytest

# Frontend
cd frontend && npm install && npm run dev
```

---

## Directives de Développement

### Principes

1. **Modularité**: Chaque composant (STT, TTS, Agent, Graph) est indépendant
2. **Async-first**: Utiliser async/await pour I/O
3. **Type safety**: TypeScript frontend, Pydantic backend
4. **Configuration centralisée**: `.env` pour backend
5. **Atomic Design**: Frontend organisé en atoms → molecules → organisms → templates

### Code Backend

- Utiliser **FastAPI** pour nouveaux endpoints
- **Pydantic** pour validation de données
- **Loguru** pour logging
- Services vocaux dans `src/voice/`
- Agent conversationnel dans `src/agents/`
- Code analysis dans `src/code_analysis/`

### Code Frontend

- **Vue 3 Composition API** + `<script setup>`
- **TypeScript** strict
- **Pinia** pour state management
- **Element Plus** pour composants UI
- Atomic Design dans `src/components/`

### Knowledge Graph Builder

- **Pipeline d'agents IA** (sans Graphiti - nécessite Neo4j Enterprise)
- **Neo4j Community** comme backend de graphe
- **Agents Claude** pour extraction intelligente
- Types d'entités: Person, Organization, Movie, Studio, Location, Concept, Generic
- Types de relations: ACTED_IN, DIRECTED, PRODUCED_BY, WORKS_AT, KNOWS, RELATED_TO, LOCATED_IN, PART_OF
- Code dans `backend/src/kg/`
- Idempotent: MERGE pour éviter duplicates

---

## Workflow de Développement

### Ajout de Fonctionnalités

1. Vérifier TODO.md pour contexte
2. Développer de manière modulaire
3. Tester chaque composant
4. Mettre à jour documentation si nécessaire

### Tests

- Tests unitaires avec pytest (backend)
- Tests d'intégration pour pipeline complet
- Validation manuelle via interface web

### Configuration

- `.env` backend: clés API, modèles, configurations
- Pas de secrets dans le code versioned
- `.env.example` comme template

---

## Points d'Attention

### Performance

- Whisper local peut être lent (modèle "tiny" ou "base" recommandé)
- Edge TTS rapide et gratuit
- Objectif latence totale: < 3s end-to-end

### Sécurité

- Clés API dans `.env` uniquement
- CORS configuré pour développement local
- Fichiers audio temporaires dans `backend/data/temp/` (ignorés par git)

### ESP32 (futur)

- Matériel en commande
- I2S pour microphone (INMP441) et speaker (MAX98357A)
- Wake word detection locale
- Communication WiFi avec backend

---

## Documentation

- **README.md**: Vue d'ensemble et démarrage rapide
- **TODO.md**: État actuel et prochaines étapes
- **ARCHITECTURE.md**: Architecture technique détaillée
- **START.md**: Guide ultra-rapide 30 secondes
- **docs/**: Documentation spécifique (QUICK_START, WEB_INTERFACE)

---

## Domaine: Assistant Personnel

Jarvis doit gérer:
- Informations personnelles (préférences, contacts, habitudes)
- Événements (rendez-vous, rappels, anniversaires)
- Connaissances mémorisées depuis conversations
- Tâches et projets
- Contexte conversationnel
- Home automation (futur)

### Flow Conversationnel

1. **Capture**: Audio via microphone (web ou ESP32)
2. **STT**: Whisper transcrit en texte
3. **Agent**:
   - Recherche dans knowledge graph (GraphRAG)
   - Génération réponse via OpenRouter
   - Extraction nouvelles entités à mémoriser
4. **Mise à jour**: Graphiti stocke nouvelles informations
5. **TTS**: Edge TTS génère audio réponse
6. **Lecture**: Audio renvoyé à l'utilisateur

---

## Ressources Utiles

- **Graphiti**: https://github.com/getzep/graphiti
- **OpenRouter**: https://openrouter.ai/docs
- **Whisper**: https://github.com/openai/whisper
- **Neo4j**: https://neo4j.com/docs/
- **ESP32 Audio**: https://github.com/atomic14/esp32_audio

---

## Notes Importantes

- Le projet utilise maintenant un frontend séparé (Vue.js) au lieu de l'ancien `static/`
- `backend/src/code_analysis/` est un nouveau module pour analyser du code Python
- Les fichiers temporaires audio (.webm) dans `backend/data/temp/` ne doivent pas être versionnés
- OpenRouter permet d'accéder à de nombreux modèles LLM (Claude, GPT-4, Llama, etc.)
