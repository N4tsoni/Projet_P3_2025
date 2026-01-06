# TODO - Jarvis Assistant Vocal

> Version simplifiée et à jour du projet - Dernière mise à jour: 2026-01-06

---

## 🎯 État Actuel

### ✅ **Fonctionnel** (Phase 1-3 complétées)

**Infrastructure:**
- [x] Docker + Docker Compose (3 services: frontend, backend, neo4j)
- [x] Poetry pour gestion dépendances Python
- [x] Configuration .env simplifiée

**Frontend Vue.js 3:**
- [x] Interface moderne avec TypeScript + Element Plus
- [x] Atomic Design (atoms, molecules, organisms, templates)
- [x] Glassmorphism et animations
- [x] VoiceRecorder avec push-to-talk et visualisation audio
- [x] Historique des conversations
- [x] Visualisation du knowledge graph (préparé)
- [x] Responsive design

**Backend FastAPI:**
- [x] API REST complète (`/api/voice/process`, `/api/knowledge/*`)
- [x] Speech-to-Text: Whisper local (gratuit)
- [x] Agent: OpenRouter avec Claude 3.5 Sonnet
- [x] Text-to-Speech: Edge TTS (gratuit, voix fr-FR-DeniseNeural)
- [x] Pipeline vocal complet: Audio → STT → Agent → TTS → Audio

**Code Analysis (nouveau):**
- [x] Analyseur de code Python (`backend/src/code_analysis/`)
- [x] Entity extractor pour code
- [x] Parser AST Python
- [x] Intégration Graphiti pour code graph

---

## 🔄 En Cours (Phase 4)

### **Knowledge Graph & GraphRAG**

**Priorité 1: Intégration Graphiti pour Conversations**
- [ ] Schéma du graphe pour entités conversationnelles
  - Person, Event, Task, Note, Preference, Contact
  - Relations: KNOWS, LIKES, SCHEDULED_FOR, RELATED_TO
- [ ] Modèles Pydantic pour entités personnelles
- [ ] Extraction automatique d'entités depuis transcriptions vocales
- [ ] Mise à jour du graphe post-conversation
- [ ] GraphRAG: Recherche sémantique dans le knowledge graph
- [ ] Enrichissement du contexte de l'agent avec infos du graphe

**Priorité 2: Tests & Validation**
- [ ] Tests unitaires pour modules vocaux (STT, TTS)
- [ ] Tests d'intégration du pipeline complet
- [ ] Tests de l'analyseur de code
- [ ] Optimisation latence (objectif < 3s end-to-end)

---

## 📦 Planifié (Phase 5+)

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
- [ ] Mode conversation continue (sans push-to-talk)
- [ ] Raccourcis clavier pour interface web
- [ ] Export/import des conversations
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
- [ ] Modèle Whisper quantifié (inference plus rapide)
- [ ] Cache intelligent des réponses fréquentes
- [ ] Mode offline partiel
- [ ] Déploiement Raspberry Pi

---

## 📂 Structure du Projet

```
Projet_P3/
├── frontend/              # Vue.js 3 + TypeScript + Element Plus
│   ├── src/
│   │   ├── components/   # Atomic Design (atoms, molecules, organisms)
│   │   ├── stores/       # Pinia (state management)
│   │   ├── services/     # API client (axios)
│   │   ├── types/        # TypeScript types
│   │   └── App.vue
│   └── Dockerfile
│
├── backend/              # FastAPI + Python 3.11
│   ├── src/
│   │   ├── api/         # Routes REST
│   │   ├── agents/      # jarvis_agent.py (OpenRouter)
│   │   ├── voice/       # stt.py (Whisper) + tts.py (Edge TTS)
│   │   ├── code_analysis/  # Analyseur de code (nouveau)
│   │   ├── graph/       # Graphiti integration (à finaliser)
│   │   ├── models/      # Pydantic models
│   │   └── main.py
│   ├── config/          # Configurations et schémas
│   ├── data/            # Données et graphes
│   └── Dockerfile
│
├── esp32/               # Firmware ESP32 (à développer)
│   └── src/
│
├── docs/                # Documentation
│   ├── QUICK_START.md
│   └── WEB_INTERFACE.md
│
├── docker-compose.yml   # 3 services: frontend, backend, neo4j
├── Makefile            # Commandes utiles
├── ARCHITECTURE.md     # Architecture technique détaillée
├── CLAUDE.md           # Instructions pour Claude Code
├── README.md           # Point d'entrée principal
└── TODO.md             # Ce fichier
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
# API Docs: http://localhost:8000/docs
# Neo4j Browser: http://localhost:7474
```

### Développement
```bash
# Backend - Ajouter une dépendance
docker-compose exec backend poetry add package-name

# Backend - Tests
docker-compose exec backend poetry run pytest

# Frontend - Installation
cd frontend && npm install

# Frontend - Dev
npm run dev
```

---

## 🎯 Prochaines Étapes Recommandées

**Court terme (cette semaine):**
1. ✅ Nettoyer et organiser le projet (fait)
2. Finaliser intégration Graphiti pour conversations
3. Implémenter extraction d'entités vocales
4. Tester GraphRAG avec vraies conversations

**Moyen terme (ce mois):**
1. Tests unitaires et d'intégration complets
2. Optimisation performance (< 3s latence)
3. Documentation API complète
4. Développer firmware ESP32 (si matériel reçu)

**Long terme (prochains mois):**
1. Wake word detection sur ESP32
2. Pipeline vocal ESP32 bout-en-bout
3. Multi-utilisateurs et fonctionnalités avancées
4. Home automation et intégrations externes

---

## 📚 Ressources

### Documentation Projet
- [README.md](README.md) - Vue d'ensemble et démarrage
- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture technique
- [docs/QUICK_START.md](docs/QUICK_START.md) - Guide détaillé
- [docs/WEB_INTERFACE.md](docs/WEB_INTERFACE.md) - Interface web

### Technologies Externes
- **Graphiti**: https://github.com/getzep/graphiti
- **OpenRouter**: https://openrouter.ai/docs
- **Neo4j**: https://neo4j.com/docs/
- **Whisper**: https://github.com/openai/whisper
- **ESP32 Audio**: https://github.com/atomic14/esp32_audio

### Hardware
- **ESP32-S3 DevKit C** (recommandé pour I2S)
- **INMP441** I2S Digital Microphone
- **MAX98357A** I2S Amplifier
- **Speaker 4Ω 3W**
- **LED RGB** pour feedback visuel
