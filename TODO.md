# TODO - Jarvis: Assistant Vocal Intelligent

## ✅ Phase 1: Infrastructure de Base (COMPLÉTÉE)

- [x] Configuration Docker et docker-compose
- [x] Migration vers Poetry
- [x] Configuration Graphiti avec Neo4j
- [x] Structure de dossiers du projet
- [x] Documentation de base

---

## ✅ Phase 2: Backend API et Voice Processing (COMPLÉTÉE)

### ✅ Tâche 1: Configurer FastAPI et endpoints de base
- [x] Créer application FastAPI (src/api/main.py)
- [x] Endpoint `/health` pour health check
- [x] Endpoint `/api/voice/process` pour traitement vocal
- [x] Endpoint `/api/knowledge/query` pour requêtes
- [x] Configuration CORS pour ESP32
- [x] Interface web de test avec push-to-talk

### ✅ Tâche 2: Implémenter Speech-to-Text (STT)
- [x] Choix: Whisper local (gratuit, pas de clé) + Groq (alternatif)
- [x] Créer module STT (src/voice/stt.py)
- [x] Support format audio WebM
- [x] Transcription français/multilingue
- [x] Module WhisperLocalSTT et GroqSTT

### ✅ Tâche 3: Implémenter Text-to-Speech (TTS)
- [x] Choix: Edge TTS (gratuit, Microsoft)
- [x] Créer module TTS (src/voice/tts.py)
- [x] Génération audio MP3
- [x] Support voix françaises (Denise, Henri)
- [x] Module EdgeTTSProvider et CoquiTTSProvider

### ✅ Tâche 4: Créer l'agent conversationnel
- [x] Agent avec OpenRouter (src/agents/jarvis_agent.py)
- [x] Support Claude 3.5 Sonnet, GPT-4, Llama, etc.
- [x] Gestion historique conversationnel
- [x] Prompts système optimisés pour vocal

### ✅ Tâche 5: Interface web de test
- [x] Interface HTML/CSS/JS moderne (static/)
- [x] Bouton push-to-talk fonctionnel
- [x] Visualisation audio en temps réel
- [x] Affichage transcription et réponse
- [x] Player audio pour réponse vocale

### ✅ Tâche 6: Pipeline complet intégré
- [x] Audio → STT → Agent → TTS → Audio
- [x] Gestion fichiers temporaires
- [x] Logs détaillés de chaque étape
- [x] Configuration .env simplifiée

---

## ⏳ Phase 3: Tests et Validation (EN COURS)

### Tâche 7: Tester le pipeline complet
- [ ] Tester interface web avec vraie clé OpenRouter ✅ PRÊT
- [ ] Vérifier qualité transcription Whisper
- [ ] Vérifier qualité voix Edge TTS
- [ ] Tester différents modèles LLM
- [ ] Optimiser latence si nécessaire

---

## Phase 4: Knowledge Graph Personnel (À FAIRE)

### Tâche 8: Définir le schéma du graphe pour données personnelles
- [ ] Entités: Person, Event, Task, Note, Preference, Contact
- [ ] Relations: KNOWS, LIKES, SCHEDULED_FOR, RELATED_TO, MENTIONED_IN
- [ ] Propriétés temporelles (timestamps)
- [ ] Schéma de métadonnées conversationnelles
- [ ] Documentation du schéma (config/graph_schema_personal.yaml)

### Tâche 9: Créer les modèles Pydantic pour entités
- [ ] PersonModel (src/models/person.py)
- [ ] EventModel (anniversaires, rendez-vous)
- [ ] TaskModel (tâches, rappels)
- [ ] NoteModel (informations mémorisées)
- [ ] PreferenceModel (préférences utilisateur)
- [ ] Validation et sérialisation
- [ ] Tests unitaires des modèles

### Tâche 10: Implémenter extraction d'entités depuis texte
- [ ] Utiliser LLM pour extraction structurée
- [ ] Prompts pour identifier informations à mémoriser
- [ ] Détection de nouvelles vs mises à jour
- [ ] Résolution d'entités (merge de similaires)
- [ ] Pipeline d'extraction (src/graph/entity_extraction.py)
- [ ] Tests avec conversations exemples

### Tâche 11: Intégrer GraphRAG pour mémoire contextuelle
- [ ] Recherche sémantique dans le knowledge graph
- [ ] Récupération d'informations pertinentes
- [ ] Construction du contexte enrichi
- [ ] Ranking des résultats par pertinence
- [ ] Module GraphRAG (src/rag/memory_retrieval.py)
- [ ] Intégration dans l'agent

### Tâche 12: Implémenter mise à jour automatique du graphe
- [ ] Détection d'informations à mémoriser
- [ ] Ajout automatique au graphe post-conversation
- [ ] Système de confirmation pour infos importantes
- [ ] Versioning des modifications
- [ ] Module update (src/graph/auto_update.py)
- [ ] Tests de mise à jour

---

## Phase 5: ESP32 Voice Interface (EN ATTENTE MATÉRIEL)

### Tâche 13: Setup environnement ESP32
- [ ] Installer PlatformIO ou Arduino IDE
- [ ] Créer projet ESP32 (esp32/platformio.ini)
- [ ] Configurer pins pour I2S microphone
- [ ] Configurer pins pour speaker/amp
- [ ] Test basique LED/Serial

### Tâche 14: Implémenter capture audio sur ESP32
- [ ] Driver I2S pour microphone
- [ ] Buffer audio circulaire
- [ ] Format PCM 16kHz mono
- [ ] Détection de silence (VAD basique)
- [ ] Code: esp32/src/audio_capture.cpp
- [ ] Tests capture et sauvegarde SD

### Tâche 15: Implémenter lecture audio sur ESP32
- [ ] Driver I2S pour speaker/DAC
- [ ] Décodage MP3/WAV
- [ ] Contrôle volume
- [ ] Buffer de lecture
- [ ] Code: esp32/src/audio_playback.cpp
- [ ] Tests lecture fichiers

### Tâche 16: Wake word detection
- [ ] Choisir solution (Porcupine, Edge Impulse, custom)
- [ ] Entraîner modèle "Hey Jarvis"
- [ ] Intégration sur ESP32
- [ ] Détection locale sans cloud
- [ ] LED feedback visuel
- [ ] Tests de précision

### Tâche 17: Communication WiFi ESP32 <-> Backend
- [ ] Gestionnaire WiFi (WiFiManager)
- [ ] Client HTTP pour upload audio
- [ ] Réception réponse audio
- [ ] Gestion timeout et reconnexion
- [ ] Code: esp32/src/wifi_manager.cpp
- [ ] Tests communication

### Tâche 18: Pipeline vocal complet ESP32
- [ ] Intégrer wake word → capture → upload → process → download → play
- [ ] Gestion des états (idle, listening, processing, speaking)
- [ ] LED indicators pour feedback utilisateur
- [ ] Optimisation latence end-to-end
- [ ] Code: esp32/src/main.cpp
- [ ] Tests bout en bout

---

## Phase 6: Améliorations et Optimisations (FUTUR)

### Interface de monitoring (optionnel)
- [ ] Dashboard Streamlit pour visualiser graphe
- [ ] Historique des conversations
- [ ] Statistiques d'utilisation
- [ ] Édition manuelle du knowledge graph
- [ ] Code: src/ui/dashboard.py

### Fonctionnalités avancées
- [ ] Support multi-utilisateurs (reconnaissance vocale)
- [ ] Intégration home automation (contrôle IoT)
- [ ] Routines et automatisations
- [ ] Notifications proactives
- [ ] Support multilingue amélioré
- [ ] Mode conversation continue
- [ ] Intégration calendrier/email
- [ ] Commandes vocales rapides (timer, météo, etc.)

### Optimisations
- [ ] Modèle Whisper quantifié local (plus rapide)
- [ ] Cache intelligent des réponses
- [ ] Compression audio optimale
- [ ] Mode offline partiel
- [ ] Déploiement sur Raspberry Pi

---

## 📊 Décisions Techniques

### ✅ Backend (DÉCIDÉ)
- [x] Architecture: Docker + Poetry
- [x] Database: Neo4j
- [x] API: FastAPI
- [x] STT: Whisper local (+ Groq en alternatif)
- [x] TTS: Edge TTS (gratuit, excellente qualité)
- [x] LLM: OpenRouter (Claude 3.5 Sonnet recommandé)

### ⏳ ESP32 (À DÉCIDER)
- [ ] Board: ESP32-S3 (recommandé pour I2S) vs ESP32-WROOM?
- [ ] Microphone: INMP441 I2S vs PDM?
- [ ] Speaker: MAX98357A I2S vs DAC simple?
- [ ] Wake word: Porcupine vs Edge Impulse vs custom?
- [ ] IDE: PlatformIO (recommandé) vs Arduino?

### ⏳ Audio ESP32 (À DÉCIDER)
- [ ] Format upload: WAV vs PCM raw?
- [ ] Format download: MP3 vs WAV vs Opus?
- [ ] Sample rate: 16kHz vs 8kHz?
- [ ] Streaming: HTTP chunks vs WebSocket?

---

## 🛠️ État Actuel du Projet

### ✅ Fonctionnel Maintenant
1. Interface web http://localhost:8000
2. Enregistrement audio via microphone navigateur
3. Transcription avec Whisper local
4. Agent conversationnel via OpenRouter
5. Synthèse vocale avec Edge TTS
6. Pipeline complet Audio → Texte → Réponse → Audio

### 🎯 Prochaine Étape Recommandée
**Tester le système complet !**
1. Lancer `make build && make up`
2. Ouvrir http://localhost:8000
3. Tester différentes conversations
4. Valider qualité STT/TTS
5. Optimiser si nécessaire

### 📦 En Attente
- Matériel ESP32 (commandé)
- Intégration Graphiti/GraphRAG pour mémoire

---

## 📚 Ressources

### Documentation
- [START.md](START.md) - Guide démarrage rapide
- [QUICK_START.md](docs/QUICK_START.md) - Configuration détaillée
- [WEB_INTERFACE.md](docs/WEB_INTERFACE.md) - Interface web

### ESP32
- ESP32 I2S Audio: https://github.com/atomic14/esp32_audio
- ESP32 Wake Word: https://github.com/Picovoice/porcupine
- Audio Processing: https://github.com/espressif/esp-adf

### GraphRAG
- Graphiti Docs: https://github.com/getzep/graphiti
- LangChain Memory: https://python.langchain.com/docs/modules/memory/

### Hardware Shopping List
- ESP32-S3 DevKit C (recommandé)
- INMP441 I2S Microphone
- MAX98357A I2S Amplifier
- Speaker 4Ω 3W
- LED RGB pour feedback
- Câbles Dupont femelle-femelle
- Breadboard 830 points
