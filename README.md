# 🤖 Jarvis - Assistant Vocal Intelligent avec GraphRAG

> Assistant personnel vocal type "Jarvis" utilisant GraphRAG et Graphiti avec interface web et ESP32 (à venir)

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
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
- [Contribution](#-contribution)

---

## 🎯 Vue d'Ensemble

**Jarvis** est un assistant vocal intelligent qui mémorise vos conversations grâce à un **knowledge graph dynamique** (GraphRAG + Graphiti). Il combine:

- 🎤 **Reconnaissance vocale** (Whisper local - gratuit)
- 🧠 **Agent conversationnel** (Claude 3.5 Sonnet via OpenRouter)
- 🔊 **Synthèse vocale** (Edge TTS Microsoft - gratuit)
- 🕸️ **Knowledge Graph** (Neo4j + Graphiti)
- 🌐 **Interface web** moderne avec push-to-talk
- 📡 **ESP32** (à venir) pour interaction vocale physique

### Cas d'Usage

- Assistant personnel qui se souvient de vos préférences
- Gestion de tâches et rappels contextuels
- Conversations naturelles avec mémoire à long terme
- Base de connaissances personnelle interrogeable

---

## ✅ État Actuel

### **Phase 2-3: OPÉRATIONNEL** ✅

Le pipeline vocal complet est **fonctionnel et testé**:

```
Audio → Whisper STT → Claude Agent → Edge TTS → Audio Response
```

**Ce qui fonctionne aujourd'hui:**
- ✅ Interface web avec push-to-talk (http://localhost:8000)
- ✅ Transcription vocale en français (Whisper local)
- ✅ Agent conversationnel intelligent (Claude via OpenRouter)
- ✅ Synthèse vocale en français (Edge TTS - voix Denise)
- ✅ Visualisation waveform temps réel
- ✅ Docker + Docker Compose configuré
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
- Ports **7474**, **7687**, et **8000** disponibles

### Installation (5 minutes)

```bash
# 1. Cloner le repository
git clone <repository-url>
cd Projet_P3

# 2. Vérifier que le .env contient votre clé OpenRouter
cat .env
# OPENROUTER_API_KEY=sk-or-v1-xxxxx (remplacez par votre clé)

# 3. Lancer avec Docker
docker compose build
docker compose up -d

# 4. Vérifier que tout fonctionne
docker compose ps
# Devrait afficher graphrag-neo4j (healthy) et graphrag-app (running)
```

### Utilisation

1. **Ouvrir l'interface**: http://localhost:8000
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
| **Interface Web** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Neo4j Browser** | http://localhost:7474 | neo4j / graphrag2024 |
| **API Health** | http://localhost:8000/health | - |

---

## 🏗️ Architecture

### Pipeline Vocal (Fonctionnel)

```
┌─────────────────┐
│  Web Interface  │  Push-to-talk, Waveform visualization
│   (HTML/JS)     │
└────────┬────────┘
         │ WebM audio (16kHz mono)
         ▼
┌─────────────────┐
│   FastAPI API   │  POST /api/voice/process
│   (src/api)     │
└────────┬────────┘
         │
    ┌────┴─────────────────────┐
    │                          │
    ▼                          ▼
┌──────────┐           ┌──────────────┐
│ Whisper  │           │  Edge TTS    │
│   STT    │           │     TTS      │
│(src/voice│           │ (src/voice)  │
└────┬─────┘           └──────▲───────┘
     │                        │
     │ "Bonjour Jarvis"       │ MP3 audio
     │                        │
     ▼                        │
┌────────────────────────────┴──┐
│   Claude 3.5 Sonnet Agent     │
│      (src/agents)             │
│   via OpenRouter              │
└───────────────────────────────┘
```

### Knowledge Graph (En intégration)

```
┌──────────────────┐
│  Conversations   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐      ┌─────────────┐
│    Graphiti      │◄────►│   Neo4j     │
│  (src/graph)     │      │  Database   │
└────────┬─────────┘      └─────────────┘
         │
         ▼
┌──────────────────┐
│   Entities &     │  Person, Event, Task,
│   Relations      │  Preference, Note
└──────────────────┘
```

### Structure des Fichiers

```
Projet_P3/
├── src/                          # Code source (959 lignes)
│   ├── main.py                   # Point d'entrée (26 lignes)
│   ├── api/
│   │   └── main.py              # FastAPI app (188 lignes)
│   ├── agents/
│   │   └── jarvis_agent.py      # Agent conversationnel (144 lignes)
│   ├── voice/
│   │   ├── stt.py               # Speech-to-Text (177 lignes)
│   │   └── tts.py               # Text-to-Speech (161 lignes)
│   ├── graph/
│   │   ├── graphiti_client.py   # Knowledge graph (170 lignes)
│   │   └── test_connection.py   # Tests connexion (93 lignes)
│   ├── models/                  # Modèles Pydantic (à implémenter)
│   ├── rag/                     # GraphRAG (à implémenter)
│   └── tools/                   # Outils agent (à implémenter)
├── static/
│   ├── index.html               # Interface web (244 lignes)
│   └── app.js                   # Frontend logic (237 lignes)
├── tests/                       # Tests (à implémenter)
├── esp32/                       # Firmware ESP32 (à implémenter)
├── config/
│   └── graphiti_config.yaml     # Config Graphiti
├── docs/
│   ├── QUICK_START.md           # Guide démarrage
│   └── WEB_INTERFACE.md         # Doc interface web
├── docker-compose.yml           # Orchestration services
├── Dockerfile                   # Image Python 3.11
├── pyproject.toml              # Dépendances Poetry
├── Makefile                    # Commandes dev
├── .env                        # Configuration
├── TODO.md                     # Roadmap détaillée
├── CLAUDE.md                   # Instructions techniques
└── README.md                   # Ce fichier
```

---

## 🛠️ Technologies

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

### Frontend

- **HTML5** + **CSS3** (design moderne avec gradients)
- **Vanilla JavaScript** (pas de framework)
- **MediaRecorder API** (capture audio)
- **Canvas API** (visualisation waveform)

### Hardware (Planifié)

- **ESP32** (WiFi/Bluetooth)
- **Microphone I2S** INMP441
- **Amplificateur I2S** MAX98357A
- **Speaker** 3W 4Ω

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[START.md](START.md)** | Guide démarrage ultra-rapide (5 min) |
| **[TODO.md](TODO.md)** | Roadmap complète et progression |
| **[CLAUDE.md](CLAUDE.md)** | Instructions techniques pour Claude |
| **[docs/QUICK_START.md](docs/QUICK_START.md)** | Configuration détaillée |
| **[docs/WEB_INTERFACE.md](docs/WEB_INTERFACE.md)** | Documentation interface web |

---

## 💻 Développement

### Commandes Makefile

```bash
# Démarrage
make build              # Build Docker images
make up                 # Lancer les services
make down               # Arrêter les services
make restart            # Redémarrer

# Logs
make logs               # Tous les logs
make logs-app           # Logs application seulement
make logs-neo4j         # Logs Neo4j seulement

# Développement
make shell              # Accéder au container
make test               # Exécuter tests
make test-connection    # Tester connexion Neo4j/Graphiti

# Qualité code
make format             # Formater avec Black
make lint               # Vérifier avec Ruff
make lint-fix           # Auto-fix Ruff
make type-check         # Type checking MyPy
make quality            # format + lint + type-check

# Nettoyage
make clean              # Nettoyer fichiers temp
make clean-docker       # Supprimer volumes Docker (⚠️ perte données)
make reset              # Reset complet projet
```

### Développement Local (sans Docker)

Pour un développement plus rapide sans rebuild Docker:

```bash
# 1. Installer Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 2. Installer les dépendances
poetry install

# 3. Garder Neo4j en Docker
docker compose up neo4j -d

# 4. Modifier .env pour pointer vers localhost
# NEO4J_URI=bolt://localhost:7687

# 5. Lancer l'app localement
poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Avantages**: Hot-reload instantané, pas de rebuild, debug plus facile.

### Ajouter des Dépendances

```bash
# Avec Docker
docker compose exec app poetry add package-name
docker compose exec app poetry add --group dev package-dev

# Avec Poetry local
poetry add package-name
poetry add --group dev package-dev
```

### Configuration

Toute la configuration se fait via `.env`:

```bash
# Neo4j (requis)
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=graphrag2024

# OpenRouter (requis - obtenez une clé sur openrouter.ai)
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Modèle LLM (modifiable)
LLM_MODEL=anthropic/claude-3.5-sonnet
# Alternatives: meta-llama/llama-3.1-70b-instruct, google/gemini-flash-1.5

# Speech-to-Text (modifiable)
STT_PROVIDER=whisper-local  # ou "groq"
STT_MODEL=base              # tiny, base, small, medium, large

# Text-to-Speech (modifiable)
TTS_PROVIDER=edge-tts       # ou "coqui-tts"
TTS_VOICE=fr-FR-DeniseNeural  # ou fr-FR-HenriNeural (homme)

# Logging
LOG_LEVEL=INFO
```

---

## 🗺️ Roadmap

### Phase 1: Infrastructure ✅ (Complété)

- [x] Configuration Docker + Docker Compose
- [x] Neo4j containerisé avec APOC
- [x] Structure projet avec Poetry
- [x] Configuration environnement (.env)

### Phase 2: Backend API ✅ (Complété)

- [x] FastAPI avec endpoints voice/process
- [x] Intégration Neo4j driver
- [x] Client Graphiti basique
- [x] Logging avec Loguru
- [x] CORS pour ESP32

### Phase 3: Voice Processing ✅ (Complété)

- [x] Whisper local STT (gratuit)
- [x] Edge TTS synthèse vocale (gratuit)
- [x] Agent conversationnel OpenRouter
- [x] Pipeline complet audio → texte → réponse → audio
- [x] Interface web avec push-to-talk
- [x] Visualisation waveform temps réel

### Phase 4: Knowledge Graph 🔄 (En cours)

- [ ] Définir schéma entités personnelles (Person, Event, Task, Preference, Note)
- [ ] Extraction automatique entités depuis conversations
- [ ] Mise à jour automatique knowledge graph après chaque conversation
- [ ] Implémentation GraphRAG pour enrichissement contexte
- [ ] Recherche sémantique dans le graphe
- [ ] Modèles Pydantic pour entités

### Phase 5: ESP32 Hardware 📦 (Matériel en commande)

- [ ] Firmware ESP32 avec wake word detection
- [ ] Driver microphone I2S
- [ ] Driver speaker I2S
- [ ] Communication WiFi avec backend
- [ ] Upload/download audio
- [ ] LED feedback

### Phase 6: Fonctionnalités Avancées 📦

- [ ] Multi-utilisateurs
- [ ] Home automation (MQTT/Zigbee)
- [ ] Tests unitaires et d'intégration
- [ ] CI/CD
- [ ] Monitoring et métriques

**Voir [TODO.md](TODO.md) pour les détails complets.**

---

## 🧪 Tests

```bash
# Tests connexion Neo4j/Graphiti
make test-connection

# Tests unitaires (à implémenter)
make test

# Tests avec coverage (à implémenter)
make test-cov
```

---

## 🐛 Dépannage

### Neo4j ne démarre pas

```bash
# Vérifier les logs
docker compose logs neo4j

# Nettoyer et redémarrer
docker compose down
docker compose up -d
```

### L'app ne se connecte pas à Neo4j

```bash
# Vérifier que Neo4j est healthy
docker compose ps

# Tester la connexion
make test-connection
```

### Erreur "OpenRouter API key not configured"

Vérifiez que `.env` contient:
```
OPENROUTER_API_KEY=sk-or-v1-votre-vraie-clé
```

Obtenez une clé sur https://openrouter.ai

### Whisper est lent

```bash
# Utiliser un modèle plus petit dans .env
STT_MODEL=tiny  # ou base (actuel), small, medium, large

# Ou passer à Groq (cloud, gratuit)
STT_PROVIDER=groq
GROQ_API_KEY=votre-clé-groq
```

---

## 🤝 Contribution

Les contributions sont bienvenues! Voir les issues GitHub pour les tâches disponibles.

### Workflow

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Standards Code

- **Black** pour le formatage (line length 100)
- **Ruff** pour le linting
- **MyPy** pour le type checking
- **Pytest** pour les tests

```bash
# Vérifier avant commit
make quality
```

---

## 📄 Licence

MIT License - voir [LICENSE](LICENSE) pour les détails.

---

## 🙏 Remerciements

- **OpenAI Whisper** pour le STT open-source
- **Microsoft Edge TTS** pour la synthèse vocale gratuite
- **OpenRouter** pour l'accès unifié aux LLMs
- **Anthropic Claude** pour les capacités conversationnelles
- **Neo4j** pour la base de données graphe
- **Graphiti** pour le framework knowledge graph

---

## 📞 Support

- **Documentation**: Voir dossier `docs/`
- **Issues**: Ouvrir un ticket GitHub
- **Questions**: Voir [CLAUDE.md](CLAUDE.md) pour les détails techniques

---

**Fait avec ❤️ pour créer un véritable assistant personnel intelligent**
