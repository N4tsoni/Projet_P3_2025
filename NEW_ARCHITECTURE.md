# Nouvelle Architecture Jarvis - Frontend/Backend Séparé

## 🎯 Architecture

Le projet a été restructuré avec une séparation claire entre frontend et backend :

```
Projet_P3/
├── frontend/              # Vue.js + Vite + TypeScript + Element Plus
│   ├── src/
│   │   ├── components/   # VoiceRecorder, ConversationHistory, KnowledgeGraphViz
│   │   ├── stores/       # Pinia stores (conversation)
│   │   ├── services/     # API client (axios)
│   │   ├── types/        # TypeScript types
│   │   ├── App.vue       # Application principale
│   │   └── main.ts       # Point d'entrée
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
│
├── backend/              # FastAPI + Python
│   ├── src/
│   │   ├── api/         # Routes FastAPI
│   │   ├── agents/      # Agent conversationnel
│   │   ├── voice/       # STT (Whisper) + TTS (Edge TTS)
│   │   ├── graph/       # Graphiti + Neo4j
│   │   └── models/      # Pydantic models
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── .env
│
├── docker-compose.yml    # 3 services: frontend (5173), backend (8000), neo4j
├── Makefile             # Commandes utiles
└── docs/
```

## 🛠️ Stack Technique

### Frontend
- **Vue 3** - Framework JavaScript progressif
- **Vite** - Build tool ultra-rapide avec HMR
- **TypeScript** - Type safety et meilleure DX
- **Element Plus** - Composants UI riches et modernes
- **Pinia** - State management officiel pour Vue 3
- **Axios** - Client HTTP pour l'API

### Backend
- **FastAPI** - Framework web Python moderne et performant
- **Whisper Local** - STT gratuit (OpenAI open-source)
- **Edge TTS** - TTS gratuit (Microsoft)
- **OpenRouter** - Accès à 100+ modèles LLM
- **Graphiti** - Knowledge graph dynamique (à intégrer)
- **Neo4j** - Base de données graphe

## 🚀 Démarrage Rapide

### Prérequis
- Docker et Docker Compose installés
- Make (optionnel mais recommandé)
- Ports disponibles : 5173 (frontend), 8000 (backend), 7474/7687 (neo4j)

### 1. Configuration

Créer le fichier `.env` dans `backend/` (copier depuis `.env.example`):
```bash
cp backend/.env.example backend/.env
```

Éditer `backend/.env` et configurer :
```env
# OpenRouter (obligatoire pour l'agent conversationnel)
OPENROUTER_API_KEY=votre_clé_ici

# Neo4j (optionnel, valeurs par défaut)
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=graphrag2024
```

### 2. Lancer l'application

```bash
# Build les images Docker
make build

# Lancer tous les services
make up

# Voir les logs
make logs
```

### 3. Accès aux interfaces

- **Frontend Vue.js** : http://localhost:5173
- **Backend API** : http://localhost:8000
- **API Docs (Swagger)** : http://localhost:8000/docs
- **Neo4j Browser** : http://localhost:7474

## 📦 Services Docker

Le `docker-compose.yml` configure 3 services :

### 1. Frontend (jarvis-frontend)
- Port : 5173
- Hot Module Replacement activé
- Proxy `/api` vers le backend

### 2. Backend (jarvis-backend)
- Port : 8000
- FastAPI avec reload automatique
- Volume monté pour développement

### 3. Neo4j (jarvis-neo4j)
- Ports : 7474 (HTTP), 7687 (Bolt)
- Plugin APOC activé
- Données persistées dans volume Docker

## 🎨 Fonctionnalités Frontend

### ✅ Implémentées

1. **Push-to-Talk Vocal**
   - Bouton maintenir-pour-parler
   - Visualisation waveform temps réel
   - Feedback visuel de l'état

2. **Historique Conversations**
   - Affichage messages utilisateur/Jarvis
   - Lecture audio des réponses
   - Clear history

3. **Knowledge Graph Visualization**
   - Affichage statistiques (nœuds/relations)
   - Placeholder pour visualisation interactive
   - Rafraîchissement manuel

4. **Health Check**
   - Vérification automatique backend
   - Indicateur de statut dans header

### 🔜 À Venir

- Visualisation interactive du graphe (D3.js ou Cytoscape)
- Mode sombre
- Paramètres utilisateur
- Export conversations

## 🔧 Commandes Utiles

### Docker

```bash
# Build
make build

# Start
make up

# Stop
make down

# Restart
make restart

# Logs
make logs                # Tous les services
make logs-backend        # Backend seulement
make logs-frontend       # Frontend seulement
make logs-neo4j          # Neo4j seulement

# Shell
make shell-backend       # Accéder au container backend
make shell-frontend      # Accéder au container frontend

# Reset complet (⚠️ perte de données)
make reset
```

### Backend (Python)

```bash
# Tests
make test
make test-cov

# Qualité code
make format              # Black
make lint                # Ruff
make type-check          # MyPy
make quality             # Tout en un

# Dépendances
make add PACKAGE=nom-du-package
make add-dev PACKAGE=nom-du-package
make update
```

### Frontend (npm)

```bash
# Installer dépendance
make add-frontend PACKAGE=nom-du-package

# Mise à jour
make update-frontend

# Accès direct npm (dans le container)
make shell-frontend
npm install mon-package
npm run build
```

## 📡 Communication Frontend ↔ Backend

### Proxy Vite

Le `vite.config.ts` configure un proxy :
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://backend:8000',
      changeOrigin: true,
    },
  },
}
```

Les requêtes du frontend `fetch('/api/...')` sont automatiquement redirigées vers le backend.

### Service API

Le service `src/services/api.ts` expose :

```typescript
// Health check
await jarvisApi.healthCheck()

// Traiter message vocal
await jarvisApi.processVoice(audioBlob)

// Récupérer knowledge graph
await jarvisApi.getKnowledgeGraph()

// Rechercher dans le graphe
await jarvisApi.queryKnowledge(query)
```

## 🧪 Tests

### Backend

```bash
# Tests unitaires
make test

# Avec couverture
make test-cov

# Test connexion Neo4j
make test-connection
```

### Frontend

```bash
# Dans le container
make shell-frontend
npm run test  # À configurer
```

## 📝 Développement

### Backend

1. Le code est dans `backend/src/`
2. Hot reload activé (uvicorn --reload)
3. Les changements sont détectés automatiquement

### Frontend

1. Le code est dans `frontend/src/`
2. HMR Vite activé
3. Les changements s'affichent instantanément

### Bonnes Pratiques

**Frontend:**
- Utiliser TypeScript pour le type safety
- Composants Vue SFC (Single File Components)
- Store Pinia pour le state management
- Element Plus pour les composants UI

**Backend:**
- Utiliser Poetry pour les dépendances
- Type hints Python partout
- Pydantic pour la validation
- Black + Ruff pour le formatage

## 🐛 Dépannage

### Le frontend ne se connecte pas au backend

1. Vérifier que les 3 containers tournent : `docker ps`
2. Vérifier les logs backend : `make logs-backend`
3. Vérifier le health check : http://localhost:8000/health

### Neo4j ne démarre pas

1. Arrêter tous les containers : `make down`
2. Vérifier les logs : `docker logs jarvis-neo4j`
3. Reset si nécessaire : `make reset` (⚠️ perte données)

### Erreurs de permissions

```bash
# Donner les droits sur les dossiers
sudo chown -R $USER:$USER backend/ frontend/
```

## 📚 Ressources

- [Vue 3 Documentation](https://vuejs.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Element Plus](https://element-plus.org/)
- [Pinia](https://pinia.vuejs.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Neo4j Documentation](https://neo4j.com/docs/)

## 🎯 Prochaines Étapes

1. **Tester le pipeline complet** - Vérifier que tout fonctionne end-to-end
2. **Intégrer Graphiti** - Activer la mémoire persistante
3. **Visualisation graphe** - Ajouter D3.js ou Cytoscape pour viz interactive
4. **ESP32** - Quand le matériel arrive, développer le firmware
5. **Features avancées** - Multi-user, home automation, etc.

## ⚡ Performances

- Frontend : Build Vite optimisé, lazy loading components
- Backend : FastAPI asynchrone, concurrence élevée
- Neo4j : Index appropriés, requêtes optimisées
- Communication : Compression HTTP, caching

---

**Bonne mise à jour ! 🚀**

Pour toute question, consulter la documentation ou ouvrir une issue.
