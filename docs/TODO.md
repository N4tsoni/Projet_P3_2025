# TODO - Jarvis Assistant Vocal

> Version à jour du projet - Dernière mise à jour: 2026-01-07

---

## 🎯 État Actuel

### ✅ **Fonctionnel** (Phases 1-4 complétées)

**Infrastructure:**
- [x] Docker Compose (4 services: frontend, backend, neo4j, postgres)
- [x] Poetry pour gestion dépendances Python
- [x] Configuration .env simplifiée
- [x] PostgreSQL pour persistence des conversations

**Frontend Vue.js 3:**
- [x] Interface moderne avec TypeScript + Element Plus
- [x] Atomic Design (atoms, molecules, organisms, templates)
- [x] Glassmorphism et animations
- [x] VoiceRecorder avec push-to-talk et visualisation audio
- [x] **ConversationSidebar** - Gestion complète des conversations
- [x] **Historique des conversations persistant**
- [x] Visualisation du knowledge graph (préparé)
- [x] Responsive design (3 colonnes: sidebar | recorder | content)

**Backend FastAPI - Layered Architecture:**
- [x] **Architecture en couches** (Routes → Services → Repositories → Models)
- [x] API REST complète avec documentation auto-générée
- [x] **Speech-to-Text: Groq Whisper large-v3** (10x plus rapide que local)
- [x] Agent: OpenRouter avec Claude 3.5 Sonnet
- [x] Text-to-Speech: Edge TTS (gratuit, voix fr-FR-DeniseNeural)
- [x] Pipeline vocal complet: Audio → STT → Agent → TTS → Audio
- [x] **Persistence PostgreSQL** avec SQLAlchemy
- [x] **Auto-nommage des conversations** depuis premier message
- [x] CRUD complet pour conversations et messages

**Tests & Validation:**
- [x] Tests unitaires pytest (voice_service, 92% couverture)
- [x] 5 Jupyter notebooks pour tests interactifs :
  - `01_test_stt_groq.ipynb` - Test Groq Whisper
  - `02_test_tts_edge.ipynb` - Test Edge TTS
  - `03_test_agent_openrouter.ipynb` - Test agent Claude
  - `04_test_neo4j_graphiti.ipynb` - Test Neo4j/Graphiti
  - `05_pipeline_complet.ipynb` - Test pipeline end-to-end
- [x] Documentation complète (ARCHITECTURE.md, TESTING.md)

---

## 🔄 En Cours (Phase 5)

### **Knowledge Graph & GraphRAG**

**Note**: Neo4j Community Edition ne supporte pas les fonctions de similarité vectorielle natives nécessaires pour Graphiti. À évaluer:
- Option 1: Migrer vers Neo4j Enterprise
- Option 2: Utiliser alternative (Memgraph, etc.)
- Option 3: Implémenter solution custom avec embeddings

**Objectifs GraphRAG:**
- [ ] Schéma du graphe pour entités conversationnelles
  - Person, Event, Task, Note, Preference, Contact
  - Relations: KNOWS, LIKES, SCHEDULED_FOR, RELATED_TO
- [ ] Extraction automatique d'entités depuis transcriptions vocales
- [ ] Mise à jour du graphe post-conversation
- [ ] GraphRAG: Recherche sémantique dans le knowledge graph
- [ ] Enrichissement du contexte de l'agent avec infos du graphe

---

## 📦 Planifié (Phase 6+)

### **ESP32 Hardware** (matériel en commande)

**Setup Initial:**
- [ ] Configuration PlatformIO pour ESP32
- [ ] Driver I2S pour microphone INMP441
- [ ] Driver I2S pour speaker MAX98357A
- [ ] Tests basiques capture/lecture audio

**Wake Word & Communication:**
- [ ] Wake word detection locale ("Hey Jarvis")
- [ ] WiFi manager et client HTTP
- [ ] Upload audio vers backend
- [ ] Download et lecture réponse audio

**Pipeline ESP32 Complet:**
- [ ] Intégration: Wake word → Capture → Backend → Lecture
- [ ] Gestion états (idle, listening, processing, speaking)
- [ ] LED indicators pour feedback utilisateur
- [ ] Optimisation latence matérielle

---

## 🚀 Fonctionnalités Futures

### **Améliorations UX**
- [ ] Recherche dans les conversations
- [ ] Tags/catégories pour conversations
- [ ] Export/import des conversations (JSON, texte)
- [ ] Raccourcis clavier pour interface web
- [ ] Mode conversation continue (sans push-to-talk)
- [ ] Thèmes personnalisables (dark/light)

### **Intelligence Avancée**
- [ ] Support multi-utilisateurs (reconnaissance vocale)
- [ ] Routines et automatisations personnalisées
- [ ] Notifications proactives basées sur le contexte
- [ ] Intégration calendrier/email
- [ ] Commandes vocales rapides (timer, météo, calculs)

### **Intégrations**
- [ ] Home automation (contrôle dispositifs IoT)
- [ ] API externes (météo, news, etc.)
- [ ] Synchronisation cloud optionnelle

### **Optimisations**
- [ ] Cache intelligent des réponses fréquentes
- [ ] Mode offline partiel
- [ ] Déploiement Raspberry Pi
- [ ] Tests de charge et performance

---

## 📂 Structure du Projet

```
Projet_P3/
├── frontend/              # Vue.js 3 + TypeScript + Element Plus
│   ├── src/
│   │   ├── components/   # Atomic Design
│   │   │   ├── atoms/         # BaseButton, BaseBadge, etc.
│   │   │   ├── molecules/     # StatCard, MessageBubble, etc.
│   │   │   └── organisms/     # VoiceRecorder, ConversationSidebar, etc.
│   │   ├── stores/       # Pinia (conversation store)
│   │   ├── services/     # API client (axios)
│   │   ├── types/        # TypeScript types
│   │   └── App.vue
│   └── Dockerfile
│
├── backend/              # FastAPI + Python 3.11
│   ├── src/
│   │   ├── api/         # Layered Architecture
│   │   │   ├── routes/       # voice, knowledge, conversations, health
│   │   │   └── main.py       # FastAPI app
│   │   ├── core/        # Configuration & Database
│   │   │   ├── config.py     # Settings (Pydantic)
│   │   │   └── database.py   # SQLAlchemy setup
│   │   ├── models/      # Pydantic & SQLAlchemy models
│   │   │   ├── requests.py
│   │   │   ├── responses.py
│   │   │   └── db_models.py  # Conversation, Message
│   │   ├── services/    # Business Logic
│   │   │   ├── voice_service.py
│   │   │   └── conversation_service.py
│   │   ├── repositories/  # Data Access
│   │   │   └── conversation_repository.py
│   │   ├── agents/      # jarvis_agent.py (OpenRouter)
│   │   ├── voice/       # stt.py (Groq) + tts.py (Edge TTS)
│   │   ├── graph/       # Graphiti integration (en attente)
│   │   └── code_analysis/  # Analyseur de code (bonus)
│   ├── tests/           # Tests pytest
│   │   ├── conftest.py
│   │   └── services/
│   ├── notebooks/       # Jupyter notebooks de test
│   ├── config/          # Configurations et schémas
│   ├── data/            # Données et graphes
│   └── Dockerfile
│
├── esp32/               # Firmware ESP32 (à développer)
│   └── src/
│
├── docs/                # Documentation
│   ├── ARCHITECTURE.md      # Layered Architecture
│   ├── TESTING.md           # Guide des tests
│   ├── QUICK_START.md       # Démarrage rapide
│   ├── WEB_INTERFACE.md     # Interface web
│   ├── START.md             # Guide 30 secondes
│   └── TODO.md              # Ce fichier
│
├── docker-compose.yml   # 4 services: frontend, backend, neo4j, postgres
├── Makefile            # Commandes utiles
├── CLAUDE.md           # Instructions pour Claude Code
└── README.md           # Point d'entrée principal
```

---

## 🛠️ Commandes Utiles

### Docker
```bash
make build          # Build les images
make up            # Lancer tous les services
make down          # Arrêter les services
make logs          # Voir les logs
make clean         # Nettoyer (⚠️ supprime les données)
```

### Accès aux Services
```bash
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs (Swagger): http://localhost:8000/docs
# Neo4j Browser: http://localhost:7474
# PostgreSQL: localhost:5432 (jarvis/jarvis2024)
# Jupyter Notebooks: http://localhost:8888
```

### Développement Backend
```bash
# Ajouter une dépendance
docker compose exec backend poetry add package-name

# Tests pytest
docker compose exec backend pytest

# Tests avec couverture
docker compose exec backend pytest --cov=src --cov-report=html

# Lancer Jupyter
docker compose exec backend jupyter notebook \
  --ip=0.0.0.0 --port=8888 --no-browser --allow-root

# Accéder au shell
docker compose exec backend bash
```

### Développement Frontend
```bash
# Installation
cd frontend && npm install

# Dev local (hors Docker)
npm run dev

# Build production
npm run build

# Type check
npm run type-check
```

### Database
```bash
# Accéder à PostgreSQL
docker compose exec postgres psql -U jarvis -d jarvis

# Voir les conversations
docker compose exec postgres psql -U jarvis -d jarvis \
  -c "SELECT id, name, created_at FROM conversations ORDER BY updated_at DESC;"

# Voir les messages
docker compose exec postgres psql -U jarvis -d jarvis \
  -c "SELECT * FROM messages WHERE conversation_id='...';"
```

---

## 🎯 Prochaines Étapes Recommandées

**Court terme (cette semaine):**
1. ✅ Système de conversations complet (fait)
2. ✅ Auto-nommage des conversations (fait)
3. Améliorer l'UI/UX (recherche, tags, export)
4. Ajouter plus de tests (routes API, repositories)

**Moyen terme (ce mois):**
1. Décider stratégie GraphRAG (Neo4j Enterprise vs alternative)
2. Implémenter extraction d'entités vocales
3. Tests d'intégration complets
4. Développer firmware ESP32 (si matériel reçu)

**Long terme (prochains mois):**
1. Wake word detection sur ESP32
2. Pipeline vocal ESP32 bout-en-bout
3. Multi-utilisateurs et fonctionnalités avancées
4. Home automation et intégrations externes

---

## 📊 Métriques de Performance

**Latences actuelles (mesuré):**
- STT (Groq Whisper): ~0.9s
- Agent (OpenRouter Claude): ~1-2s
- TTS (Edge TTS): ~0.5s
- **Total pipeline**: ~2.5-3.5s ✅ (objectif < 3s atteint)

**Couverture tests:**
- voice_service: 92% ✅
- Objectif global: >60%

---

## 📚 Ressources

### Documentation Projet
- [README.md](../README.md) - Vue d'ensemble et démarrage
- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture Layered en détail
- [TESTING.md](TESTING.md) - Guide des tests et notebooks
- [QUICK_START.md](QUICK_START.md) - Guide démarrage détaillé
- [WEB_INTERFACE.md](WEB_INTERFACE.md) - Interface web
- [START.md](START.md) - Démarrage ultra-rapide 30 secondes

### Technologies Externes
- **Graphiti**: https://github.com/getzep/graphiti
- **OpenRouter**: https://openrouter.ai/docs
- **Neo4j**: https://neo4j.com/docs/
- **Groq Whisper**: https://console.groq.com/docs/speech-text
- **Edge TTS**: https://github.com/rany2/edge-tts
- **ESP32 Audio**: https://github.com/atomic14/esp32_audio

### Hardware
- **ESP32-S3 DevKit C** (recommandé pour I2S)
- **INMP441** I2S Digital Microphone
- **MAX98357A** I2S Amplifier
- **Speaker 4Ω 3W**
- **LED RGB** pour feedback visuel

---

## 🎉 Changelog Récent

### 2026-01-07
- ✅ Migration STT vers Groq Whisper (10x plus rapide)
- ✅ Refactoring complet Layered Architecture
- ✅ Ajout PostgreSQL pour persistence
- ✅ Système de conversations complet (CRUD)
- ✅ Auto-nommage des conversations depuis premier message
- ✅ Frontend avec ConversationSidebar
- ✅ Tests pytest + 5 Jupyter notebooks
- ✅ Documentation complète (ARCHITECTURE.md, TESTING.md)
- ✅ Nettoyage et organisation du projet

### 2026-01-06
- ✅ Tests Graphiti (limitations Neo4j Community identifiées)
- ✅ Pipeline vocal end-to-end fonctionnel
- ✅ Interface Vue.js moderne avec glassmorphism
- ✅ Docker Compose 3 services (ajout Neo4j)

---

**Projet opérationnel et prêt pour la phase suivante !** 🚀
