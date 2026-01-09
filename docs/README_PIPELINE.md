# Knowledge Graph Pipeline Architecture

## 📋 Vue d'ensemble

Le système de pipeline modulaire pour la construction de Knowledge Graphs (KG) est conçu pour traiter des documents de différents formats et extraire des entités et relations structurées.

## 🏗️ Structure

```
backend/src/kg/
├── pipeline/
│   ├── __init__.py
│   ├── base.py              # Classes de base (Stage, StageResult)
│   ├── pipeline.py          # Orchestrateur principal (Pipeline, PipelineContext)
│   ├── factory.py           # Factory pour pipelines préconfigurées
│   └── stages/
│       ├── __init__.py
│       ├── parsing.py       # Stage 1: Parsing de documents
│       ├── chunking.py      # Stage 2: Découpage en chunks
│       ├── embedding.py     # Stage 3: Génération d'embeddings
│       ├── ner.py           # Stage 4: Named Entity Recognition
│       ├── extraction.py    # Stage 5: Extraction entités/relations (LLM)
│       ├── transformation.py # Stage 6: Transformation des données
│       ├── enrichment.py    # Stage 7: Enrichissement
│       ├── validation.py    # Stage 8: Validation
│       └── storage.py       # Stage 9: Stockage Neo4j
└── pipeline_example.py      # Exemples d'utilisation
```

## 🔄 Pipeline Flow

```
┌─────────────┐
│  Document   │
└──────┬──────┘
       ↓
┌─────────────────────┐
│  1. ParsingStage    │  Parse CSV, JSON, PDF, TXT
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│  2. ChunkingStage   │  Découpe en chunks (optionnel)
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│  3. EmbeddingStage  │  Génère embeddings (optionnel)
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│  4. NERStage        │  Named Entity Recognition (optionnel)
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│  5. ExtractionStage │  Extraction LLM (Claude)
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│  6. TransformationStage │  Normalisation des données
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│  7. EnrichmentStage │  Enrichissement contextuel
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│  8. ValidationStage │  Validation qualité
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│  9. StorageStage    │  Stockage Neo4j
└──────┬──────────────┘
       ↓
   ┌────────┐
   │  Done  │
   └────────┘
```

## 🎯 Les 9 Stages

### 1. **ParsingStage** - Parsing de Documents
**Responsabilité**: Convertir les documents bruts en données structurées

**Formats supportés**:
- ✅ CSV (implémenté)
- ⏳ JSON (à implémenter)
- ⏳ PDF (à implémenter)
- ⏳ TXT (à implémenter)
- ⏳ XLSX (à implémenter)

**Entrée**: `context.file_path`, `context.file_format`
**Sortie**: `context.raw_data`, `context.metadata`

### 2. **ChunkingStage** - Découpage en Chunks
**Responsabilité**: Découper les textes longs en chunks gérables

**Configuration**:
- `chunk_size`: Taille maximale d'un chunk (défaut: 1000 caractères)
- `chunk_overlap`: Chevauchement entre chunks (défaut: 200 caractères)

**Entrée**: `context.raw_data`
**Sortie**: `context.chunks`

**Note**: Pour les CSV, chaque ligne devient un chunk. Pour les textes, on découpe avec chevauchement.

### 3. **EmbeddingStage** - Génération d'Embeddings
**Responsabilité**: Générer des représentations vectorielles des chunks

**Modèles supportés**:
- Sentence-Transformers (all-MiniLM-L6-v2, etc.)
- OpenAI embeddings
- Custom models

**Entrée**: `context.chunks`
**Sortie**: `context.embeddings`

**Usage**: Pour recherche sémantique, similarité, clustering

### 4. **NERStage** - Named Entity Recognition
**Responsabilité**: Identifier les entités nommées avec des modèles NLP

**Modèles supportés**:
- spaCy (en_core_web_sm, fr_core_news_sm, etc.)
- Transformers (BERT-NER, etc.)

**Entrée**: `context.chunks`
**Sortie**: Enrichit `context.entities`

**Entités détectées**: PERSON, ORG, GPE, DATE, etc.

### 5. **ExtractionStage** - Extraction LLM
**Responsabilité**: Extraire entités et relations avec Claude (LLM)

**Configuration**:
- `batch_size`: Nombre de records par batch (défaut: 50)

**Agents**:
- `EntityExtractorAgent`: Extrait entités structurées
- `RelationExtractorAgent`: Extrait relations entre entités

**Entrée**: `context.raw_data`, `context.metadata`
**Sortie**: `context.entities`, `context.relations`

**Note**: C'est le stage principal d'extraction intelligent.

### 6. **TransformationStage** - Transformation
**Responsabilité**: Normaliser et transformer les données extraites

**Transformations**:
- Normalisation des noms (lowercase, title case)
- Conversion de types (dates, nombres)
- Déduplication avancée
- Merge de propriétés

**Entrée**: `context.entities`, `context.relations`
**Sortie**: Transforme en place

### 7. **EnrichmentStage** - Enrichissement
**Responsabilité**: Enrichir les données avec des informations externes

**Sources d'enrichissement**:
- Wikipedia / DBpedia
- Wikidata
- APIs externes
- Calcul de scores (centralité, importance)
- Ajout de métadonnées temporelles

**Entrée**: `context.entities`, `context.relations`
**Sortie**: `context.enriched_entities`, `context.enriched_relations`

### 8. **ValidationStage** - Validation
**Responsabilité**: Valider la qualité et cohérence des données

**Validations**:
- Champs requis présents
- Types de données corrects
- Références valides (entités existent)
- Pas de doublons
- Contraintes métier respectées

**Configuration**:
- `strict`: Si True, échoue sur erreur. Si False, continue avec warnings

**Entrée**: `context.enriched_entities`, `context.enriched_relations`
**Sortie**: `context.validation_results`

### 9. **StorageStage** - Stockage Neo4j
**Responsabilité**: Persister le graphe dans Neo4j

**Opérations**:
- Création de nœuds (MERGE sur name)
- Création de relations (MERGE)
- Transactions batch pour performance
- Gestion d'erreurs

**Entrée**: `context.enriched_entities`, `context.enriched_relations`
**Sortie**: `context.storage_ids`

## 🚀 Utilisation

### Méthode 1: Factory (Recommandé)

```python
from kg.pipeline.factory import PipelineFactory

# Pipeline pour CSV
pipeline = PipelineFactory.create_csv_pipeline()

# Pipeline pour textes (PDF, TXT)
pipeline = PipelineFactory.create_text_pipeline()

# Pipeline minimal (rapide)
pipeline = PipelineFactory.create_minimal_pipeline()

# Pipeline personnalisée
pipeline = PipelineFactory.create_custom_pipeline(
    include_chunking=False,
    include_ner=False,
    batch_size=100
)
```

### Méthode 2: Construction Manuelle

```python
from kg.pipeline import Pipeline
from kg.pipeline.stages import ParsingStage, ExtractionStage, StorageStage

pipeline = Pipeline(name="My Pipeline")
pipeline.add_stage(ParsingStage())
pipeline.add_stage(ExtractionStage(batch_size=50))
pipeline.add_stage(StorageStage())
```

### Exécution

```python
from pathlib import Path

context = await pipeline.execute(
    file_path=Path("data/movies.csv"),
    filename="movies.csv",
    file_format="csv"
)

# Résultats
print(f"Success: {context.is_successful()}")
print(f"Entities: {len(context.entities)}")
print(f"Relations: {len(context.relations)}")
print(f"Duration: {context.get_duration():.2f}s")

# Résultats par stage
for result in context.stage_results:
    print(f"{result.stage_name}: {result.status} ({result.duration_seconds:.2f}s)")
```

## 🎛️ Configuration des Pipelines

### Pipeline CSV (Structuré)

Pour données tabulaires structurées:

```
ParsingStage → ExtractionStage → TransformationStage → ValidationStage → StorageStage
```

**Stages exclus**: Chunking, Embedding, NER (pas nécessaires pour CSV)

### Pipeline Text (Non-structuré)

Pour documents texte (PDF, TXT, etc.):

```
ParsingStage → ChunkingStage → EmbeddingStage → NERStage →
ExtractionStage → TransformationStage → EnrichmentStage →
ValidationStage → StorageStage
```

**Stages inclus**: Tous les stages pour traitement complet

### Pipeline Minimal (Rapide)

Pour tests ou cas simples:

```
ParsingStage → ExtractionStage → StorageStage
```

**Durée**: ~30% plus rapide que pipeline complet

## 🔧 Personnalisation

### Désactiver un Stage

```python
pipeline = PipelineFactory.create_default_pipeline()

# Désactiver validation
validation_stage = pipeline.get_stage("ValidationStage")
validation_stage.disable()

# Le stage sera skippé lors de l'exécution
```

### Ajouter/Retirer des Stages

```python
# Retirer un stage
pipeline.remove_stage("EmbeddingStage")

# Ajouter un stage personnalisé
from kg.pipeline.base import Stage

class MyCustomStage(Stage):
    async def execute(self, context):
        # ... votre logique
        return StageResult(...)

pipeline.add_stage(MyCustomStage())
```

### Modifier les Paramètres

```python
pipeline = Pipeline()
pipeline.add_stage(ChunkingStage(chunk_size=2000, chunk_overlap=400))
pipeline.add_stage(ExtractionStage(batch_size=100))
pipeline.add_stage(ValidationStage(strict=True))
```

## 📊 PipelineContext

Le `PipelineContext` est l'objet partagé entre tous les stages.

**Données d'entrée**:
- `file_path`: Chemin du fichier
- `filename`: Nom du fichier
- `file_format`: Format (csv, json, pdf, txt)
- `document`: Objet Document pour tracking

**Données intermédiaires** (remplies par stages):
- `raw_data`: Données parsées brutes
- `metadata`: Métadonnées du fichier
- `chunks`: Chunks de texte
- `embeddings`: Embeddings vectoriels
- `entities`: Entités extraites
- `relations`: Relations extraites
- `enriched_entities`: Entités enrichies
- `enriched_relations`: Relations enrichies
- `validation_results`: Résultats de validation
- `storage_ids`: IDs Neo4j

**Tracking**:
- `start_time`: Début du pipeline
- `stage_results`: Résultats de chaque stage
- `errors`: Liste des erreurs

**Méthodes**:
- `get_duration()`: Durée totale
- `is_successful()`: Succès ou échec
- `get_stage_result(name)`: Résultat d'un stage spécifique
- `to_dict()`: Convertir en dictionnaire

## 🧪 Tests

```bash
# Lancer les exemples
cd backend
python -m kg.pipeline_example

# Tester avec un fichier
python -m kg.pipeline_example data/test_datasets/movies_sample.csv
```

## 📝 TODO

### Stages à compléter

- [ ] **ParsingStage**: Ajouter parsers JSON, PDF, TXT, XLSX
- [ ] **ChunkingStage**: Implémenter chunking avec overlap pour texte
- [ ] **EmbeddingStage**: Intégrer sentence-transformers
- [ ] **NERStage**: Intégrer spaCy et transformers
- [ ] **TransformationStage**: Implémenter normalisation avancée
- [ ] **EnrichmentStage**: Ajouter sources externes (Wikipedia, DBpedia)
- [ ] **ValidationStage**: Implémenter règles de validation complètes

### Fonctionnalités à ajouter

- [ ] Support streaming pour gros fichiers
- [ ] Parallélisation des stages indépendants
- [ ] Cache des résultats intermédiaires
- [ ] Reprise sur échec (checkpointing)
- [ ] Métriques et monitoring (Prometheus)
- [ ] Pipeline DAG (non-linéaire)
- [ ] UI pour visualiser pipeline execution

## 🎓 Bonnes Pratiques

1. **Utilisez les factories** pour les cas courants
2. **Désactivez les stages inutiles** pour améliorer performance
3. **Testez avec pipeline minimal** avant d'activer tous les stages
4. **Ajustez batch_size** selon la taille des documents
5. **Validez en mode non-strict** pendant développement
6. **Surveillez les durées** de chaque stage pour optimisation

## 📚 Références

- [FastAPI Async](https://fastapi.tiangolo.com/async/)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- [Sentence Transformers](https://www.sbert.net/)
- [spaCy NER](https://spacy.io/usage/linguistic-features#named-entities)
- [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)

---

**Version**: 1.0.0
**Date**: 2025-01-07
**Auteur**: Jarvis Backend Team
