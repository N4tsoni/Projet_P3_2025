# TODO - Jarvis Assistant Vocal

> Version à jour du projet - Dernière mise à jour: 2026-01-07
> **Branche actuelle: KG** - Refonte complète du Knowledge Graph par pipeline d'agents IA

---

## 🎯 État Actuel

### ✅ **Fonctionnel** (Phases 1-4 complétées)

**Infrastructure:**
- [x] Docker Compose (4 services: frontend, backend, neo4j, postgres)
- [x] Poetry pour gestion dépendances Python
- [x] PostgreSQL pour persistence des conversations
- [x] Neo4j pour le Knowledge Graph

**Frontend Vue.js 3:**
- [x] Interface moderne avec TypeScript + Element Plus
- [x] Atomic Design (atoms, molecules, organisms)
- [x] Glassmorphism et animations
- [x] VoiceRecorder avec push-to-talk
- [x] ConversationSidebar - Gestion conversations
- [x] Historique persistant des conversations
- [x] Responsive design (3 colonnes)

**Backend FastAPI - Layered Architecture:**
- [x] Architecture en couches (Routes → Services → Repositories → Models)
- [x] API REST complète
- [x] Speech-to-Text: Groq Whisper large-v3
- [x] Agent: OpenRouter avec Claude 3.5 Sonnet
- [x] Text-to-Speech: Edge TTS
- [x] Pipeline vocal: Audio → STT → Agent → TTS → Audio
- [x] Persistence PostgreSQL avec SQLAlchemy
- [x] Auto-nommage des conversations
- [x] CRUD complet conversations/messages

**Tests:**
- [x] Tests unitaires pytest (voice_service, 92% couverture)
- [x] 5 Jupyter notebooks pour tests interactifs
- [x] Documentation complète

---

## ✅ **COMPLÉTÉ - Phase 5: Knowledge Graph par Pipeline d'Agents IA (Sprint 1)**

### 🆕 **Nouvelle Approche KG Builder**

**Pourquoi ce changement ?**
- ❌ Graphiti nécessite Neo4j Enterprise (fonctions vectorielles)
- ✅ **Pipeline d'agents IA** = contrôle total, flexible, puissant
- ✅ LLM (Claude) excellent pour extraction entités/relations
- ✅ Support natif données structurées ET non-structurées
- ✅ Évolutif et modulaire

### **Architecture Pipeline KG**

```
Documents (CSV, JSON, PDF, TXT)
    ↓
Agent Parser (analyse format, extraction)
    ↓
Agent Entity Extractor (identifie entités + propriétés)
    ↓
Agent Relation Extractor (identifie relations)
    ↓
Neo4j Storage (CREATE nodes et edges)
    ↓
Agent Validator (cohérence, déduplication, enrichissement)
```

### **Tâches Phase 5**

**Backend - Pipeline KG:**
- [x] Créer structure `backend/src/kg/` (agents, services, models)
- [x] Agent Parser - Analyse et extraction de documents (CSV)
- [x] Agent Entity Extractor - Extraction d'entités typées (Claude)
- [x] Agent Relation Extractor - Extraction de relations (Claude)
- [x] Service Neo4j direct (sans Graphiti)
- [x] Models Pydantic pour entités/relations
- [x] Pipeline orchestrator (coordonne les agents)
- [x] Routes API `/api/kg/*` (upload, process, query, graph)
- [x] Support format CSV (JSON, PDF, TXT à venir Sprint 2)
- [x] Déduplication de base (avancée Sprint 2)

**Frontend - KG Builder:**
- [x] Page dédiée "KG Builder" (`/kg-builder`)
- [x] Upload zone (drag & drop fichiers)
- [x] Processing status en temps réel (indicateurs de progression)
- [x] KGFileUpload component avec validation
- [x] KGStatistics component (compteurs nodes/relations par type)
- [x] KGGraphViewer component (liste des nodes/edges)
- [x] Navigation par onglets (Upload/Statistics/Graph)
- [x] Store Pinia pour gestion état KG
- [x] Intégration API complète
- [ ] Graph viewer interactif visuel (D3.js ou vis.js) - Sprint 2
- [ ] Recherche et filtrage avancé du graphe - Sprint 2
- [ ] Export du graphe (JSON, Cypher) - Sprint 2

**Tests & Validation:**
- [x] Tests unitaires agents d'extraction
- [x] Tests d'intégration pipeline complet
- [x] Notebook démo complet (06_kg_pipeline_test.ipynb)
- [x] Dataset test CSV (movies_sample.csv)
- [x] Validation qualité extraction (via tests)

---

## 📦 Planifié (Phase 6+)

### **Évolution KG Builder**

**Support multi-sources:**
- [ ] Upload API endpoints (intégration externe)
- [ ] Scraping web agents
- [ ] Base de données SQL/NoSQL sources
- [ ] Synchronisation temps réel

**Intelligence avancée:**
- [ ] Enrichissement automatique via LLM
- [ ] Résolution d'entités (entity linking)
- [ ] Inférence de relations implicites
- [ ] Clustering et communautés
- [ ] Temporal knowledge graph (évolution dans le temps)

**GraphRAG - Retrieval Augmented Generation:**
- [ ] Intégration KG dans le contexte de l'agent vocal
- [ ] Recherche sémantique dans le graphe
- [ ] Réponses enrichies par le graphe
- [ ] Questions sur le KG ("Qui connaît qui ?", "Quels événements en janvier ?")

### **ESP32 Hardware** (matériel en commande)

**Setup Initial:**
- [ ] Configuration PlatformIO pour ESP32
- [ ] Driver I2S micro + speaker
- [ ] Tests capture/lecture audio

**Pipeline complet:**
- [ ] Wake word detection ("Hey Jarvis")
- [ ] Communication WiFi avec backend
- [ ] Gestion états et LED feedback

---

## 🚀 Fonctionnalités Futures

### **KG Builder UX**
- [ ] Templates de schémas prédéfinis (CRM, Events, People, etc.)
- [ ] Mode wizard pour création guidée
- [ ] Versioning du graphe (snapshots)
- [ ] Collaboration multi-utilisateurs
- [ ] Permissions et accès contrôlés

### **Assistant Vocal Avancé**
- [ ] Support multi-utilisateurs
- [ ] Routines et automatisations
- [ ] Notifications proactives
- [ ] Intégration calendrier/email
- [ ] Home automation

---

## 📂 Structure du Projet (Nouvelle)

```
Projet_P3/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── organisms/
│   │   │       ├── VoiceRecorder.vue
│   │   │       ├── ConversationSidebar.vue
│   │   │       └── KGBuilder.vue (NOUVEAU)
│   │   ├── views/
│   │   │   └── KGBuilderView.vue (NOUVEAU)
│   │   ├── stores/
│   │   │   ├── conversation.ts
│   │   │   └── kg.ts (NOUVEAU)
│   │   └── services/
│   │       └── api.ts (+ méthodes KG)
│   └── ...
│
├── backend/
│   ├── src/
│   │   ├── api/routes/
│   │   │   ├── voice.py
│   │   │   ├── conversations.py
│   │   │   ├── knowledge.py (refactoring)
│   │   │   └── kg.py (NOUVEAU - KG Builder routes)
│   │   ├── kg/ (NOUVEAU - Pipeline KG)
│   │   │   ├── agents/
│   │   │   │   ├── parser_agent.py
│   │   │   │   ├── entity_extractor_agent.py
│   │   │   │   ├── relation_extractor_agent.py
│   │   │   │   └── validator_agent.py
│   │   │   ├── services/
│   │   │   │   ├── kg_service.py
│   │   │   │   ├── neo4j_service.py
│   │   │   │   └── pipeline_orchestrator.py
│   │   │   ├── models/
│   │   │   │   ├── entity.py
│   │   │   │   ├── relation.py
│   │   │   │   └── document.py
│   │   │   └── parsers/
│   │   │       ├── csv_parser.py
│   │   │       ├── json_parser.py
│   │   │       ├── pdf_parser.py
│   │   │       └── txt_parser.py
│   │   ├── services/
│   │   │   ├── voice_service.py
│   │   │   └── conversation_service.py
│   │   ├── repositories/
│   │   │   └── conversation_repository.py
│   │   └── ...
│   ├── tests/
│   │   └── kg/ (NOUVEAU - Tests pipeline)
│   └── notebooks/
│       └── 06_kg_pipeline_test.ipynb (NOUVEAU)
│
├── docs/
│   ├── TODO.md (ce fichier)
│   ├── ARCHITECTURE.md
│   ├── KG_PIPELINE.md (NOUVEAU - Doc pipeline KG)
│   └── ...
│
└── ...
```

---

## 🛠️ Commandes Utiles

### Docker
```bash
make up            # Lancer tous les services
make down          # Arrêter
make logs          # Logs
```

### Développement Backend
```bash
# Ajouter dépendance
docker compose exec backend poetry add package-name

# Tests
docker compose exec backend pytest

# Jupyter
docker compose exec backend jupyter notebook \
  --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```

### Neo4j - Requêtes KG
```bash
# Via Python
docker compose exec backend python

>>> from neo4j import GraphDatabase
>>> driver = GraphDatabase.driver("bolt://neo4j:7687", auth=("neo4j", "graphrag2024"))
>>> with driver.session() as session:
...     result = session.run("MATCH (n) RETURN count(n)")
...     print(result.single()[0])
```

### Accès Services
```bash
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/docs
# Neo4j Browser: http://localhost:7474
# PostgreSQL: localhost:5432
# Jupyter: http://localhost:8888
```

---

## 🎯 Plan d'Action - Branche KG

### **Sprint 1 - Fondations** ✅ COMPLÉTÉ

**Jour 1-2: Architecture & Setup**
- [x] Nettoyer ancien code Graphiti/code_analysis
- [x] Créer structure `backend/src/kg/`
- [x] Setup Neo4j direct (models, service)
- [x] Routes API de base `/api/kg/`
- [ ] Frontend: page KG Builder (structure) - Sprint 2

**Jour 3-4: Premier Agent - CSV**
- [x] Parser CSV avec Pandas
- [x] Agent Entity Extractor (CSV structuré)
- [x] Agent Relation Extractor (CSV)
- [x] Storage Neo4j
- [x] Test end-to-end CSV → Neo4j

**Jour 5: Validation & Tests**
- [x] Tests unitaires agents
- [x] Notebook de démo
- [x] Dataset test CSV
- [ ] Graph viewer basique frontend - Sprint 2

**✅ Sprint 1 COMPLÉTÉ - Pipeline KG complet opérationnel (Backend + Frontend)!**

### **Sprint 2 - Extension (semaine prochaine)**
- [ ] Support JSON, PDF, TXT
- [ ] Agent Validator (déduplication)
- [ ] Graph viewer avancé (D3.js)
- [ ] Upload multi-fichiers
- [ ] Processing status temps réel

### **Sprint 3 - GraphRAG (après)**
- [ ] Intégration KG → contexte agent vocal
- [ ] Recherche sémantique dans KG
- [ ] Questions sur le graphe
- [ ] Enrichissement automatique

---

## 📊 Schéma KG Initial (Exemple)

### **Types d'Entités**
```python
EntityType:
  - Person (name, email, phone, role)
  - Organization (name, industry, location)
  - Event (name, date, location, description)
  - Document (title, type, date, source)
  - Concept (name, category, description)
```

### **Types de Relations**
```python
RelationType:
  - KNOWS (Person → Person)
  - WORKS_AT (Person → Organization)
  - ATTENDED (Person → Event)
  - MENTIONS (Document → Person/Org/Concept)
  - RELATED_TO (generic)
  - HAPPENED_AT (Event → Location)
  - CREATED_BY (Document → Person)
```

---

## 📚 Ressources

### Documentation Projet
- [README.md](../README.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [KG_PIPELINE.md](KG_PIPELINE.md) (à créer)
- [TESTING.md](TESTING.md)

### Technologies - KG Pipeline
- **Neo4j Python Driver**: https://neo4j.com/docs/python-manual/current/
- **LangChain** (optionnel pour agents): https://python.langchain.com/
- **Pandas** (parsing CSV): https://pandas.pydata.org/
- **PyPDF2** (parsing PDF): https://pypdf2.readthedocs.io/
- **D3.js** (graph viz): https://d3js.org/
- **vis.js** (alternative graph viz): https://visjs.org/

### LLM pour Agents
- **OpenRouter API**: https://openrouter.ai/docs
- **Claude Sonnet 4**: Excellent pour extraction structurée
- **Prompt Engineering**: https://www.anthropic.com/claude/prompting

---

## 🎉 Changelog

### 2026-01-07 (soir) - Branche KG - Sprint 1 COMPLET ✅ + Corrections
- ✅ Frontend KG Builder complet et opérationnel
- ✅ KGFileUpload component (drag & drop, validation, progress)
- ✅ KGStatistics component (dashboard stats)
- ✅ KGGraphViewer component (liste nodes/edges)
- ✅ Navigation par onglets (Upload/Statistics/Graph)
- ✅ Store Pinia kg.ts pour state management
- ✅ Corrections critiques pipeline:
  - Fixed: entity.type.value sur string (use_enum_values=True)
  - Fixed: Neo4j service calls (sync vs async)
  - Fixed: Neo4j connect() manquant
  - Fixed: document.mark_completed() arguments manquants
  - Fixed: storage_data None handling
- ✅ Pipeline testé et validé end-to-end
- ✅ Gestion idempotente des duplicates (MERGE Neo4j)
- ✅ 12 entités + 9 relations test stockées avec succès

### 2026-01-07 (matin) - Branche KG - Sprint 1 Backend ✅
- ✅ Nettoyage code Graphiti et code_analysis
- ✅ TODO mis à jour avec nouvelle approche Pipeline KG
- ✅ Architecture Pipeline d'agents IA complète
- ✅ Models Pydantic (Entity, Relation, Document)
- ✅ Service Neo4j direct (MERGE, batch operations)
- ✅ Parser CSV avec auto-détection (encoding, délimiteur)
- ✅ Agent Entity Extractor (Claude via OpenRouter)
- ✅ Agent Relation Extractor (Claude via OpenRouter)
- ✅ Pipeline Orchestrator (coordination complète)
- ✅ Routes API `/api/kg/*` (8 endpoints)
- ✅ Dataset test Movies (10 films, 45 entités, 78 relations)
- ✅ Tests end-to-end pytest
- ✅ Notebook démo interactif (06_kg_pipeline_test.ipynb)
- ✅ Documentation complète (KG_PIPELINE.md)

### 2026-01-07 - Main
- ✅ Système conversations complet (PostgreSQL)
- ✅ Auto-nommage conversations
- ✅ Migration Groq Whisper
- ✅ Layered Architecture
- ✅ Tests + Documentation

---

**Branche KG - Objectif: Knowledge Graph Builder complet par agents IA** 🚀
