# 📓 Notebooks Jarvis - Guides Interactifs

Ce dossier contient des notebooks Jupyter pour tester et explorer chaque technologie du projet Jarvis.

## 🚀 Démarrage Rapide

```bash
# Depuis le container backend
docker compose exec backend jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root

# Ou localement
cd backend
jupyter notebook
```

## 📚 Notebooks Disponibles

### 1. **01_test_stt_groq.ipynb** - Speech-to-Text
- Teste Groq Whisper API
- Compare avec Whisper local
- Exemples audio de test

### 2. **02_test_tts_edge.ipynb** - Text-to-Speech  
- Teste Edge TTS
- Différentes voix françaises
- Génération audio

### 3. **03_test_agent_openrouter.ipynb** - Agent Conversationnel
- Teste OpenRouter avec Claude
- Exemples de conversations
- Gestion de l'historique

### 4. **04_test_neo4j_graphiti.ipynb** - Knowledge Graph
- Connexion Neo4j
- Opérations Graphiti
- Visualisation du graphe

### 5. **05_pipeline_complet.ipynb** - Pipeline End-to-End
- Pipeline vocal complet
- STT → Agent → TTS
- Test d'intégration

## 🎯 Utilisation

Chaque notebook est autonome et peut être exécuté indépendamment.

Les notebooks se connectent au backend Docker en cours d'exécution.

## 📝 Notes

- Les notebooks utilisent les mêmes configurations que le backend (`.env`)
- Assurez-vous que les services Docker sont lancés (`docker compose up`)
- Les fichiers audio de test sont générés automatiquement
