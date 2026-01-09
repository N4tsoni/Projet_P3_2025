# 🤖 Jarvis - Assistant Vocal Intelligent

> Assistant vocal avec Knowledge Graph dynamique, agent LangGraph et recherche vectorielle

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Vue](https://img.shields.io/badge/Vue-3.5+-4FC08D.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.108.0-009688.svg)](https://fastapi.tiangolo.com)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.15-008CC1.svg)](https://neo4j.com)

---

## 🎯 Vue d'Ensemble

Jarvis est un assistant vocal intelligent qui combine **reconnaissance vocale**, **agent conversationnel avec mémoire contextuelle** et **knowledge graph dynamique**.

**Pipeline complet :**
```
Audio → Whisper STT → LangGraph Agent (6 nodes) → Neo4j KG → Edge TTS → Audio
```

**Stack technique :**
- 🎤 **Whisper** (STT local)
- 🧠 **Agent LangGraph** avec Neo4j Vector Search + GraphRAG
- 🔊 **Edge TTS** (synthèse vocale)
- 🕸️ **Knowledge Graph** Neo4j + pipeline modulaire (9 stages)
- 🌐 **Frontend Vue.js 3** moderne avec animations

---

## 🚀 Démarrage Rapide

### Prérequis
- Docker & Docker Compose
- 4GB RAM minimum
- Clé API OpenRouter

### Installation (2 minutes)

```bash
# 1. Cloner le repo
git clone <repository-url>
cd Projet_P3

# 2. Configuration
cd backend
cp .env.example .env
# Éditer .env et ajouter: OPENROUTER_API_KEY=sk-or-v1-xxxxx

# 3. Lancement
cd ..
docker compose up -d

# 4. Accès
# Frontend: http://localhost:5173
# API: http://localhost:8000/docs
# Neo4j: http://localhost:7474 (neo4j/graphrag2024)
```

**Utilisation :** Ouvrir http://localhost:5173, maintenir le bouton micro, parler, relâcher.

---

## 🏗️ Architecture

### Vue Simplifiée

```
┌─────────────────────────────────────────────┐
│  Frontend Vue.js 3                          │
│  - Voice Recorder (push-to-talk)           │
│  - Conversation History                     │
│  - KG Builder (upload docs + pipeline 🏃‍♂️) │
└─────────────────┬───────────────────────────┘
                  │ REST API
┌─────────────────▼───────────────────────────┐
│  Backend FastAPI                            │
│  ┌──────────────────────────────────────┐   │
│  │ LangGraph Agent (6 nodes)            │   │
│  │ NER → Semantic Search → Ranking      │   │
│  │ → Context → LLM → Memory             │   │
│  └──────────────┬───────────────────────┘   │
│                 │                            │
│  ┌──────────────▼───────────────────────┐   │
│  │ KG Pipeline (9 stages)               │   │
│  │ Parsing → Chunking → Embedding       │   │
│  │ → NER → Extraction → Transform       │   │
│  │ → Enrich → Validate → Storage        │   │
│  └──────────────┬───────────────────────┘   │
└─────────────────┼───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  Neo4j (Graph + Vector Search)              │
│  PostgreSQL (Conversation History)          │
└─────────────────────────────────────────────┘
```

### Composants Clés

| Composant | Description |
|-----------|-------------|
| **Agent LangGraph** | 6 nodes modulaires (NER, retrieval, ranking, context, LLM, memory) |
| **Neo4j Vector** | Recherche vectorielle native avec embeddings all-MiniLM-L6-v2 |
| **Pipeline KG** | 9 stages configurables pour traiter CSV, JSON, PDF, TXT, XLSX, XML |
| **GraphRAG** | Enrichissement contextuel avec ranking multi-facteurs |
| **Frontend** | Vue 3 + TypeScript + Atomic Design + animations |

---

## 📚 Documentation

Documentation complète dans [`docs/`](docs/) :

| Document | Contenu |
|----------|---------|
| **[Home](docs/Home.md)** | Vue d'ensemble et concepts |
| **[KG_PIPELINE](docs/KG_PIPELINE.md)** | Pipeline Knowledge Graph détaillé |
| **[PIPELINE_ARCHITECTURE](docs/PIPELINE_ARCHITECTURE.md)** | Architecture technique du pipeline |
| **[STT_Configuration](docs/STT_Configuration.md)** | Configuration Speech-to-Text |
| **[SPRINT1_COMPLETE](docs/SPRINT1_COMPLETE.md)** | Résumé Phase 4 |

**Visualisations Obsidian :**
- [Jarvis Architecture](docs/Jarvis%20Architecture.canvas)
- [Jarvis LangGraph Agent](docs/Jarvis%20LangGraph%20Agent.canvas)

---

## 🛠️ Technologies

**Backend :** Python 3.11, FastAPI, LangGraph, LangChain, Neo4j, PostgreSQL, spaCy, sentence-transformers

**Frontend :** Vue 3, TypeScript, Vite, Tailwind CSS, Element Plus, Pinia

**Voice :** Whisper (STT), Edge TTS (TTS)

**LLM :** Claude 3.5 Sonnet via OpenRouter

---

## 💻 Développement

```bash
# Logs
docker compose logs -f

# Redémarrer un service
docker compose restart backend

# Ajouter une dépendance backend
docker compose exec backend poetry add package-name

# Ajouter une dépendance frontend
docker compose exec frontend npm install package-name

# Tests
docker compose exec backend pytest
```

**Variables d'environnement** (`.env` dans `backend/`) :
```bash
NEO4J_URI=bolt://neo4j:7687
OPENROUTER_API_KEY=sk-or-v1-xxxxx
LLM_MODEL=anthropic/claude-3.5-sonnet
STT_PROVIDER=whisper-local
TTS_PROVIDER=edge-tts
```

---

## 🗺️ Roadmap

### ✅ Phase 1-4 : Complétées
- Infrastructure Docker
- Pipeline vocal complet
- Frontend Vue.js moderne
- Agent LangGraph avec Neo4j Vector Search
- Pipeline KG modulaire (9 stages)
- GraphRAG avec ranking
- Animation UI (pipeline progress 🏃‍♂️)

### 📦 Phase 5 : ESP32 Hardware (Planifié)
- Firmware ESP32 avec wake word
- Microphone + speaker I2S
- Communication WiFi

### 📦 Phase 6 : Avancé (Planifié)
- Multi-utilisateurs
- Tests E2E complets
- CI/CD
- Monitoring

---

## 🤝 Contribution

**Standards :**
- Backend : Black, Ruff, MyPy, Pytest
- Frontend : ESLint, Prettier, TypeScript strict
- Commits : `type(scope): message` (feat, fix, docs, style, refactor, test, chore)

**Workflow :**
```bash
git checkout -b feature/amazing-feature
# ... développement ...
git commit -m "feat(backend): add amazing feature"
git push origin feature/amazing-feature
# Créer Pull Request
```

---

## 📄 Licence

MIT License - voir [LICENSE](LICENSE)

---

**Fait avec ❤️ - Documentation complète dans [docs/](docs/)**
