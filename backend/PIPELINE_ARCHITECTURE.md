# Pipeline Architecture - Vue Détaillée

## 📐 Architecture Complète

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          KNOWLEDGE GRAPH PIPELINE                            │
│                                                                              │
│  Input: Document (CSV, JSON, PDF, TXT, XLSX, XML)                          │
│  Output: Neo4j Knowledge Graph                                              │
└─────────────────────────────────────────────────────────────────────────────┘

                                      │
                                      ↓
                          ┌────────────────────┐
                          │  PipelineContext   │
                          │                    │
                          │  - file_path       │
                          │  - filename        │
                          │  - file_format     │
                          │  - document        │
                          └────────────────────┘
                                      │
                                      ↓
╔═════════════════════════════════════════════════════════════════════════════╗
║                           STAGE 1: PARSING                                  ║
╠═════════════════════════════════════════════════════════════════════════════╣
║  Classe: ParsingStage                                                       ║
║  Responsabilité: Parse documents → structured data                          ║
║                                                                              ║
║  Formats:                                                                    ║
║    ✅ CSV     → pandas DataFrame + metadata                                 ║
║    ⏳ JSON    → dict/list                                                   ║
║    ⏳ PDF     → extracted text                                              ║
║    ⏳ TXT     → raw text                                                    ║
║    ⏳ XLSX    → DataFrame                                                   ║
║    ⏳ XML     → structured dict                                             ║
║                                                                              ║
║  Sortie: context.raw_data, context.metadata                                 ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      ↓
╔═════════════════════════════════════════════════════════════════════════════╗
║                           STAGE 2: CHUNKING                                 ║
╠═════════════════════════════════════════════════════════════════════════════╣
║  Classe: ChunkingStage                                                      ║
║  Responsabilité: Split data into manageable chunks                          ║
║                                                                              ║
║  Stratégies:                                                                 ║
║    • CSV: Each row = 1 chunk                                                ║
║    • Text: Sliding window with overlap                                      ║
║    • JSON: Split by structure depth                                         ║
║                                                                              ║
║  Params:                                                                     ║
║    - chunk_size: 1000 chars (default)                                       ║
║    - chunk_overlap: 200 chars (default)                                     ║
║                                                                              ║
║  Sortie: context.chunks = [{id, content, type, metadata}, ...]             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      ↓
╔═════════════════════════════════════════════════════════════════════════════╗
║                           STAGE 3: EMBEDDING                                ║
╠═════════════════════════════════════════════════════════════════════════════╣
║  Classe: EmbeddingStage                                                     ║
║  Responsabilité: Generate vector embeddings for semantic search             ║
║                                                                              ║
║  Modèles:                                                                    ║
║    • Sentence-Transformers: all-MiniLM-L6-v2 (384 dims)                    ║
║    • OpenAI: text-embedding-3-small (1536 dims)                             ║
║    • Custom: BERT, RoBERTa, etc.                                            ║
║                                                                              ║
║  Params:                                                                     ║
║    - model_name: "all-MiniLM-L6-v2"                                         ║
║    - batch_size: 32                                                         ║
║                                                                              ║
║  Sortie: context.embeddings = [[0.1, 0.2, ...], ...]                       ║
║  Usage: Similarity search, clustering, retrieval                            ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      ↓
╔═════════════════════════════════════════════════════════════════════════════╗
║                           STAGE 4: NER                                      ║
╠═════════════════════════════════════════════════════════════════════════════╣
║  Classe: NERStage                                                           ║
║  Responsabilité: Named Entity Recognition with NLP models                   ║
║                                                                              ║
║  Modèles:                                                                    ║
║    • spaCy: en_core_web_sm, fr_core_news_sm                                ║
║    • Transformers: dbmdz/bert-large-cased-finetuned-conll03-english        ║
║                                                                              ║
║  Entités détectées:                                                          ║
║    PERSON, ORG, GPE, LOC, DATE, TIME, MONEY, PERCENT, etc.                 ║
║                                                                              ║
║  Params:                                                                     ║
║    - model_name: "en_core_web_sm"                                           ║
║                                                                              ║
║  Sortie: Enrichit context.entities (ajoute, ne remplace pas)               ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      ↓
╔═════════════════════════════════════════════════════════════════════════════╗
║                         STAGE 5: EXTRACTION (LLM)                           ║
╠═════════════════════════════════════════════════════════════════════════════╣
║  Classe: ExtractionStage                                                    ║
║  Responsabilité: Extract structured entities & relations using LLM          ║
║                                                                              ║
║  Agents:                                                                     ║
║    1. EntityExtractorAgent                                                  ║
║       - Utilise Claude 3.5 Sonnet via OpenRouter                            ║
║       - Batch processing (50 records/batch)                                 ║
║       - Extract: Person, Movie, Studio, Org, Location, Concept              ║
║       - Déduplication par (type, name)                                      ║
║                                                                              ║
║    2. RelationExtractorAgent                                                ║
║       - Utilise Claude 3.5 Sonnet via OpenRouter                            ║
║       - Batch processing (50 records/batch)                                 ║
║       - Extract: ACTED_IN, DIRECTED, PRODUCED_BY, KNOWS, etc.               ║
║       - Validation: références aux entités extraites                         ║
║                                                                              ║
║  Params:                                                                     ║
║    - batch_size: 50                                                         ║
║                                                                              ║
║  Sortie:                                                                     ║
║    - context.entities = [Entity, ...]                                       ║
║    - context.relations = [Relation, ...]                                    ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      ↓
╔═════════════════════════════════════════════════════════════════════════════╗
║                        STAGE 6: TRANSFORMATION                              ║
╠═════════════════════════════════════════════════════════════════════════════╣
║  Classe: TransformationStage                                                ║
║  Responsabilité: Normalize and transform extracted data                     ║
║                                                                              ║
║  Transformations:                                                            ║
║    • Name normalization (casing, accents, etc.)                             ║
║    • Type conversion (string → int, date parsing)                           ║
║    • Property standardization                                                ║
║    • Advanced deduplication (fuzzy matching)                                ║
║    • Entity merging                                                          ║
║    • Relation type standardization                                           ║
║                                                                              ║
║  Exemple:                                                                    ║
║    "tom hanks" → "Tom Hanks"                                                ║
║    "1994" → Date(1994, 1, 1)                                                ║
║    "directed_by" → "DIRECTED"                                               ║
║                                                                              ║
║  Sortie: Transforme context.entities et context.relations en place          ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      ↓
╔═════════════════════════════════════════════════════════════════════════════╗
║                         STAGE 7: ENRICHMENT                                 ║
╠═════════════════════════════════════════════════════════════════════════════╣
║  Classe: EnrichmentStage                                                    ║
║  Responsabilité: Enrich entities with external information                  ║
║                                                                              ║
║  Sources:                                                                    ║
║    • Wikipedia API                                                           ║
║    • DBpedia SPARQL                                                          ║
║    • Wikidata                                                                ║
║    • Custom APIs                                                             ║
║                                                                              ║
║  Enrichissements:                                                            ║
║    • Biographical info (birth date, nationality, etc.)                      ║
║    • Descriptions and summaries                                              ║
║    • Images and media                                                        ║
║    • Related entities                                                        ║
║    • Confidence scores                                                       ║
║    • Temporal information                                                    ║
║    • Graph metrics (centrality, PageRank)                                   ║
║                                                                              ║
║  Sortie:                                                                     ║
║    - context.enriched_entities                                              ║
║    - context.enriched_relations                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      ↓
╔═════════════════════════════════════════════════════════════════════════════╗
║                         STAGE 8: VALIDATION                                 ║
╠═════════════════════════════════════════════════════════════════════════════╣
║  Classe: ValidationStage                                                    ║
║  Responsabilité: Validate data quality and consistency                      ║
║                                                                              ║
║  Validations:                                                                ║
║    ✓ Required fields present (type, name, etc.)                             ║
║    ✓ Data types correct (string, int, float, date)                          ║
║    ✓ Enum values valid (EntityType, RelationType)                           ║
║    ✓ References valid (relations point to existing entities)                ║
║    ✓ No duplicates (after deduplication)                                    ║
║    ✓ Constraints respected (min/max values, patterns)                       ║
║    ✓ Properties schema valid                                                 ║
║                                                                              ║
║  Modes:                                                                      ║
║    • strict=True: Fail pipeline on any error                                ║
║    • strict=False: Log warnings, continue                                   ║
║                                                                              ║
║  Params:                                                                     ║
║    - strict: False (default)                                                ║
║                                                                              ║
║  Sortie:                                                                     ║
║    - context.validation_results = {                                         ║
║        "entities": {total, valid, invalid, errors, warnings},               ║
║        "relations": {...},                                                  ║
║        "total_errors": N,                                                   ║
║        "total_warnings": M                                                  ║
║      }                                                                       ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      ↓
╔═════════════════════════════════════════════════════════════════════════════╗
║                          STAGE 9: STORAGE                                   ║
╠═════════════════════════════════════════════════════════════════════════════╣
║  Classe: StorageStage                                                       ║
║  Responsabilité: Persist knowledge graph to Neo4j                           ║
║                                                                              ║
║  Opérations Neo4j:                                                           ║
║    1. Create entity nodes                                                   ║
║       MERGE (e:EntityType {name: $name})                                    ║
║       SET e += $properties                                                  ║
║                                                                              ║
║    2. Create relations                                                      ║
║       MATCH (from {name: $from_name})                                       ║
║       MATCH (to {name: $to_name})                                           ║
║       MERGE (from)-[r:RELATION_TYPE]->(to)                                  ║
║       SET r += $properties                                                  ║
║                                                                              ║
║  Features:                                                                   ║
║    • Batch operations (50 entities/batch)                                   ║
║    • Transaction management                                                  ║
║    • MERGE to avoid duplicates                                              ║
║    • Return Neo4j internal IDs                                              ║
║    • Error handling and rollback                                            ║
║                                                                              ║
║  Sortie:                                                                     ║
║    - context.storage_ids = {                                                ║
║        "entity_ids": ["1", "2", "3", ...],                                  ║
║        "relation_ids": ["10", "11", "12", ...]                              ║
║      }                                                                       ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                      │
                                      ↓
                          ┌────────────────────┐
                          │    Neo4j Graph     │
                          │                    │
                          │  Nodes: 150        │
                          │  Relationships: 280│
                          └────────────────────┘
                                      │
                                      ↓
                               ✅ DONE


═══════════════════════════════════════════════════════════════════════════════
                              STAGE RESULTS
═══════════════════════════════════════════════════════════════════════════════

StageResult for each stage:
┌──────────────────┬──────────┬──────────┬────────────────────────────┐
│ Stage            │ Status   │ Duration │ Output                     │
├──────────────────┼──────────┼──────────┼────────────────────────────┤
│ ParsingStage     │ ✅ DONE  │ 0.15s    │ 100 rows, 5 columns        │
│ ChunkingStage    │ ✅ DONE  │ 0.02s    │ 100 chunks                 │
│ EmbeddingStage   │ ⏭️ SKIP  │ 0.00s    │ N/A (disabled)             │
│ NERStage         │ ⏭️ SKIP  │ 0.00s    │ N/A (disabled)             │
│ ExtractionStage  │ ✅ DONE  │ 12.5s    │ 50 entities, 120 relations │
│ Transformation   │ ✅ DONE  │ 0.30s    │ 50 → 48 entities (merged)  │
│ EnrichmentStage  │ ✅ DONE  │ 2.10s    │ Added 25 properties        │
│ ValidationStage  │ ✅ DONE  │ 0.05s    │ 0 errors, 3 warnings       │
│ StorageStage     │ ✅ DONE  │ 1.20s    │ Stored to Neo4j            │
└──────────────────┴──────────┴──────────┴────────────────────────────┘

Total Duration: 16.32s
Status: ✅ SUCCESS
```

## 🎯 Pipelines Préconfigurées

### 1. CSV Pipeline (Optimisé Structuré)
```
ParsingStage → ExtractionStage → TransformationStage → ValidationStage → StorageStage
```
**Durée estimée**: ~10-15s pour 100 rows
**Usage**: Données tabulaires (CSV, XLSX)

### 2. Text Pipeline (Complet Non-structuré)
```
ParsingStage → ChunkingStage → EmbeddingStage → NERStage →
ExtractionStage → TransformationStage → EnrichmentStage →
ValidationStage → StorageStage
```
**Durée estimée**: ~30-60s pour 10 pages
**Usage**: PDF, TXT, DOCX

### 3. Minimal Pipeline (Rapide)
```
ParsingStage → ExtractionStage → StorageStage
```
**Durée estimée**: ~5-8s pour 100 rows
**Usage**: Tests, prototypage

### 4. Default Pipeline (Complet)
```
Tous les stages activés
```
**Durée estimée**: ~40-90s selon taille
**Usage**: Production avec toutes fonctionnalités

## 📊 Métriques et Performance

| Stage            | Typical Time | Bottleneck Factor |
|------------------|--------------|-------------------|
| Parsing          | 0.1-0.5s     | ⚡ Fast           |
| Chunking         | 0.01-0.1s    | ⚡ Fast           |
| Embedding        | 1-5s         | 🐢 Slow (GPU)     |
| NER              | 0.5-2s       | ⚡ Medium         |
| Extraction (LLM) | 10-30s       | 🐢🐢 Very Slow    |
| Transformation   | 0.1-0.5s     | ⚡ Fast           |
| Enrichment       | 1-10s        | 🐢 Slow (API)     |
| Validation       | 0.01-0.1s    | ⚡ Fast           |
| Storage          | 0.5-2s       | ⚡ Medium         |

**Bottleneck principal**: ExtractionStage (LLM API calls)

## 🔧 Optimisations

### Parallélisation
- Stages indépendants peuvent être parallélisés
- Batch processing pour LLM et embeddings
- Async I/O pour Neo4j et APIs

### Caching
- Cache embeddings pour chunks répétés
- Cache NER results
- Cache enrichment API responses

### Streaming
- Process large files in streaming mode
- Avoid loading entire file in memory
- Yield results progressively
