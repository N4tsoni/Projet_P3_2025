# Guide de Setup - POC GraphRAG

## Étapes de démarrage

### 1. Créer le fichier .env

```bash
cp .env.example .env
```

Puis éditez `.env` et ajoutez votre clé API OpenAI :
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### 2. Build et lancement des containers

```bash
# Build des images
docker-compose build

# Lancer les services
docker-compose up -d

# Vérifier que les services tournent
docker-compose ps
```

### 3. Attendre que Neo4j soit prêt

Vérifiez que Neo4j est disponible :
```bash
# Voir les logs Neo4j
docker-compose logs -f neo4j

# Attendre le message "Started."
```

Ou accédez à http://localhost:7474 et connectez-vous avec :
- Username: `neo4j`
- Password: `graphrag2024` (ou celle dans votre .env)

### 4. Accéder à l'interface web Jarvis

Ouvrez votre navigateur et allez sur http://localhost:8000

Vous devriez voir l'interface vocale de Jarvis avec un bouton microphone.

### 5. Tester la connexion Graphiti (optionnel)

```bash
# Accéder au container de l'app
docker-compose exec app bash

# Dans le container, exécuter le test avec Poetry
poetry run python src/graph/test_connection.py
```

Vous devriez voir :
```
✅ Neo4j connection successful
✅ Graphiti initialized successfully
✅ Episode added: X nodes created
✅ Search completed: X results found
🎉 All tests passed!
```

### 5. (Optionnel) Explorer Neo4j

Accédez à http://localhost:7474 et exécutez des requêtes Cypher :

```cypher
// Voir tous les noeuds
MATCH (n) RETURN n LIMIT 25;

// Voir les épisodes créés
MATCH (e:EpisodicNode) RETURN e;

// Voir toutes les relations
MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50;
```

## Troubleshooting

### Erreur: "Connection refused" à Neo4j

Solution :
```bash
# Vérifier que Neo4j tourne
docker-compose ps

# Relancer Neo4j
docker-compose restart neo4j

# Attendre 10-15 secondes et réessayer
```

### Erreur: "OpenAI API key not found"

Solution :
- Vérifiez que `.env` contient `OPENAI_API_KEY=...`
- Relancez les containers : `docker-compose restart app`

### Erreur: "Module not found"

Solution :
```bash
# Rebuild l'image
docker-compose build app

# Relancer
docker-compose up -d app
```

### Neo4j demande de changer le mot de passe

Si c'est la première fois :
1. Allez sur http://localhost:7474
2. Connectez-vous avec `neo4j` / `neo4j`
3. Changez le mot de passe pour `graphrag2024` (ou mettez à jour .env)

## Prochaines étapes

Une fois les tests passés, vous pouvez :
1. Créer des modèles de données comptables (Phase 2)
2. Implémenter l'ingestion de données
3. Créer les agents comptables

Voir [TODO.md](TODO.md) pour la liste complète des tâches.
