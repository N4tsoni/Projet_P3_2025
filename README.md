# Jarvis - Assistant Vocal Intelligent avec GraphRAG

Assistant personnel vocal type "Jarvis" utilisant GraphRAG et Graphiti avec interface ESP32.

## Description

Ce projet implémente un assistant vocal intelligent qui utilise GraphRAG (Graph Retrieval-Augmented Generation) avec un knowledge graph dynamique pour mémoriser et raisonner sur vos informations personnelles. L'assistant communique via un ESP32 avec capacités vocales (wake word, STT, TTS) et construit progressivement une mémoire de vos préférences, habitudes et connaissances partagées.

## Technologies

**Backend:**
- **Docker & Docker Compose**: Containerisation
- **Poetry**: Gestion moderne des dépendances Python
- **FastAPI**: API REST pour communication ESP32
- **Neo4j**: Base de données graphe
- **Graphiti**: Framework pour knowledge graphs dynamiques
- **LangChain**: Framework pour agent conversationnel
- **Whisper/Google STT**: Reconnaissance vocale
- **OpenAI TTS**: Synthèse vocale
- **Python 3.10+**: Langage principal

**Hardware:**
- **ESP32**: Microcontrôleur avec WiFi
- **Microphone I2S**: Capture audio
- **Speaker**: Diffusion audio

## Prérequis

- Docker et Docker Compose installés
- Au moins 4GB de RAM disponible pour les containers
- Ports 7474, 7687, et 8000 disponibles

## Installation

1. Cloner le repository:
```bash
git clone <repository-url>
cd Projet_P3
```

2. Créer le fichier `.env` depuis l'exemple:
```bash
cp .env.example .env
```

3. Éditer `.env` et ajouter vos clés API:
```bash
OPENAI_API_KEY=your_actual_api_key_here
# ou
ANTHROPIC_API_KEY=your_actual_api_key_here
```

## Utilisation

### Démarrer les services

```bash
# Build des images
docker-compose build

# Lancer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f
```

### Accéder aux services

- **Neo4j Browser**: http://localhost:7474
  - User: `neo4j`
  - Password: voir `.env` (par défaut: `graphrag2024`)

- **Application**: Port 8000 (une fois l'interface implémentée)

### Développement

Le projet utilise un Makefile pour simplifier les commandes courantes :

```bash
# Voir toutes les commandes disponibles
make help

# Exécuter les tests
make test

# Tester la connexion Graphiti
make test-connection

# Formater le code
make format

# Vérifier la qualité du code
make quality

# Accéder au shell du container
make shell
```

Commandes Poetry dans le container :

```bash
# Ajouter une dépendance
make add PACKAGE=nom-du-package

# Ajouter une dépendance de dev
make add-dev PACKAGE=nom-du-package

# Mettre à jour les dépendances
make update
```

### Arrêter les services

```bash
# Arrêter les containers
docker-compose down

# Arrêter et supprimer les volumes (⚠️ perte de données)
docker-compose down -v
```

## Structure du Projet

```
Projet_P3/
├── src/
│   ├── graph/          # Gestion du knowledge graph (Graphiti)
│   ├── rag/            # Système GraphRAG
│   ├── agents/         # Agents comptables
│   ├── tools/          # Outils pour les agents
│   ├── data/           # Ingestion et modèles de données
│   └── main.py         # Point d'entrée
├── tests/              # Tests unitaires et d'intégration
├── data/               # Données d'exemple
│   └── examples/       # Exemples de factures, transactions
├── config/             # Fichiers de configuration
├── docs/               # Documentation
├── notebooks/          # Jupyter notebooks pour exploration
├── Dockerfile          # Image Docker de l'application
├── docker-compose.yml  # Orchestration des services
├── requirements.txt    # Dépendances Python
└── .env.example        # Template des variables d'environnement
```

## Progression

Voir [TODO.md](TODO.md) pour l'état d'avancement du projet et [CLAUDE.md](CLAUDE.md) pour la documentation technique.

## Licence

MIT
