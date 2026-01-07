# 🚀 Démarrage Rapide - Jarvis

## Étape 1: Configuration (30 secondes)

Ouvrez le fichier `.env` et remplacez cette ligne:

```bash
OPENROUTER_API_KEY=sk-or-v1-VOTRE-CLE-ICI
```

Par votre vraie clé OpenRouter.

**Où obtenir une clé OpenRouter ?**
1. Allez sur https://openrouter.ai
2. Créez un compte (gratuit)
3. Allez dans "Keys"
4. Créez une nouvelle clé

## Étape 2: Lancer Jarvis

```bash
make build
make up
```

Attendez 30 secondes que tout démarre.

## Étape 3: Tester !

Ouvrez votre navigateur: **http://localhost:5173** (Frontend Vue.js)

> L'API backend est sur http://localhost:8000

### Premier test
1. Maintenez le bouton microphone 🎤
2. Dites: **"Bonjour Jarvis, présente-toi"**
3. Relâchez le bouton
4. Écoutez la réponse !

### Tests supplémentaires

```
"Quelle est la capitale de la France ?"
"Raconte-moi une blague"
"Retiens que j'aime le café"
"Qu'est-ce que j'aime boire ?"
```

## Commandes Utiles

```bash
make logs       # Voir tous les logs
make logs-app   # Voir juste l'application
make restart    # Redémarrer
make down       # Arrêter tout
```

## Problèmes ?

### "OPENROUTER_API_KEY not found"
→ Vérifiez que vous avez bien modifié `.env` avec votre clé

### Whisper est lent
→ Dans `.env`, changez:
```bash
STT_MODEL=tiny  # Au lieu de base
```

### Voir les erreurs
```bash
make logs-app
```

---

**C'est tout !** Jarvis est prêt à vous parler 🎙️
