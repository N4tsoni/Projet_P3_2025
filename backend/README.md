# Backend Jarvis - Architecture MVC

Backend FastAPI pour l'assistant vocal Jarvis avec GraphRAG.

## 🚀 Quick Start

### Avec Docker (Recommandé)

```bash
# Depuis la racine du projet
docker compose up -d backend

# Voir les logs
docker compose logs -f backend

# Accéder au shell
docker compose exec backend bash
```

### Sans Docker

```bash
cd backend

# Installer les dépendances
poetry install

# Lancer l'application
poetry run python src/main_new.py

# Ou avec uvicorn directement
poetry run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Structure du Projet

```
backend/
├── src/
│   ├── app.py                    # Application FastAPI
│   ├── main_new.py               # Entry point
│   ├── core/                     # Configuration
│   ├── middlewares/              # Middlewares
│   ├── api/routes/               # Routes API
│   ├── controllers/              # Controllers
│   ├── services/                 # Services métier
│   ├── schemas/                  # Pydantic schemas
│   ├── agents/                   # AI Agents
│   └── graph/                    # GraphRAG
├── tests/                        # Tests
├── data/                         # Données
├── config/                       # Configuration files
├── pyproject.toml                # Dependencies
└── ARCHITECTURE.md               # Documentation architecture
```

## 🏗️ Architecture

L'architecture suit un pattern **MVC modulaire**:

```
Routes → Controllers → Services → Repositories/Agents
  ↓          ↓            ↓
Schemas   Orchestration  Business Logic
```

Voir [ARCHITECTURE.md](./ARCHITECTURE.md) pour les détails complets.

## 🛠️ Développement

### Configuration

Copier `.env.example` vers `.env` et configurer:

```bash
cp .env.example .env
```

Variables essentielles:
- `OPENROUTER_API_KEY`: Clé API OpenRouter
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`: Neo4j credentials
- `STT_PROVIDER`: `whisper-local` ou `groq`
- `TTS_PROVIDER`: `edge-tts` ou `coqui-local`

### Ajouter une Dépendance

```bash
# Dépendance de production
poetry add package-name

# Dépendance de dev
poetry add --group dev package-name
```

### Code Quality

```bash
# Formatter
poetry run black src/ tests/

# Linter
poetry run ruff check src/ tests/

# Corriger automatiquement
poetry run ruff check --fix src/ tests/

# Type checking
poetry run mypy src/
```

### Tests

```bash
# Tous les tests
poetry run pytest

# Avec couverture
poetry run pytest --cov=src --cov-report=html

# Un fichier spécifique
poetry run pytest tests/test_something.py

# Avec output verbeux
poetry run pytest -v
```

## 📡 API Endpoints

### Health Checks

```bash
# Health check simple
GET /health

# Health check détaillé
GET /api/health
```

### Voice Processing

```bash
# Traiter un fichier audio
POST /api/voice/process
Content-Type: multipart/form-data

# Body: audio file (WebM, WAV, etc.)
```

### Knowledge Graph

```bash
# Query le graphe
GET /api/knowledge/query?q=question

# Obtenir le graphe complet
GET /api/knowledge/graph

# Ajouter de la connaissance
POST /api/knowledge/add
Content-Type: application/json

{
  "data": {
    "type": "fact",
    "content": "..."
  }
}
```

### Documentation Interactive

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Configuration

### Variables d'Environnement

Toutes les variables sont centralisées dans `src/core/config.py` avec Pydantic Settings.

```python
from src.core.config import get_settings

settings = get_settings()
print(settings.OPENROUTER_API_KEY)
print(settings.STT_PROVIDER)
```

### Logging

Configuré avec Loguru dans `src/core/logging.py`.

Logs vers:
- Console (colorés)
- Fichier `/app/logs/jarvis_YYYY-MM-DD.log` (en production)

Niveaux: DEBUG, INFO, WARNING, ERROR, CRITICAL

```python
from loguru import logger

logger.info("Message info")
logger.warning("Message warning")
logger.error("Message erreur")
```

## 🎯 Ajouter une Fonctionnalité

### Exemple: Ajouter un endpoint `/api/stats`

**1. Créer le schema** (`src/schemas/stats.py`):
```python
from pydantic import BaseModel

class StatsResponse(BaseModel):
    total_conversations: int
    total_queries: int
```

**2. Créer le service** (`src/services/stats_service.py`):
```python
class StatsService:
    async def get_stats(self) -> dict:
        # Logic
        return {"total_conversations": 10, "total_queries": 50}
```

**3. Créer le controller** (`src/controllers/stats_controller.py`):
```python
from src.schemas.stats import StatsResponse

class StatsController:
    async def get_stats(self) -> StatsResponse:
        service = get_stats_service()
        stats = await service.get_stats()
        return StatsResponse(**stats)
```

**4. Créer la route** (`src/api/routes/stats.py`):
```python
router = APIRouter(prefix="/api/stats", tags=["Stats"])

@router.get("/", response_model=StatsResponse)
async def get_stats(controller = Depends(get_stats_controller)):
    return await controller.get_stats()
```

**5. Inclure dans l'app** (`src/app.py`):
```python
from src.api.routes import stats
app.include_router(stats.router)
```

## 🧩 Services Disponibles

### STT Service (`services/voice/stt_service.py`)

```python
from src.services.voice.stt_service import get_stt_service

stt = get_stt_service()
text = await stt.transcribe(audio_path, language="fr")
```

Providers: `whisper-local`, `groq`

### TTS Service (`services/voice/tts_service.py`)

```python
from src.services.voice.tts_service import get_tts_service

tts = get_tts_service()
audio_path = await tts.synthesize("Bonjour", output_path)
```

Providers: `edge-tts`, `coqui-local`

### Agent Service (`services/agent_service.py`)

```python
from src.services.agent_service import get_agent_service

agent = get_agent_service()
response = await agent.process_message("Bonjour Jarvis")
```

### Knowledge Service (`services/knowledge_service.py`)

```python
from src.services.knowledge_service import get_knowledge_service

knowledge = get_knowledge_service()
results = await knowledge.query_knowledge("query")
graph = await knowledge.get_knowledge_graph()
```

## 🐛 Debugging

### Logs en Temps Réel

```bash
# Tous les services
docker compose logs -f

# Backend uniquement
docker compose logs -f backend

# Dernières 100 lignes
docker compose logs backend --tail=100
```

### Shell Interactif

```bash
# Accéder au container
docker compose exec backend bash

# Tester une import
docker compose exec backend python -c "from src.core.config import get_settings; print(get_settings())"
```

### Mode Debug

Dans `.env`:
```
DEBUG=True
LOG_LEVEL=DEBUG
```

## 🔐 Sécurité

### Best Practices

1. **Ne jamais commit** `.env`
2. **Valider toutes les entrées** avec Pydantic schemas
3. **Utiliser HTTPS** en production
4. **Rate limiting** sur endpoints publics
5. **Authentification** pour endpoints sensibles

### TODO Sécurité

- [ ] Authentification JWT
- [ ] Rate limiting
- [ ] HTTPS only en prod
- [ ] Input sanitization
- [ ] API key rotation
- [ ] Audit logging

## 📊 Monitoring

### Métriques à Ajouter

- Latence des requêtes
- Taux d'erreur
- Usage CPU/RAM
- Nombre de requêtes par endpoint
- Temps de traitement STT/TTS

### Tools Recommandés

- Prometheus + Grafana
- Sentry pour error tracking
- New Relic ou DataDog

## 🚢 Déploiement

### Production Checklist

- [ ] `DEBUG=False`
- [ ] Variables d'environnement sécurisées
- [ ] HTTPS activé
- [ ] Rate limiting configuré
- [ ] Logs vers fichier
- [ ] Monitoring activé
- [ ] Backups Neo4j configurés
- [ ] Health checks configurés

## 📚 Ressources

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Documentation architecture complète
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [Loguru](https://loguru.readthedocs.io/)
- [Poetry](https://python-poetry.org/docs/)

## 🤝 Contributing

1. Suivre l'architecture MVC établie
2. Ajouter des tests pour nouveau code
3. Documenter avec docstrings
4. Linter avec Black + Ruff
5. Type hints partout

## 📝 License

Voir LICENSE à la racine du projet.
