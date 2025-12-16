# Quick Start - Jarvis Voice Assistant

## Configuration Rapide

### 1. Créer le fichier .env

```bash
cp .env.example .env
```

### 2. Ajouter votre clé OpenRouter

Éditez `.env` et ajoutez votre clé :

```bash
# LLM API Keys
OPENROUTER_API_KEY=sk-or-v1-votre-clé-ici

# Modèle à utiliser (options recommandées)
LLM_MODEL=anthropic/claude-3.5-sonnet      # Recommandé, excellent
# LLM_MODEL=openai/gpt-4-turbo             # Alternative
# LLM_MODEL=meta-llama/llama-3.1-70b-instruct  # Gratuit

# STT (Speech-to-Text) - Whisper local par défaut, pas de clé nécessaire
STT_PROVIDER=whisper-local
STT_MODEL=base  # ou tiny (plus rapide) ou small (meilleure qualité)

# TTS (Text-to-Speech) - Edge TTS gratuit, pas de clé nécessaire
TTS_PROVIDER=edge-tts
TTS_VOICE=fr-FR-DeniseNeural  # Voix française féminine
# TTS_VOICE=fr-FR-HenriNeural  # Voix française masculine
```

### 3. Lancer l'application

```bash
# Build et lancement
make build
make up

# Ou directement
docker compose up --build -d
```

### 4. Attendre que tout démarre

```bash
# Voir les logs
make logs

# Attendre que vous voyiez:
# - Neo4j: "Started."
# - App: "Application startup complete"
```

### 5. Ouvrir l'interface

Allez sur **http://localhost:8000**

## Utilisation

### Interface Vocale

1. **Maintenez** le bouton microphone enfoncé
2. **Parlez** - ex: "Bonjour Jarvis, comment vas-tu ?"
3. **Relâchez** le bouton
4. Attendez la transcription et la réponse vocale

### Exemples de questions

```
"Bonjour Jarvis, présente-toi"
"Quelle est la capitale de la France ?"
"Retiens que j'aime le café le matin"
"Rappelle-moi ce que j'aime le matin"
"Raconte-moi une blague"
```

## Configuration des Modèles

### Modèles OpenRouter Recommandés

**Gratuits:**
- `meta-llama/llama-3.1-70b-instruct` - Très bon, gratuit
- `google/gemini-flash-1.5` - Rapide, gratuit

**Payants (excellente qualité):**
- `anthropic/claude-3.5-sonnet` - Recommandé ⭐
- `openai/gpt-4-turbo` - Excellent aussi
- `google/gemini-pro-1.5` - Bonne alternative

### STT (Speech-to-Text)

**Option 1: Whisper Local (gratuit, recommandé)**
```bash
STT_PROVIDER=whisper-local
STT_MODEL=base  # tiny < base < small < medium < large
```

**Option 2: Groq (gratuit, très rapide)**
1. Créez un compte sur https://console.groq.com
2. Obtenez une API key
3. Configurez:
```bash
STT_PROVIDER=groq
GROQ_API_KEY=votre-clé-groq
```

### TTS (Text-to-Speech)

**Option 1: Edge TTS (gratuit, recommandé)**
```bash
TTS_PROVIDER=edge-tts
TTS_VOICE=fr-FR-DeniseNeural
```

Voix disponibles:
- `fr-FR-DeniseNeural` - Française, féminine
- `fr-FR-HenriNeural` - Français, masculin
- `en-US-AriaNeural` - Anglaise, féminine
- `en-US-GuyNeural` - Anglais, masculin

**Option 2: Coqui TTS (local, plus lent)**
```bash
TTS_PROVIDER=coqui-local
```

## Troubleshooting

### "OPENROUTER_API_KEY not found"

Vérifiez que vous avez créé `.env` et ajouté votre clé.

### Whisper très lent

Utilisez un modèle plus petit:
```bash
STT_MODEL=tiny  # Le plus rapide
```

Ou passez à Groq (beaucoup plus rapide).

### Erreur lors de la transcription

Vérifiez les logs:
```bash
make logs-app
```

Si Whisper échoue, essayez un modèle plus petit ou Groq.

### Audio de réponse ne joue pas

Vérifiez que Edge TTS est configuré:
```bash
docker compose logs app | grep -i "tts"
```

## Commandes Utiles

```bash
# Voir les logs en temps réel
make logs

# Juste l'application
make logs-app

# Redémarrer l'application
make restart

# Accéder au shell
make shell

# Nettoyer et redémarrer
make clean-docker
make build
make up
```

## Prochaines Étapes

Une fois que vous avez testé la voix:

1. ✅ Interface web fonctionne
2. ✅ Transcription (STT) fonctionne
3. ✅ Agent répond
4. ✅ Synthèse vocale (TTS) fonctionne
5. ⏳ Ajouter Graphiti pour la mémoire
6. 📦 Préparer l'ESP32

## Support

Si vous rencontrez des problèmes:

1. Vérifiez les logs: `make logs-app`
2. Vérifiez que tous les services tournent: `docker compose ps`
3. Vérifiez votre .env
4. Essayez de redémarrer: `make restart`

Bon test ! 🎙️
