"""
Script pour créer les notebooks de test.
"""
import json
from pathlib import Path

NOTEBOOKS_DIR = Path(__file__).parent / "notebooks"
NOTEBOOKS_DIR.mkdir(exist_ok=True)

notebooks = {
    "01_test_stt_groq.ipynb": {
        "title": "Test STT - Groq Whisper",
        "cells": [
            {
                "type": "markdown",
                "content": "# 🎤 Test STT - Groq Whisper API\n\nTestez la transcription audio avec Groq."
            },
            {
                "type": "code",
                "content": "import sys\nsys.path.append('/app')\nfrom src.voice.stt import transcribe_audio\nfrom pathlib import Path\nimport asyncio"
            },
            {
                "type": "code",
                "content": "# Créer un audio de test\nimport edge_tts\n\ntext = \"Bonjour, test de transcription\"\naudio_path = Path('/tmp/test.mp3')\n\nasync def create():\n    tts = edge_tts.Communicate(text, 'fr-FR-DeniseNeural')\n    await tts.save(str(audio_path))\n\nawait create()\nprint(f\"Audio créé: {audio_path}\")"
            },
            {
                "type": "code",
                "content": "# Transcrire\nimport time\n\nstart = time.time()\ntranscription = await transcribe_audio(audio_path, 'fr')\nduration = time.time() - start\n\nprint(f\"Original: {text}\")\nprint(f\"Transcription: {transcription}\")\nprint(f\"Temps: {duration:.2f}s\")"
            }
        ]
    },
    "02_test_tts_edge.ipynb": {
        "title": "Test TTS - Edge TTS",
        "cells": [
            {
                "type": "markdown",
                "content": "# 🔊 Test TTS - Edge TTS\n\nTestez la synthèse vocale."
            },
            {
                "type": "code",
                "content": "import sys\nsys.path.append('/app')\nfrom src.voice.tts import synthesize_speech\nfrom pathlib import Path\nimport asyncio"
            },
            {
                "type": "code",
                "content": "# Synthétiser du texte\ntext = \"Bonjour, je suis Jarvis, votre assistant vocal intelligent.\"\noutput_path = Path('/tmp/tts_test.mp3')\n\nawait synthesize_speech(text, output_path)\nprint(f\"Audio généré: {output_path}\")"
            },
            {
                "type": "code",
                "content": "# Tester différentes voix\nvoices = [\n    'fr-FR-DeniseNeural',\n    'fr-FR-HenriNeural',\n    'fr-CA-SylvieNeural'\n]\n\nfor voice in voices:\n    print(f\"Test voix: {voice}\")\n    # TODO: tester chaque voix"
            }
        ]
    },
    "03_test_agent_openrouter.ipynb": {
        "title": "Test Agent - OpenRouter",
        "cells": [
            {
                "type": "markdown",
                "content": "# 🤖 Test Agent Conversationnel\n\nTestez l'agent avec OpenRouter/Claude."
            },
            {
                "type": "code",
                "content": "import sys\nsys.path.append('/app')\nfrom src.agents.jarvis_agent import get_agent\nimport asyncio"
            },
            {
                "type": "code",
                "content": "# Conversation simple\nagent = get_agent()\n\nquestions = [\n    \"Bonjour, qui es-tu?\",\n    \"Quelle est la capitale de la France?\",\n    \"Mémorise que j'aime le café\"\n]\n\nfor q in questions:\n    response = await agent.chat(q)\n    print(f\"Q: {q}\")\n    print(f\"R: {response}\\n\")"
            }
        ]
    },
    "04_test_neo4j_graphiti.ipynb": {
        "title": "Test Knowledge Graph",
        "cells": [
            {
                "type": "markdown",
                "content": "# 🕸️ Test Knowledge Graph - Neo4j & Graphiti\n\nTestez les opérations sur le knowledge graph."
            },
            {
                "type": "code",
                "content": "import sys\nsys.path.append('/app')\nfrom src.graph.graphiti_client import get_graphiti_client\nimport asyncio"
            },
            {
                "type": "code",
                "content": "# Test connexion\nclient = get_graphiti_client()\nprint(\"Client Graphiti initialisé\")"
            },
            {
                "type": "code",
                "content": "# Ajouter un épisode de test\nfrom datetime import datetime\n\nnodes = await client.add_episode(\n    name=\"test_episode\",\n    content=\"L'utilisateur aime le café et habite à Paris.\",\n    source_description=\"Test manuel\",\n    reference_time=datetime.now().isoformat()\n)\n\nprint(f\"Nodes créés: {len(nodes)}\")"
            }
        ]
    },
    "05_pipeline_complet.ipynb": {
        "title": "Pipeline Complet",
        "cells": [
            {
                "type": "markdown",
                "content": "# 🚀 Pipeline Vocal Complet\n\nTest end-to-end: Audio → STT → Agent → TTS → Audio"
            },
            {
                "type": "code",
                "content": "import sys\nsys.path.append('/app')\nfrom src.services.voice_service import get_voice_service\nfrom pathlib import Path\nimport asyncio"
            },
            {
                "type": "code",
                "content": "# Créer un mock audio file\nfrom unittest.mock import AsyncMock\n\nmock_audio = AsyncMock()\nmock_audio.filename = 'test.webm'\nmock_audio.content_type = 'audio/webm'\nmock_audio.read = AsyncMock(return_value=b'fake')\n\nprint(\"Mock audio prêt\")"
            },
            {
                "type": "code",
                "content": "# Test pipeline complet\nservice = get_voice_service()\n\ntry:\n    transcription, response, audio_url = await service.process_voice_input(mock_audio)\n    print(f\"Transcription: {transcription}\")\n    print(f\"Réponse: {response}\")\n    print(f\"Audio: {audio_url}\")\nexcept Exception as e:\n    print(f\"Erreur: {e}\")"
            }
        ]
    }
}

def create_notebook(filename, config):
    """Créer un notebook Jupyter."""
    cells = []
    
    for cell_config in config["cells"]:
        cell = {
            "cell_type": cell_config["type"],
            "metadata": {},
            "source": [cell_config["content"]]
        }
        
        if cell_config["type"] == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
        
        cells.append(cell)
    
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    output_path = NOTEBOOKS_DIR / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
    
    print(f"✅ Créé: {output_path}")

if __name__ == "__main__":
    print("Création des notebooks...")
    for filename, config in notebooks.items():
        create_notebook(filename, config)
    print(f"\n🎉 {len(notebooks)} notebooks créés dans {NOTEBOOKS_DIR}")
