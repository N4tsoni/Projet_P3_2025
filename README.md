# 🤖 Jarvis - Assistant Vocal Intelligent avec GraphRAG

> Assistant personnel vocal type "Jarvis" utilisant GraphRAG et Graphiti avec interface Vue.js moderne et ESP32 (à venir)

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Vue](https://img.shields.io/badge/Vue-3.5+-4FC08D.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.108.0-009688.svg)](https://fastapi.tiangolo.com)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.15-008CC1.svg)](https://neo4j.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📋 Table des Matières

- [Vue d'Ensemble](#-vue-densemble)
- [État Actuel](#-état-actuel)
- [Démarrage Rapide](#-démarrage-rapide)
- [Architecture](#-architecture)
- [Technologies](#-technologies)
- [Documentation](#-documentation)
- [Développement](#-développement)
- [Roadmap](#-roadmap)

---

## 🎯 Vue d'Ensemble

**Jarvis** est un assistant vocal intelligent qui mémorise vos conversations grâce à un **knowledge graph dynamique** (GraphRAG + Graphiti). Il combine:

- 🎤 **Reconnaissance vocale** (Whisper local - gratuit)
- 🧠 **Agent conversationnel** (Claude 3.5 Sonnet via OpenRouter)
- 🔊 **Synthèse vocale** (Edge TTS Microsoft - gratuit)
- 🕸️ **Knowledge Graph** (Neo4j + Graphiti)
- 🌐 **Interface Vue.js 3** moderne avec Atomic Design
- 📡 **ESP32** (à venir) pour interaction vocale physique

### Cas d'Usage

- Assistant personnel qui se souvient de vos préférences
- Gestion de tâches et rappels contextuels
- Conversations naturelles avec mémoire à long terme
- Base de connaissances personnelle interrogeable

---

## ✅ État Actuel

### **Phase 3: OPÉRATIONNEL** ✅

Le pipeline vocal complet est **fonctionnel et testé** avec une interface moderne:

```
Audio → Whisper STT → Claude Agent → Edge TTS → Audio Response
```

**Ce qui fonctionne aujourd'hui:**
- ✅ **Frontend Vue.js 3** avec TypeScript et Atomic Design
- ✅ Interface moderne avec glassmorphism et animations
- ✅ Push-to-talk vocal avec visualisation waveform temps réel
- ✅ Historique des conversations avec lecture audio
- ✅ Visualisation du knowledge graph
- ✅ Transcription vocale en français (Whisper local)
- ✅ Agent conversationnel intelligent (Claude via OpenRouter)
- ✅ Synthèse vocale en français (Edge TTS - voix Denise)
- ✅ Docker + Docker Compose avec 3 services
- ✅ Neo4j prêt pour knowledge graph
- ✅ API REST FastAPI complète

**En cours d'implémentation:**
- 🔄 Intégration Graphiti pour mémoire persistante (Phase 4)
- 🔄 Extraction automatique d'entités depuis conversations
- 🔄 GraphRAG pour enrichissement contextuel

**Planifié:**
- 📦 Firmware ESP32 (matériel en commande - Phase 5)
- 📦 Wake word detection ("Hey Jarvis")
- 📦 Tests unitaires et d'intégration

---

## 🚀 Démarrage Rapide

### Prérequis

- **Docker** et **Docker Compose** installés
- **4GB RAM** minimum
- Ports **5173**, **7474**, **7687**, et **8000** disponibles

### Installation (5 minutes)

```bash
# 1. Cloner le repository
git clone <repository-url>
cd Projet_P3

# 2. Configuration backend
cd backend
cp .env.example .env
# Éditer .env et ajouter votre clé OpenRouter:
# OPENROUTER_API_KEY=sk-or-v1-xxxxx

# 3. Retour à la racine et lancement
cd ..
docker compose build
docker compose up -d

# 4. Vérifier que tout fonctionne
docker compose ps
# Devrait afficher 3 services: jarvis-neo4j (healthy), jarvis-backend, jarvis-frontend
```

### Utilisation

1. **Ouvrir l'interface**: http://localhost:5173
2. **Maintenir** le bouton microphone
3. **Parler** en français
4. **Relâcher** le bouton
5. **Écouter** la réponse de Jarvis

**Exemple de conversation:**
- "Bonjour Jarvis, présente-toi"
- "Quelle heure est-il ?"
- "Rappelle-moi que j'aime le café noir"

### Accès aux Services

| Service | URL | Identifiants |
|---------|-----|--------------|
| **Frontend Vue.js** | http://localhost:5173 | - |
| **Backend API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Neo4j Browser** | http://localhost:7474 | neo4j / graphrag2024 |

---

## 🏗️ Architecture

### Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Vue.js 3)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Voice       │  │ Conversation │  │  Knowledge   │      │
│  │  Recorder    │  │  History     │  │  Graph Viz   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │ Axios API calls                │
└────────────────────────────┼────────────────────────────────┘
                             │ http://localhost:5173/api
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  /api/voice/process    POST  (Audio → Response)      │  │
│  │  /api/health           GET   (Health check)          │  │
│  │  /api/knowledge/graph  GET   (Graph data)            │  │
│  └──────────────────────────────────────────────────────┘  │
│         │                      │                            │
│         ▼                      ▼                            │
│  ┌────────────┐         ┌────────────┐                     │
│  │  Whisper   │         │  Edge TTS  │                     │
│  │    STT     │         │    TTS     │                     │
│  └────────────┘         └────────────┘                     │
│         │                      ▲                            │
│         │    "Bonjour"         │ MP3 audio                 │
│         ▼                      │                            │
│  ┌─────────────────────────────┴──────────────────┐        │
│  │   Claude 3.5 Sonnet Agent (OpenRouter)         │        │
│  └─────────────────────────────┬──────────────────┘        │
│                                 │                           │
│                                 ▼                           │
│  ┌──────────────────────────────────────────────┐          │
│  │   Graphiti + Neo4j Knowledge Graph           │          │
│  └──────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                        ┌──────────────┐
                        │   Neo4j DB   │
                        └──────────────┘
```

### Structure des Dossiers

```
Projet_P3/
├── frontend/                      # Frontend Vue.js 3
│   ├── src/
│   │   ├── components/
│   │   │   ├── atoms/            # Composants de base (BaseButton, BaseBadge, etc.)
│   │   │   ├── molecules/        # Combinaisons (StatCard, MessageBubble, etc.)
│   │   │   └── organisms/        # Sections complexes (VoiceRecorder, etc.)
│   │   ├── stores/               # Pinia state management
│   │   ├── services/             # API client (Axios)
│   │   ├── types/                # TypeScript types
│   │   ├── styles/               # SCSS global + mixins
│   │   ├── App.vue               # Composant racine
│   │   └── main.ts               # Point d'entrée
│   ├── public/                   # Assets statiques
│   ├── index.html
│   ├── vite.config.ts            # Configuration Vite
│   ├── tailwind.config.js        # Configuration Tailwind
│   ├── tsconfig.json             # Configuration TypeScript
│   ├── package.json              # Dépendances npm
│   ├── Dockerfile                # Image Node 20
│   └── CLAUDE.md                 # Documentation frontend
│
├── backend/                       # Backend FastAPI
│   ├── src/
│   │   ├── main.py               # Point d'entrée
│   │   ├── api/
│   │   │   └── main.py          # FastAPI app
│   │   ├── agents/
│   │   │   └── jarvis_agent.py  # Agent conversationnel
│   │   ├── voice/
│   │   │   ├── stt.py           # Speech-to-Text
│   │   │   └── tts.py           # Text-to-Speech
│   │   ├── graph/
│   │   │   └── graphiti_client.py # Knowledge graph
│   │   └── models/              # Modèles Pydantic
│   ├── tests/                   # Tests
│   ├── config/
│   │   └── graphiti_config.yaml
│   ├── pyproject.toml           # Dépendances Poetry
│   ├── Dockerfile               # Image Python 3.11
│   └── .env                     # Configuration
│
├── docker-compose.yml           # Orchestration 3 services
├── Makefile                    # Commandes dev
├── CLAUDE.md                   # Instructions projet
├── TODO.md                     # Roadmap
└── README.md                   # Ce fichier
```

### Atomic Design (Frontend)

Le frontend suit la méthodologie **Atomic Design** pour une réutilisabilité maximale:

```
Atoms (Composants de base)
  ↓
Molecules (Combinaisons simples)
  ↓
Organisms (Sections complexes)
  ↓
Templates (Layouts)
  ↓
Pages (Vues complètes)
```

**Exemples:**
- **Atoms**: BaseButton, BaseBadge, BaseIcon, BaseSpinner, BaseAvatar
- **Molecules**: StatCard, MessageBubble, AudioPlayer
- **Organisms**: VoiceRecorder, ConversationHistory, KnowledgeGraphViz

Voir `frontend/CLAUDE.md` pour la documentation complète.

---

## 🛠️ Technologies

### Frontend

| Technologie | Version | Usage |
|------------|---------|-------|
| **Vue 3** | 3.5.24 | Framework JavaScript progressif |
| **Vite** | 7.2.4 | Build tool ultra-rapide |
| **TypeScript** | 5.9.3 | Type safety |
| **Tailwind CSS** | 3.4.17 | Utility-first CSS |
| **SCSS** | 1.97.0 | Styles personnalisés |
| **Element Plus** | 2.12.0 | Bibliothèque UI Vue 3 |
| **Pinia** | 3.0.4 | State management |
| **Axios** | 1.13.2 | Client HTTP |

### Backend

| Technologie | Version | Usage |
|------------|---------|-------|
| **Python** | 3.11 | Langage principal |
| **FastAPI** | 0.108.0 | API REST async |
| **Uvicorn** | 0.25.0 | Serveur ASGI |
| **Neo4j** | 5.15 | Base de données graphe |
| **Graphiti** | 0.3.0 | Framework knowledge graph |
| **LangChain** | 0.1.0 | Framework LLM |
| **Docker** | - | Containerisation |

### Voice Processing

| Service | Provider | Coût | Notes |
|---------|----------|------|-------|
| **STT** | Whisper Local | Gratuit | OpenAI open-source, CPU ok |
| **STT (alt)** | Groq | Gratuit | Cloud, plus rapide |
| **LLM** | OpenRouter | ~$0.003/req | Claude 3.5 Sonnet |
| **TTS** | Edge TTS | Gratuit | Microsoft, voix fr-FR-DeniseNeural |
| **TTS (alt)** | Coqui TTS | Gratuit | Local, plus lent |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[CLAUDE.md](CLAUDE.md)** | Instructions projet pour Claude Code |
| **[frontend/CLAUDE.md](frontend/CLAUDE.md)** | Documentation frontend complète |
| **[TODO.md](TODO.md)** | Roadmap et progression |
| **[START.md](START.md)** | Guide démarrage ultra-rapide |
| **[docs/QUICK_START.md](docs/QUICK_START.md)** | Configuration détaillée |

---

## 💻 Développement

### Commandes Docker

```bash
# Démarrage
docker compose build            # Build images
docker compose up -d            # Lancer services
docker compose down             # Arrêter services

# Logs
docker compose logs -f          # Tous les logs
docker compose logs frontend    # Logs frontend
docker compose logs backend     # Logs backend
docker compose logs neo4j       # Logs Neo4j

# État
docker compose ps               # Voir les services
docker compose restart frontend # Redémarrer un service
```

### Développement Frontend

```bash
cd frontend

# Installation (si pas de Docker)
npm install

# Développement local (HMR)
npm run dev

# Build de production
npm run build

# Preview du build
npm run preview

# Type checking
npm run type-check
```

### Développement Backend

```bash
cd backend

# Installation Poetry
poetry install

# Lancer en local (sans Docker)
poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Tests
poetry run pytest

# Qualité code
poetry run black src/
poetry run ruff check src/
poetry run mypy src/
```

### Ajouter des Dépendances

**Frontend:**
```bash
# Via Docker
docker compose exec frontend npm install package-name

# En local
cd frontend && npm install package-name
```

**Backend:**
```bash
# Via Docker
docker compose exec backend poetry add package-name

# En local
cd backend && poetry add package-name
```

### Configuration

**Backend** (`.env` dans `backend/`):
```bash
# Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=graphrag2024

# OpenRouter (requis)
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Modèle LLM
LLM_MODEL=anthropic/claude-3.5-sonnet

# Speech-to-Text
STT_PROVIDER=whisper-local
STT_MODEL=base

# Text-to-Speech
TTS_PROVIDER=edge-tts
TTS_VOICE=fr-FR-DeniseNeural

# Logging
LOG_LEVEL=INFO
```

**Frontend** :
Les variables d'environnement sont gérées via `vite.config.ts` avec proxy vers le backend.

---

## 🗺️ Roadmap

### ✅ Phase 1-3: Infrastructure, API, Frontend (Complété)

- [x] Architecture backend/frontend séparée
- [x] Docker Compose avec 3 services
- [x] Frontend Vue 3 + TypeScript + Atomic Design
- [x] Interface moderne avec glassmorphism
- [x] Backend FastAPI complet
- [x] Pipeline vocal fonctionnel
- [x] Whisper STT + Edge TTS
- [x] Agent Claude 3.5 Sonnet

### 🔄 Phase 4: Knowledge Graph (En cours)

- [ ] Définir schéma entités (Person, Event, Task, Preference, Note)
- [ ] Extraction automatique entités depuis conversations
- [ ] Mise à jour automatique knowledge graph
- [ ] GraphRAG pour enrichissement contexte
- [ ] Recherche sémantique dans le graphe
- [ ] Visualisation interactive du graphe (D3.js/Cytoscape)

### 📦 Phase 5: ESP32 Hardware (Matériel en commande)

- [ ] Firmware ESP32 avec wake word
- [ ] Driver microphone I2S
- [ ] Driver speaker I2S
- [ ] Communication WiFi avec backend
- [ ] LED feedback

### 📦 Phase 6: Fonctionnalités Avancées

- [ ] Multi-utilisateurs
- [ ] Home automation (MQTT/Zigbee)
- [ ] Tests E2E frontend + backend
- [ ] CI/CD
- [ ] Monitoring

**Voir [TODO.md](TODO.md) pour les détails complets.**

---

## 🔧 Git Workflow

### Structure Git

Le projet utilise un **mono-repo** avec deux sous-projets:
- `frontend/` - Application Vue.js
- `backend/` - Application FastAPI

Chaque sous-projet a son propre `.gitignore` et peut être géré indépendamment.

### Conventions de Commit

Format : `type(scope): message`

**Types:**
- `feat` - Nouvelle fonctionnalité
- `fix` - Correction de bug
- `style` - Changements de style/CSS
- `refactor` - Refactoring de code
- `docs` - Documentation
- `test` - Tests
- `chore` - Maintenance

**Exemples:**
```bash
git commit -m "feat(frontend): add voice recorder component"
git commit -m "fix(backend): resolve whisper memory leak"
git commit -m "style(frontend): update glassmorphism effects"
git commit -m "docs: update README with new architecture"
```

### Workflow

```bash
# 1. Créer une branche feature
git checkout -b feature/amazing-feature

# 2. Faire vos modifications (frontend et/ou backend)
# ...

# 3. Commit avec message descriptif
git commit -m "feat(frontend): add feature X"

# 4. Push la branche
git push origin feature/amazing-feature

# 5. Créer une Pull Request sur GitHub
```

---

## 🐛 Dépannage

### Frontend ne démarre pas

```bash
# Vérifier les logs
docker compose logs frontend

# Rebuild le frontend
docker compose build --no-cache frontend
docker compose up -d frontend
```

### Backend ne se connecte pas à Neo4j

```bash
# Vérifier que Neo4j est healthy
docker compose ps

# Redémarrer Neo4j
docker compose restart neo4j

# Voir les logs
docker compose logs neo4j
```

### Erreur "Cannot apply unknown utility class"

Si Tailwind CSS affiche des erreurs de classes:
```bash
# Vérifier la version de Tailwind
docker compose exec frontend npm list tailwindcss

# Devrait afficher v3.4.17
# Si v4.x, rebuild le frontend
```

### Whisper est lent

```bash
# Dans backend/.env, utiliser un modèle plus petit
STT_MODEL=tiny  # ou base, small, medium, large

# Ou passer à Groq (cloud)
STT_PROVIDER=groq
GROQ_API_KEY=votre-clé
```

---

## 🤝 Contribution

Les contributions sont bienvenues!

### Standards Code

**Frontend:**
- Vue 3 Composition API (`<script setup>`)
- TypeScript strict mode
- Atomic Design
- Tailwind pour layouts, SCSS pour styles custom
- ESLint + Prettier

**Backend:**
- Black pour formatage (line length 100)
- Ruff pour linting
- MyPy pour type checking
- Pytest pour tests

```bash
# Vérifier avant commit
cd frontend && npm run type-check
cd backend && poetry run black src/ && poetry run ruff check src/
```

---

## 📄 Licence

MIT License - voir [LICENSE](LICENSE) pour les détails.

---

## 🙏 Remerciements

- **Vue.js** pour le framework réactif moderne
- **OpenAI Whisper** pour le STT open-source
- **Microsoft Edge TTS** pour la synthèse vocale gratuite
- **OpenRouter** pour l'accès unifié aux LLMs
- **Anthropic Claude** pour les capacités conversationnelles
- **Neo4j** pour la base de données graphe
- **Graphiti** pour le framework knowledge graph

---

## 📞 Support

- **Documentation**: Voir `CLAUDE.md` et `frontend/CLAUDE.md`
- **Issues**: Ouvrir un ticket GitHub
- **Questions**: Consulter [TODO.md](TODO.md) pour la roadmap

---

**Fait avec ❤️ pour créer un véritable assistant personnel intelligent**
