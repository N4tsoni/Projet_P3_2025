# Knowledge Graph Pipeline - Documentation

> Documentation complète du pipeline de construction du Knowledge Graph par agents IA

---

## Vue d'Ensemble

Le **KG Pipeline** est un système modulaire qui construit automatiquement un Knowledge Graph à partir de documents structurés (CSV, JSON, etc.) en utilisant des agents IA (Claude via OpenRouter).

### Architecture

```
📄 Document (CSV, JSON, PDF, TXT)
    ↓
🔍 Parser (analyse format, extraction)
    ↓
🤖 Agent Entity Extractor (Claude identifie entités + propriétés)
    ↓
🔗 Agent Relation Extractor (Claude identifie relations)
    ↓
💾 Neo4j Storage (stockage nodes et edges)
    ↓
✅ Validation (statistiques, déduplication)
```

---

## Composants

### 1. Models (`backend/src/kg/models/`)

#### `entity.py` - Entités (Nodes)

```python
class EntityType(str, Enum):
    PERSON = "Person"
    MOVIE = "Movie"
    STUDIO = "Studio"
    ORGANIZATION = "Organization"
    LOCATION = "Location"
    CONCEPT = "Concept"
    GENERIC = "Generic"

class Entity(BaseModel):
    type: EntityType
    name: str  # Identifiant unique
    properties: Dict[str, Any]  # Propriétés flexibles
    source: Optional[str]  # Document source
    confidence: float  # Score de confiance (0-1)
    neo4j_id: Optional[str]  # ID Neo4j après création
```

**Exemples d'entités:**
- Person: `{type: "Person", name: "Tom Hanks", properties: {birth_year: 1956, role: "actor"}}`
- Movie: `{type: "Movie", name: "Forrest Gump", properties: {year: 1994, genre: "Drama", rating: 8.8}}`
- Studio: `{type: "Studio", name: "Paramount Pictures", properties: {country: "USA"}}`

#### `relation.py` - Relations (Edges)

```python
class RelationType(str, Enum):
    ACTED_IN = "ACTED_IN"
    DIRECTED = "DIRECTED"
    PRODUCED_BY = "PRODUCED_BY"
    WORKS_AT = "WORKS_AT"
    KNOWS = "KNOWS"
    RELATED_TO = "RELATED_TO"

class Relation(BaseModel):
    type: RelationType
    from_entity: str  # Nom de l'entité source
    to_entity: str    # Nom de l'entité cible
    properties: Dict[str, Any]  # Props (role, budget, etc.)
    confidence: float
```

**Exemples de relations:**
- `Tom Hanks -[ACTED_IN {role: "Forrest"}]-> Forrest Gump`
- `Christopher Nolan -[DIRECTED]-> Inception`
- `The Dark Knight -[PRODUCED_BY {budget: 185M}]-> Warner Bros`

#### `document.py` - Tracking de traitement

```python
class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PARSING = "parsing"
    EXTRACTING_ENTITIES = "extracting_entities"
    EXTRACTING_RELATIONS = "extracting_relations"
    STORING = "storing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"

class Document(BaseModel):
    filename: str
    format: DocumentFormat  # CSV, JSON, PDF, TXT
    status: ProcessingStatus
    progress: float  # 0-100%
    entities_extracted: int
    relations_extracted: int
    error: Optional[str]
```

---

### 2. Parsers (`backend/src/kg/parsers/`)

#### `csv_parser.py` - Parser CSV

**Fonctionnalités:**
- Auto-détection encoding (chardet)
- Auto-détection délimiteur (`,`, `;`, `\t`, `|`)
- Inférence de types de colonnes (int, float, date, boolean, string)
- Génération de métadonnées
- Statistiques par colonne

**Usage:**
```python
from src.kg.parsers.csv_parser import CSVParser

parser = CSVParser()
df, metadata = parser.parse(Path("data/movies.csv"))

# metadata contient:
# - filename, size_bytes, encoding, delimiter
# - row_count, column_count, columns
# - column_types, sample_rows
```

---

### 3. Agents (`backend/src/kg/agents/`)

#### `entity_extractor_agent.py` - Extraction d'entités

**Fonctionnement:**
1. Reçoit les données CSV parsées
2. Construit un prompt structuré pour Claude
3. Envoie à OpenRouter (Claude 3.5 Sonnet)
4. Parse la réponse JSON
5. Crée des objets Entity
6. Déduplique par (type, name)

**Prompt Claude:**
- Instructions claires sur types d'entités à extraire
- Métadonnées CSV (colonnes, types)
- Sample des données
- Format JSON strict
- Exemples

**Features:**
- Batch processing (50 records par appel)
- Temperature faible (0.1) pour cohérence
- Extraction multi-valeurs (acteurs séparés par `;`)
- Confidence scoring

#### `relation_extractor_agent.py` - Extraction de relations

**Fonctionnement:**
1. Reçoit les données CSV + entités extraites
2. Construit prompt avec contexte des entités
3. Claude identifie les relations
4. Valide que les entités existent
5. Crée des objets Relation
6. Déduplique par (type, from, to)

**Validation:**
- Vérifie que from_entity existe
- Vérifie que to_entity existe
- Ignore les relations invalides

---

### 4. Services (`backend/src/kg/services/`)

#### `neo4j_service.py` - Interaction Neo4j

**Operations:**

**Entités:**
```python
# Créer une entité
entity_id = service.create_entity(entity)

# Créer en batch
entity_ids = service.create_entities_batch(entities)

# Query
entity_data = service.get_entity_by_name("Tom Hanks")
```

**Relations:**
```python
# Créer une relation
relation_id = service.create_relation(relation)

# Créer en batch
relation_ids = service.create_relations_batch(relations)
```

**Statistiques:**
```python
stats = service.get_graph_stats()
# Retourne:
# - total_nodes, total_relationships
# - nodes_by_label (Person: 25, Movie: 10, ...)
# - relationships_by_type (ACTED_IN: 50, DIRECTED: 10, ...)
```

**Visualization:**
```python
graph_data = service.get_graph_data(limit=100)
# Retourne:
# - nodes: [{id, label, properties}, ...]
# - edges: [{id, from, to, type, properties}, ...]
```

**Cypher queries:**
- Utilise `MERGE` pour éviter les duplicates
- `MATCH` par name pour créer relations
- Transactions pour ACID compliance

#### `pipeline_orchestrator.py` - Orchestrateur

**Coordonne le pipeline complet:**

```python
orchestrator = get_orchestrator()
result = await orchestrator.process_file(
    file_path=Path("data/movies.csv"),
    file_format=DocumentFormat.CSV
)
```

**Étapes:**
1. **Parse**: CSV → DataFrame
2. **Extract Entities**: DataFrame → List[Entity] (via Claude)
3. **Extract Relations**: DataFrame + Entities → List[Relation] (via Claude)
4. **Store**: Entities + Relations → Neo4j
5. **Validate**: Statistiques et vérifications

**Retourne:**
```json
{
  "status": "completed",
  "extraction": {
    "entities_extracted": 45,
    "relations_extracted": 78,
    "entities_by_type": {"Person": 25, "Movie": 10, "Studio": 10},
    "relations_by_type": {"ACTED_IN": 50, "DIRECTED": 10, ...}
  },
  "storage": {
    "entities_stored": 45,
    "relations_stored": 78
  },
  "graph_stats": {...}
}
```

---

### 5. API Routes (`backend/src/api/routes/kg.py`)

#### Endpoints disponibles:

**1. Upload document**
```http
POST /api/kg/upload
Content-Type: multipart/form-data

file: [fichier CSV/JSON/PDF/TXT]
```

**2. Process document**
```http
POST /api/kg/process/{filename}
```

**3. Upload + Process (combo)**
```http
POST /api/kg/upload-and-process
Content-Type: multipart/form-data

file: [fichier]
```

**4. Graph statistics**
```http
GET /api/kg/graph/stats
```

**5. Graph visualization**
```http
GET /api/kg/graph/visualization?limit=100
```

**6. Clear graph**
```http
DELETE /api/kg/graph/clear
⚠️ Supprime TOUTES les données !
```

**7. Health check**
```http
GET /api/kg/health
```

**8. List uploaded files**
```http
GET /api/kg/uploaded-files
```

---

## Usage

### 1. Via API (Curl)

```bash
# Upload et process
curl -X POST "http://localhost:8000/api/kg/upload-and-process" \
  -F "file=@data/movies.csv"

# Get stats
curl "http://localhost:8000/api/kg/graph/stats"

# Get visualization data
curl "http://localhost:8000/api/kg/graph/visualization?limit=50"
```

### 2. Via Python

```python
from pathlib import Path
from src.kg.services.pipeline_orchestrator import get_orchestrator
from src.kg.models.document import DocumentFormat

orchestrator = get_orchestrator()
result = await orchestrator.process_file(
    Path("data/movies.csv"),
    DocumentFormat.CSV
)
print(result)
```

### 3. Via Jupyter Notebook

```bash
# Lancer Jupyter
docker compose exec backend jupyter notebook \
  --ip=0.0.0.0 --port=8888 --no-browser --allow-root

# Ouvrir notebooks/06_kg_pipeline_test.ipynb
```

---

## Dataset de Test

### `data/test_datasets/movies_sample.csv`

10 films populaires avec:
- title, year, genre, rating
- director, studio, actors (multiples), budget

**Entités extraites (~45):**
- 25+ Persons (acteurs + réalisateurs)
- 10 Movies
- 10 Studios

**Relations extraites (~78):**
- ACTED_IN (50+)
- DIRECTED (10)
- PRODUCED_BY (10)

---

## Tests

### Tests automatisés

```bash
# Run tests
docker compose exec backend pytest tests/kg/test_pipeline_e2e.py -v

# Tests inclus:
# - CSV parsing
# - Entity extraction
# - Relation extraction
# - Neo4j connection
# - Full pipeline end-to-end
```

### Tests manuels

**Jupyter Notebook:**
`backend/notebooks/06_kg_pipeline_test.ipynb`

Sections:
1. Parse CSV
2. Extract Entities
3. Extract Relations
4. Store in Neo4j
5. Graph Statistics
6. Test Complete Pipeline
7. Query Graph Data
8. Test Specific Entity
9. Cleanup

---

## Configuration

### Variables d'environnement

```bash
# OpenRouter (LLM)
OPENROUTER_API_KEY=your_key_here

# Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=graphrag2024
```

### Settings

Dans `src/core/config.py`:
- `openrouter_api_key`: Clé API OpenRouter
- `neo4j_uri`, `neo4j_user`, `neo4j_password`: Connexion Neo4j

---

## Schéma Initial: Movies & Actors

### Entités

| Type | Propriétés | Exemple |
|------|-----------|---------|
| Person | name, role (actor/director), nationality | Tom Hanks |
| Movie | name, year, genre, rating, budget_millions | Forrest Gump (1994) |
| Studio | name, country, founded_year | Paramount Pictures |

### Relations

| Type | De | Vers | Propriétés | Exemple |
|------|-------|--------|-----------|---------|
| ACTED_IN | Person | Movie | role (character) | Tom Hanks -[ACTED_IN {role: "Forrest"}]-> Forrest Gump |
| DIRECTED | Person | Movie | - | Robert Zemeckis -[DIRECTED]-> Forrest Gump |
| PRODUCED_BY | Movie | Studio | budget_millions | Forrest Gump -[PRODUCED_BY {budget: 55}]-> Paramount |

---

## Extension Future

### Formats supplémentaires
- JSON (structuré)
- PDF (extraction texte + tables)
- TXT (non-structuré)
- XLSX (Excel)

### Agents supplémentaires
- **Validator Agent**: Cohérence, enrichissement, déduplication avancée
- **Enrichment Agent**: Recherche d'informations complémentaires
- **Resolution Agent**: Entity linking (Tom Hanks = Thomas J. Hanks)

### Features avancées
- GraphRAG: Intégration dans l'agent vocal
- Temporal KG: Évolution dans le temps
- Clustering: Détection de communautés
- Inférence: Relations implicites
- Multi-sources: APIs, scraping, bases de données

---

## Architecture Fichiers

```
backend/src/kg/
├── agents/
│   ├── entity_extractor_agent.py    # Agent extraction entités
│   └── relation_extractor_agent.py  # Agent extraction relations
├── services/
│   ├── neo4j_service.py             # Service Neo4j
│   └── pipeline_orchestrator.py     # Orchestrateur principal
├── models/
│   ├── entity.py                    # Model Entity
│   ├── relation.py                  # Model Relation
│   └── document.py                  # Model Document
└── parsers/
    └── csv_parser.py                # Parser CSV

backend/src/api/routes/
└── kg.py                            # API routes KG

backend/data/test_datasets/
└── movies_sample.csv                # Dataset de test

backend/tests/kg/
└── test_pipeline_e2e.py             # Tests end-to-end

backend/notebooks/
└── 06_kg_pipeline_test.ipynb        # Notebook de test
```

---

## Commandes Utiles

### Développement

```bash
# Lancer les services
make up

# Logs
make logs

# Backend shell
docker compose exec backend bash

# Python shell
docker compose exec backend python

# Jupyter
docker compose exec backend jupyter notebook \
  --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```

### Neo4j

```bash
# Neo4j Browser
http://localhost:7474

# Cypher queries
MATCH (n) RETURN count(n)  # Count nodes
MATCH ()-[r]->() RETURN count(r)  # Count relationships
MATCH (n:Person) RETURN n LIMIT 10  # Get persons
MATCH (p:Person)-[r:ACTED_IN]->(m:Movie) RETURN p, r, m  # Get actors and movies
```

### API

```bash
# API Docs
http://localhost:8000/docs

# Test health
curl http://localhost:8000/api/kg/health
```

---

## Dépendances Ajoutées

```toml
# pyproject.toml
[tool.poetry.dependencies]
neo4j = "^5.15.0"         # Driver Neo4j
pandas = "^2.1.4"         # Parser CSV
chardet = "^5.2.0"        # Détection encoding
httpx = "^0.26.0"         # HTTP client (déjà présent)
```

---

## Troubleshooting

### Erreur: "Neo4j connection failed"
- Vérifier que Neo4j est lancé: `docker compose ps`
- Vérifier les credentials dans `.env`
- Test connexion: `curl http://localhost:7474`

### Erreur: "OpenRouter API failed"
- Vérifier `OPENROUTER_API_KEY` dans `.env`
- Vérifier le quota/crédit OpenRouter
- Test avec curl direct à l'API

### Erreur: "CSV encoding detection failed"
- Vérifier que chardet est installé: `poetry show chardet`
- Tester avec encoding explicite: `parser.parse(file, encoding='utf-8')`

### Erreur: "Entity not found in extraction"
- Augmenter la temperature du LLM (actuellement 0.1)
- Améliorer le prompt avec plus d'exemples
- Vérifier les données CSV (colonnes manquantes ?)

---

## Contact & Support

Pour questions ou problèmes:
1. Vérifier cette documentation
2. Consulter les notebooks de test
3. Vérifier les logs: `make logs`
4. Ouvrir une issue sur le repo

---

**Version:** 1.0.0
**Date:** 2026-01-07
**Branche:** KG
**Status:** ✅ Opérationnel - Sprint 1 complété
