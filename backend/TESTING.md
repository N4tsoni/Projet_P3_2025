# 🧪 Tests & Notebooks - Guide Complet

Ce guide explique comment tester le backend Jarvis et explorer les technologies avec les notebooks interactifs.

---

## 📋 Table des Matières

1. [Tests Unitaires](#tests-unitaires)
2. [Notebooks Interactifs](#notebooks-interactifs)
3. [Tests d'Intégration](#tests-dintégration)

---

## 🧪 Tests Unitaires

### Structure des Tests

```
backend/tests/
├── conftest.py              # Fixtures pytest
├── services/
│   └── test_voice_service.py  # Tests du service vocal
└── api/
    └── (à venir)            # Tests des routes API
```

### Exécuter les Tests

**Tous les tests:**
```bash
docker compose exec backend pytest
```

**Avec couverture:**
```bash
docker compose exec backend pytest --cov=src --cov-report=html
```

**Tests spécifiques:**
```bash
docker compose exec backend pytest tests/services/test_voice_service.py -v
```

**Mode watch (re-run automatique):**
```bash
docker compose exec backend pytest-watch
```

### Résultats Actuels

```
✅ 3/3 tests passés
📊 Couverture: 92% sur voice_service
⚡ Temps: ~5s
```

### Écrire de Nouveaux Tests

**Exemple de test de service:**
```python
import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_my_service(mock_audio_file):
    service = MyService()
    
    with patch('src.module.function') as mock_func:
        mock_func.return_value = "test"
        result = await service.do_something(mock_audio_file)
        assert result == "expected"
```

---

## 📓 Notebooks Interactifs

### Notebooks Disponibles

| Notebook | Description | Techno Testée |
|----------|-------------|---------------|
| `01_test_stt_groq.ipynb` | Transcription audio | Groq Whisper large-v3 |
| `02_test_tts_edge.ipynb` | Synthèse vocale | Edge TTS |
| `03_test_agent_openrouter.ipynb` | Agent conversationnel | OpenRouter/Claude |
| `04_test_neo4j_graphiti.ipynb` | Knowledge graph | Neo4j + Graphiti |
| `05_pipeline_complet.ipynb` | Pipeline end-to-end | Tout le pipeline |

### Lancer Jupyter

**Option 1: Dans le container (recommandé)**
```bash
docker compose exec backend jupyter notebook \
  --ip=0.0.0.0 \
  --port=8888 \
  --no-browser \
  --allow-root \
  --notebook-dir=/app/notebooks

# Puis ouvrir: http://localhost:8888
```

**Option 2: Localement**
```bash
cd backend
jupyter notebook notebooks/
```

### Utiliser les Notebooks

1. **Démarrer les services:**
   ```bash
   docker compose up -d
   ```

2. **Lancer Jupyter** (voir ci-dessus)

3. **Ouvrir un notebook** et exécuter cellule par cellule

4. **Expérimenter!** Chaque notebook est autonome

### Exemples d'Utilisation

#### Test STT (Notebook 01)
```python
# Créer un audio de test
import edge_tts
text = "Bonjour Jarvis"
await create_test_audio(text)

# Transcrire
transcription = await transcribe_audio(audio_path, 'fr')
print(f"Transcription: {transcription}")
```

#### Test Agent (Notebook 03)
```python
# Conversation
agent = get_agent()
response = await agent.chat("Qui es-tu?")
print(response)
```

---

## 🔗 Tests d'Intégration

### Test du Pipeline Complet

**Depuis le notebook 05:**
```python
from src.services.voice_service import get_voice_service

service = get_voice_service()
transcription, response, audio_url = await service.process_voice_input(audio)

print(f"Pipeline OK: {transcription} → {response}")
```

**Depuis l'interface web:**
1. Ouvrir http://localhost:5173
2. Tester le microphone
3. Vérifier la réponse vocale

### Test des Endpoints API

**Health check:**
```bash
curl http://localhost:8000/api/health
```

**Knowledge graph:**
```bash
curl http://localhost:8000/api/knowledge/graph
```

**Documentation interactive:**
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📊 Métriques & Couverture

### Voir le Rapport de Couverture

```bash
# Générer le rapport
docker compose exec backend pytest --cov=src --cov-report=html

# Voir dans le navigateur
open backend/htmlcov/index.html
```

### Objectifs de Couverture

- ✅ Services: >80%
- ⚠️  Routes API: >60%
- ⚠️  Domain logic: >70%
- 🎯 Global: >60%

---

## 🎯 Bonnes Pratiques

### Tests Unitaires
- ✅ Mocker les dépendances externes (API, fichiers)
- ✅ Tester les cas d'erreur
- ✅ Un test = une fonctionnalité
- ✅ Noms de tests descriptifs

### Notebooks
- ✅ Documenter chaque cellule
- ✅ Afficher les résultats intermédiaires
- ✅ Nettoyer les fichiers temporaires
- ✅ Versionner les notebooks (avec outputs supprimés)

---

## 🐛 Debugging

### Tests qui échouent

**Voir les logs détaillés:**
```bash
docker compose exec backend pytest -vv -s
```

**Debugger avec pdb:**
```python
@pytest.mark.asyncio
async def test_something():
    import pdb; pdb.set_trace()
    # votre test
```

### Notebooks qui plantent

**Redémarrer le kernel:**
- Kernel → Restart & Clear Output

**Vérifier les services:**
```bash
docker compose ps
docker compose logs backend
```

---

## 📚 Ressources

### Documentation
- [Pytest](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Jupyter](https://jupyter.org/documentation)
- [Coverage.py](https://coverage.readthedocs.io/)

### Exemples
- Tests: `backend/tests/services/test_voice_service.py`
- Notebooks: `backend/notebooks/`
- Fixtures: `backend/tests/conftest.py`

---

**Prochaines Étapes:**
- [ ] Ajouter tests pour routes API
- [ ] Tests d'intégration Neo4j/Graphiti
- [ ] CI/CD avec GitHub Actions
- [ ] Tests de charge/performance

**Dernière mise à jour:** 2026-01-06
