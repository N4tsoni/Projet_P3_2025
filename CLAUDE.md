# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Assistant vocal intelligent type "Jarvis" utilisant GraphRAG et Graphiti avec interface ESP32.

### Objectif
Créer un assistant personnel vocal qui utilise GraphRAG (Graph Retrieval-Augmented Generation) avec un knowledge graph dynamique pour mémoriser et raisonner sur les informations personnelles fournies en conversation. L'assistant communique via un ESP32 avec capacités vocales.

### Technologies Clés

**Backend (✅ Opérationnel):**
- **Docker & Docker Compose**: Containerisation et orchestration des services
- **Poetry**: Gestion moderne des dépendances Python
- **FastAPI**: API REST pour communication avec ESP32
- **OpenRouter**: Accès à 100+ modèles LLM (Claude, GPT-4, Llama, etc.)
- **Graphiti**: Framework pour knowledge graphs dynamiques (à intégrer)
- **GraphRAG**: Recherche augmentée par graphe de connaissances (à intégrer)
- **Neo4j**: Base de données graphe (containerisée)
- **Python 3.10+**: Langage principal

**Vocal & Audio (✅ Opérationnel):**
- **Whisper Local**: Reconnaissance vocale gratuite (OpenAI open-source)
- **Groq**: Alternative STT rapide et gratuite (optionnel)
- **Edge TTS**: Synthèse vocale gratuite Microsoft (voix fr-FR-DeniseNeural)
- **Coqui TTS**: Alternative TTS locale (optionnel)

**Interface (✅ Opérationnel):**
- **Interface Web**: HTML/CSS/JS moderne avec push-to-talk
- **MediaRecorder API**: Capture audio navigateur
- **Web Audio API**: Visualisation waveform

**Hardware (📦 En commande):**
- **ESP32**: Microcontrôleur avec WiFi/Bluetooth
- **Microphone I2S**: Capture audio haute qualité
- **Amplificateur + Speaker**: Sortie audio
- **Wake word detection**: À implémenter (Porcupine ou Edge Impulse)

## Architecture

### Composants Principaux

1. **ESP32 Voice Interface**
   - Capture audio via microphone I2S
   - Wake word detection locale ("Hey Jarvis")
   - Envoi audio vers backend via WiFi
   - Réception et lecture de la réponse audio

2. **Backend API (FastAPI)**
   - `/api/voice/process`: Endpoint pour traitement vocal
   - `/api/knowledge/add`: Ajout manuel de connaissances
   - `/api/knowledge/query`: Requêtes sur le knowledge graph
   - WebSocket pour streaming audio (optionnel)

3. **Voice Processing Pipeline**
   - Speech-to-Text (Whisper/Google STT): Audio → Texte
   - Agent conversationnel: Traitement de la requête
   - Text-to-Speech (TTS): Réponse → Audio
   - Retour vers ESP32

4. **Knowledge Graph Dynamique (Graphiti)**
   - Entités personnelles: Préférences, Contacts, Événements, Tâches, Notes
   - Relations: Liens entre concepts et informations
   - Mise à jour automatique depuis conversations
   - Extraction d'entités depuis transcriptions

5. **Agent Conversationnel GraphRAG**
   - Compréhension du contexte conversationnel
   - Recherche sémantique dans le knowledge graph
   - Génération de réponses personnalisées
   - Mémorisation des nouvelles informations

## Structure du Projet

```
Projet_P3/
├── src/
│   ├── api/            # FastAPI endpoints
│   ├── graph/          # Gestion du knowledge graph (Graphiti)
│   ├── rag/            # Système GraphRAG
│   ├── agents/         # Agent conversationnel
│   ├── voice/          # Speech-to-Text et Text-to-Speech
│   ├── wake_word/      # Wake word detection
│   └── models/         # Modèles de données (Pydantic)
├── esp32/              # Code Arduino/PlatformIO pour ESP32
│   ├── src/
│   │   ├── audio_capture.cpp
│   │   ├── wifi_manager.cpp
│   │   └── main.cpp
│   └── platformio.ini
├── tests/              # Tests unitaires et d'intégration
├── data/               # Données d'exemple et knowledge graph
├── notebooks/          # Jupyter notebooks pour exploration
├── config/             # Fichiers de configuration
└── docs/               # Documentation
```

## État Actuel du Projet

### ✅ Fonctionnalités Complétées

**Interface Web de Test:**
- Interface moderne à http://localhost:8000
- Bouton push-to-talk fonctionnel
- Visualisation audio temps réel
- Affichage transcription et réponse
- Lecture audio de la réponse

**Pipeline Vocal Complet:**
- STT: Whisper local (gratuit, pas de clé API)
- Agent: OpenRouter avec Claude 3.5 Sonnet
- TTS: Edge TTS (gratuit, voix françaises)
- Integration complète dans FastAPI

**Configuration:**
- `.env` simplifié (10 lignes essentielles)
- Docker + Poetry
- Neo4j pour Graphiti
- Prêt à utiliser

### 🎯 Prochaines Étapes

1. **Immédiat**: Tester le pipeline complet via interface web
2. **Court terme**: Intégrer Graphiti pour mémoire persistante
3. **Moyen terme**: Développer firmware ESP32 (matériel en commande)
4. **Long terme**: Fonctionnalités avancées (multi-user, home automation)

## Commandes de Développement

### Docker
```bash
# Build des images
docker-compose build

# Lancer tous les services
docker-compose up

# Lancer en arrière-plan
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down

# Arrêter et supprimer volumes (⚠️ perte de données)
docker-compose down -v
```

### Développement
```bash
# Accéder au container de l'app
docker-compose exec app bash

# Ajouter une dépendance
docker-compose exec app poetry add package-name

# Ajouter une dépendance de dev
docker-compose exec app poetry add --group dev package-name

# Exécuter les tests
docker-compose exec app poetry run pytest

# Lancer l'application
docker-compose exec app poetry run python src/main.py

# Formater le code
docker-compose exec app poetry run black src/
docker-compose exec app poetry run ruff check src/

# Type checking
docker-compose exec app poetry run mypy src/
```

### Neo4j
- Interface web: http://localhost:7474
- Bolt: bolt://localhost:7687
- Credentials: voir .env

## Démarrage Rapide

### Pour Tester Maintenant

1. **Vérifier .env**: Votre clé OpenRouter doit être configurée
2. **Lancer**: `make build && make up`
3. **Ouvrir**: http://localhost:8000
4. **Tester**: Maintenir bouton microphone, parler, relâcher

### Fichiers Importants

- `START.md` - Guide démarrage ultra-rapide
- `TODO.md` - Liste complète des tâches et progression
- `docs/QUICK_START.md` - Configuration détaillée
- `docs/WEB_INTERFACE.md` - Documentation interface web

## Workflow de Développement

1. Vérifier TODO.md pour les tâches en cours
2. Développer en suivant l'architecture modulaire
3. Tester chaque composant individuellement
4. Utiliser `make test` pour valider
5. Intégrer progressivement les modules

## Domaine: Assistant Personnel

L'assistant doit gérer:
- **Informations personnelles**: Préférences, habitudes, contacts
- **Événements**: Rendez-vous, anniversaires, rappels
- **Connaissances**: Faits mémorisés, conversations passées
- **Tâches**: Todo list, projets, objectifs
- **Contexte conversationnel**: Comprendre les références et le contexte
- **Home automation** (futur): Contrôle de dispositifs IoT

## Communication avec ESP32

### Flow de conversation vocale

1. **Wake Word**: ESP32 détecte "Hey Jarvis" localement
2. **Enregistrement**: Capture audio de la question
3. **Upload**: Envoi audio au backend via HTTP POST
4. **Traitement**:
   - STT: Audio → Texte
   - Agent: Recherche GraphRAG + Génération réponse
   - Mise à jour graphe si nouvelles infos
   - TTS: Texte → Audio
5. **Download**: ESP32 reçoit l'audio de réponse
6. **Lecture**: Diffusion de la réponse

### Formats de communication

- **Audio upload**: WAV/PCM 16kHz mono
- **Audio download**: MP3 ou WAV compressé
- **Protocol**: HTTP/REST ou WebSocket pour streaming
