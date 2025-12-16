# Interface Web Jarvis - Guide d'Utilisation

## Vue d'ensemble

L'interface web permet de tester le système vocal de Jarvis avant l'arrivée du matériel ESP32. Elle utilise le microphone de votre ordinateur pour capturer l'audio.

## Fonctionnalités

### Interface Actuelle

✅ **Implémenté:**
- Interface web moderne et responsive
- Bouton push-to-talk (maintenir pour parler)
- Visualisation audio en temps réel (waveform)
- Upload audio vers backend FastAPI
- Affichage des messages
- Player audio pour la réponse

⏳ **À implémenter:**
- Speech-to-Text (Whisper)
- Agent conversationnel
- Text-to-Speech
- Intégration Graphiti

## Utilisation

### Démarrer l'application

```bash
# Lancer avec Docker
make up

# Ou manuellement
docker compose up -d
```

### Accéder à l'interface

Ouvrez votre navigateur à : **http://localhost:8000**

### Utiliser le bouton vocal

1. **Appuyez et maintenez** le bouton microphone
2. **Parlez** - vous verrez la visualisation audio
3. **Relâchez** le bouton pour envoyer
4. Attendez la réponse de Jarvis

### États de l'interface

- 🟢 **Prêt** : En attente d'input
- 🔴 **En écoute** : Enregistrement en cours
- ⚙️ **Traitement** : Backend traite la requête
- 🔊 **Jarvis parle** : Lecture de la réponse audio

## Architecture

### Frontend (static/)

**index.html**
- Interface utilisateur
- Design moderne avec gradients
- Responsive

**app.js**
- MediaRecorder API pour capture audio
- Web Audio API pour visualisation
- Fetch API pour communication backend

### Backend (src/api/)

**main.py**
- FastAPI application
- Endpoints REST pour vocal
- Gestion des fichiers audio

### Flow de données

```
[Navigateur] → MediaRecorder → Audio Blob
    ↓
[Upload] → POST /api/voice/process
    ↓
[Backend] → [STT] → [Agent] → [TTS]
    ↓
[Response] → JSON + Audio URL
    ↓
[Navigateur] → Affichage + Lecture audio
```

## Endpoints API

### GET /
Sert l'interface web

### GET /health
Health check de l'API

### POST /api/voice/process
Traite l'audio vocal

**Request:**
- Form data avec fichier audio (audio/webm)

**Response:**
```json
{
  "success": true,
  "transcription": "Texte transcrit",
  "response": "Réponse de Jarvis",
  "audio_url": "/static/response.mp3"
}
```

### GET /api/knowledge/query?q=...
Interroge le knowledge graph

### POST /api/knowledge/add
Ajoute des connaissances manuellement

## Configuration Audio

### Format d'enregistrement
- **Container**: WebM
- **Codec**: Opus (navigateur)
- **Channels**: Mono (1)
- **Sample Rate**: 16kHz
- **Features**: Echo cancellation, Noise suppression

### Permissions requises

Le navigateur demandera l'accès au microphone au premier usage.

**Chrome/Edge**: ✅ Supporté
**Firefox**: ✅ Supporté
**Safari**: ⚠️ Peut nécessiter HTTPS en production

## Développement

### Ajouter de nouveaux endpoints

Éditez `src/api/main.py`:

```python
@app.post("/api/custom")
async def custom_endpoint(data: dict):
    # Votre code
    return {"result": "success"}
```

### Modifier l'interface

Éditez `static/index.html` et `static/app.js`

### Hot reload

FastAPI est configuré avec `--reload`, les changements Python sont automatiques.

Pour le frontend, rechargez simplement la page.

## Prochaines étapes

1. ✅ Interface web fonctionnelle
2. ⏳ Implémenter STT (Whisper)
3. ⏳ Créer agent conversationnel
4. ⏳ Implémenter TTS
5. ⏳ Intégrer Graphiti
6. 📦 Migrer vers ESP32 (quand matériel arrive)

## Troubleshooting

### Microphone ne fonctionne pas
- Vérifiez les permissions du navigateur
- Essayez HTTPS (certains navigateurs requièrent SSL)
- Vérifiez qu'aucune autre app n'utilise le micro

### Erreur 500 sur /api/voice/process
- Vérifiez les logs: `make logs-app`
- Le backend est peut-être en cours de démarrage

### Audio ne s'enregistre pas
- Vérifiez la console du navigateur (F12)
- Format WebM peut ne pas être supporté (rare)

### Interface ne charge pas
- Vérifiez que le container tourne: `make up`
- Port 8000 doit être disponible
- Vérifiez http://localhost:8000/health

## Debug

### Voir les logs backend

```bash
make logs-app
```

### Console navigateur

Appuyez sur F12 pour voir les logs JavaScript

### Tester l'API directement

```bash
# Health check
curl http://localhost:8000/health

# Upload audio test
curl -X POST http://localhost:8000/api/voice/process \
  -F "audio=@test.webm"
```
