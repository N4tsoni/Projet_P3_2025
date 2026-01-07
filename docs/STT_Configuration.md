---
tags: [voice, stt, configuration, whisper, groq]
aliases: [STT Config, Speech-to-Text]
---

# 🎤 Configuration Speech-to-Text (STT)

Le système Jarvis supporte **deux providers STT** configurables via variable d'environnement.

---

## 🔧 Providers Disponibles

### Option 1: Groq API (Recommandé ⭐)

**Avantages**:
- ✅ **Très rapide** (~1 seconde pour 5s d'audio)
- ✅ **Meilleure précision** (Whisper-large-v3)
- ✅ **Free tier généreux** (pas de carte bancaire requise)
- ✅ **API stable** et fiable
- ✅ **Pas de setup local**

**Configuration**:

```bash
# .env
STT_PROVIDER=groq
GROQ_API_KEY=gsk_your_api_key_here
```

**Obtenir une clé API**:
1. Aller sur [Groq Console](https://console.groq.com/)
2. Créer un compte (gratuit)
3. Générer une API key
4. Copier dans `.env`

**Modèle utilisé**: `whisper-large-v3`

---

### Option 2: Whisper Local

**Avantages**:
- ✅ **Gratuit** et open-source
- ✅ **Offline** - pas besoin d'internet
- ✅ **Confidentialité** - données restent locales
- ✅ **Pas de clé API** nécessaire

**Inconvénients**:
- ❌ Plus lent (~2-5 secondes selon modèle)
- ❌ Nécessite CPU/GPU local
- ❌ Setup plus complexe

**Configuration**:

```bash
# .env
STT_PROVIDER=whisper
STT_MODEL=base  # tiny, base, small, medium, large
```

**Modèles disponibles**:

| Modèle | Taille | RAM  | Vitesse | Précision |
|--------|--------|------|---------|-----------|
| tiny   | 39 MB  | ~1GB | ⚡⚡⚡    | ⭐⭐      |
| base   | 74 MB  | ~1GB | ⚡⚡⚡    | ⭐⭐⭐    |
| small  | 244 MB | ~2GB | ⚡⚡      | ⭐⭐⭐⭐  |
| medium | 769 MB | ~5GB | ⚡       | ⭐⭐⭐⭐⭐ |
| large  | 1550MB | ~10GB| ⚡       | ⭐⭐⭐⭐⭐ |

**Installation**:

```bash
pip install openai-whisper
```

---

## 🔀 Changer de Provider

### Passer de Whisper Local → Groq

1. Obtenir une clé Groq (voir ci-dessus)
2. Modifier `.env`:
```bash
STT_PROVIDER=groq
GROQ_API_KEY=gsk_xxx
```
3. Redémarrer le backend:
```bash
make restart-backend
# OU
docker-compose restart backend
```

### Passer de Groq → Whisper Local

1. Installer Whisper:
```bash
docker-compose exec backend pip install openai-whisper
```

2. Modifier `.env`:
```bash
STT_PROVIDER=whisper
STT_MODEL=base
```

3. Redémarrer le backend

---

## 🧪 Tester le STT

### Test via API

```bash
# Enregistrer un audio
curl -X POST http://localhost:8000/api/voice/process \
  -F "audio=@test.webm" \
  -F "language=fr"
```

### Test via Interface Web

1. Ouvrir http://localhost:5173
2. Appuyer sur le bouton micro
3. Parler
4. Vérifier la transcription dans l'historique

---

## 📊 Comparaison des Providers

| Critère           | Groq API          | Whisper Local     |
|-------------------|-------------------|-------------------|
| Vitesse           | ⚡⚡⚡ (~1s)      | ⚡⚡ (~3-5s)      |
| Précision         | ⭐⭐⭐⭐⭐        | ⭐⭐⭐⭐          |
| Coût              | Gratuit (limite) | Gratuit (illimité)|
| Offline           | ❌ Non           | ✅ Oui            |
| Setup             | ✅ Simple        | ⚠️ Moyen          |
| Confidentialité   | ⚠️ Cloud         | ✅ Local          |
| CPU/GPU requis    | ❌ Non           | ✅ Oui            |

---

## 🔍 Code Implementation

Le code se trouve dans `backend/src/voice/stt.py`:

```python
def get_stt_provider() -> STTProvider:
    """Get STT provider based on configuration."""
    provider_name = os.getenv("STT_PROVIDER", "whisper-local")

    if provider_name in ["whisper-local", "whisper"]:
        model_name = os.getenv("STT_MODEL", "base")
        return WhisperLocalSTT(model_name=model_name)

    elif provider_name == "groq":
        return GroqSTT()

    else:
        raise ValueError(f"Unknown STT provider: {provider_name}")
```

---

## 🐛 Troubleshooting

### Groq API

**Erreur: "GROQ_API_KEY not found"**
- Vérifier que `GROQ_API_KEY` est dans `.env`
- Redémarrer le backend après modification

**Erreur: "Rate limit exceeded"**
- Free tier a des limites horaires
- Attendre ou upgrader le plan
- Ou passer en Whisper local temporairement

### Whisper Local

**Erreur: "No module named 'whisper'"**
```bash
docker-compose exec backend pip install openai-whisper
```

**Transcription trop lente**
- Utiliser un modèle plus petit (`tiny` ou `base`)
- Ou passer à Groq API

**Erreur: "Audio too short"**
- Vérifier que l'audio dure au moins 1 seconde
- Augmenter le temps d'enregistrement

---

## 🌍 Langues Supportées

Les deux providers supportent multilingue:

**Principales langues**:
- 🇫🇷 Français
- 🇬🇧 Anglais
- 🇪🇸 Espagnol
- 🇩🇪 Allemand
- 🇮🇹 Italien
- 🇵🇹 Portugais
- 🇨🇳 Chinois
- 🇯🇵 Japonais
- et 90+ autres...

**Configuration**:
```python
# Dans l'API call
await transcribe_audio(audio_path, language="fr")  # ou "en", "es", etc.
```

---

## 📈 Recommandations

### Pour Développement Local
- **Groq API** - Setup rapide, pas de config GPU

### Pour Production
- **Groq API** - Performance optimale, scaling facile
- Backup sur Whisper Local en cas de downtime API

### Pour Self-Hosted / Offline
- **Whisper Local** avec modèle `base` ou `small`

### Pour Confidentialité Max
- **Whisper Local** - Données jamais envoyées au cloud

---

## 🔗 Liens Utiles

- [Groq Documentation](https://console.groq.com/docs)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Whisper Models](https://github.com/openai/whisper#available-models-and-languages)

---

**Dernière mise à jour**: 2026-01-07
