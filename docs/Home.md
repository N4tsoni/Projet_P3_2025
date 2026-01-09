---
tags: [index, home, jarvis]
aliases: [Index, Accueil]
---

# 🏠 Jarvis - Documentation Hub

> **Jarvis** - Assistant vocal intelligent avec Knowledge Graph dynamique utilisant GraphRAG et Graphiti

---

## 🚀 Démarrage Rapide

- [[START|Guide de Démarrage 30 secondes]] - Lancer le projet en moins d'une minute
- [[QUICK_START|Quick Start Guide]] - Installation et configuration détaillée
- [[TODO|Liste des tâches]] - Suivi du développement

---

## 📚 Documentation Principale

### Vue d'Ensemble
- [[ARCHITECTURE|Architecture Système]] - Vue d'ensemble complète du système
- [[README|README Principal]] - Description générale du projet

### Configuration
- [[CLAUDE|Instructions Claude]] - Guide pour Claude Code (backend + frontend)
- [[frontend/CLAUDE|Frontend Claude]] - Instructions spécifiques frontend

---

## 🧠 Knowledge Graph Pipeline

### Documentation Pipeline
- [[README_PIPELINE|Pipeline Guide]] - Documentation utilisateur de la pipeline modulaire
- [[PIPELINE_ARCHITECTURE|Architecture Pipeline]] - Architecture technique détaillée avec diagrammes
- [[IMPLEMENTATION_SUMMARY|Résumé Implémentation]] - Changements et fonctionnalités implémentées
- [[KG_PIPELINE|KG Pipeline Overview]] - Vue d'ensemble du système KG

### Stages de la Pipeline
1. **[[#ParsingStage|Parsing]]** - CSV, JSON, PDF, TXT
2. **[[#ChunkingStage|Chunking]]** - Découpage en chunks
3. **[[#EmbeddingStage|Embedding]]** - Sentence-Transformers
4. **[[#NERStage|NER]]** - Named Entity Recognition (spaCy)
5. **[[#ExtractionStage|Extraction]]** - LLM Claude
6. **[[#TransformationStage|Transformation]]** - Normalisation
7. **[[#EnrichmentStage|Enrichment]]** - Enrichissement externe
8. **[[#ValidationStage|Validation]]** - Validation qualité
9. **[[#StorageStage|Storage]]** - Neo4j

---

## 🎨 Architecture Visuelle

```
┌─────────────────────────────────────────────────┐
│                   JARVIS                        │
│           Assistant Vocal Intelligent           │
└─────────────────────────────────────────────────┘
              │                    │
              ↓                    ↓
    ┌──────────────────┐  ┌──────────────────┐
    │    Frontend      │  │    Backend       │
    │   Vue.js 3       │  │   FastAPI        │
    │   TypeScript     │  │   Python 3.11    │
    └──────────────────┘  └──────────────────┘
              │                    │
              └────────┬───────────┘
                       ↓
              ┌──────────────────┐
              │   Knowledge      │
              │   Graph (Neo4j)  │
              └──────────────────┘
```

---

## 🔧 Stack Technique

### Frontend
- **Framework**: Vue.js 3 + Composition API
- **Language**: TypeScript
- **Build**: Vite
- **UI**: Element Plus, Tailwind CSS
- **State**: Pinia
- **Design**: Atomic Design + Glassmorphism

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11
- **STT**: Groq (Whisper-large-v3 API) ou Whisper Local
- **TTS**: Edge TTS (gratuit)
- **LLM**: Claude 3.5 Sonnet (OpenRouter)
- **Database**: Neo4j
- **KG Framework**: Graphiti

### Pipeline
- **Parsing**: CSV, JSON, PDF (pdfplumber), TXT
- **Embeddings**: Sentence-Transformers
- **NER**: spaCy
- **Extraction**: Claude via OpenRouter

---

## 📁 Structure du Projet

```
Projet_P3/
├── frontend/              # Vue.js Application
│   ├── src/
│   │   ├── components/   # Atomic Design
│   │   ├── views/        # Pages
│   │   ├── stores/       # Pinia stores
│   │   └── services/     # API client
│   └── [[frontend/CLAUDE|CLAUDE.md]]
│
├── backend/              # FastAPI Application
│   ├── src/
│   │   ├── api/         # Routes REST
│   │   ├── agents/      # LLM agents
│   │   ├── voice/       # STT (Groq/Whisper) + TTS
│   │   ├── kg/          # Knowledge Graph
│   │   │   ├── pipeline/    # Pipeline modulaire
│   │   │   ├── parsers/     # Document parsers
│   │   │   ├── agents/      # Entity/Relation extractors
│   │   │   └── services/    # Neo4j service
│   │   └── core/        # Configuration
│   └── [[CLAUDE|CLAUDE.md]]
│
├── docs/                 # 📚 Documentation (VOUS ÊTES ICI)
│   ├── [[Home|Home.md]]
│   ├── [[ARCHITECTURE|ARCHITECTURE.md]]
│   ├── [[README_PIPELINE|README_PIPELINE.md]]
│   ├── [[PIPELINE_ARCHITECTURE|PIPELINE_ARCHITECTURE.md]]
│   └── [[STT_Configuration|STT Configuration]]
│
└── docker-compose.yml
```

---

## 🎯 Fonctionnalités Principales

### ✅ Opérationnel
- [x] Pipeline vocal complet (STT → Agent → TTS)
  - STT: Groq API (rapide) ou Whisper Local
  - TTS: Edge TTS (gratuit)
- [x] Interface Vue.js moderne avec glassmorphism
- [x] Enregistrement push-to-talk avec visualisation
- [x] Historique des conversations
- [x] **Pipeline modulaire KG** (nouveau !)
- [x] **Parsers multi-formats** (CSV, JSON, PDF, TXT)
- [x] **Embeddings** avec Sentence-Transformers
- [x] **NER** avec spaCy
- [x] Extraction entités/relations avec Claude
- [x] Stockage Neo4j

### 🚧 En Développement
- [ ] Graphiti pour mémoire conversationnelle
- [ ] Transformations avancées
- [ ] Enrichissement externe (Wikipedia, DBpedia)
- [ ] Validation avancée

### 📦 Planifié
- [ ] Firmware ESP32
- [ ] Wake word detection
- [ ] Tests unitaires et d'intégration

---

## 📊 Pipeline Flow

```
Document Input
     ↓
ParsingStage (CSV/JSON/PDF/TXT) ✅
     ↓
ChunkingStage ✅
     ↓
EmbeddingStage (sentence-transformers) ✅
     ↓
NERStage (spaCy) ✅
     ↓
ExtractionStage (Claude LLM) ✅
     ↓
TransformationStage (normalisation)
     ↓
EnrichmentStage (external APIs)
     ↓
ValidationStage (quality checks)
     ↓
StorageStage (Neo4j) ✅
     ↓
Knowledge Graph
```

---

## 🔗 Liens Utiles

### Documentation Externe
- [Vue 3 Docs](https://vuejs.org/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Neo4j Docs](https://neo4j.com/docs/)
- [Sentence-Transformers](https://www.sbert.net/)
- [spaCy Docs](https://spacy.io/)
- [Obsidian](https://obsidian.md/)

### APIs Utilisées
- [OpenRouter](https://openrouter.ai/) - Claude 3.5 Sonnet
- [Edge TTS](https://github.com/rany2/edge-tts) - TTS gratuit
- [Groq](https://console.groq.com/) - STT Whisper-large-v3 (rapide)
- [Whisper](https://github.com/openai/whisper) - STT local (alternative)

---

## 📝 Notes de Développement

### Commandes Principales

```bash
# Démarrage
make build && make up

# Services
Frontend: http://localhost:5173
Backend:  http://localhost:8000
Neo4j:    http://localhost:7474

# Backend - Tests Pipeline
cd backend
python -m kg.pipeline_example
```

### Installation Pipeline

```bash
# Minimal (CSV only)
pip install pandas chardet

# Complet
pip install -r requirements_pipeline.txt
python -m spacy download en_core_web_sm
```

---

## 🏷️ Tags

#jarvis #knowledge-graph #pipeline #vue3 #fastapi #neo4j #claude #ai-assistant #voice-assistant #nlp #ner #embeddings #graphrag

---

## 📅 Dernière Mise à Jour

**Date**: 2026-01-07
**Version**: 1.0.0
**Statut**: ✅ Pipeline Production-Ready

---

## 🗺️ Navigation Rapide

- **Démarrage**: [[START]] → [[QUICK_START]]
- **Architecture**: [[ARCHITECTURE]] → [[PIPELINE_ARCHITECTURE]]
- **Pipeline**: [[README_PIPELINE]] → [[IMPLEMENTATION_SUMMARY]]
- **Frontend**: [[frontend/CLAUDE]]
- **Backend**: [[CLAUDE]]
- **KG**: [[KG_PIPELINE]]
- **Voice**: [[STT_Configuration|Configuration STT]]
- **TODO**: [[TODO]]
