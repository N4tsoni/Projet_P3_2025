"""
FastAPI application for Jarvis voice assistant.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import os
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Jarvis Voice Assistant API",
    description="Backend API for Jarvis voice assistant with GraphRAG",
    version="0.1.0",
)

# CORS configuration for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (web interface)
static_dir = Path(__file__).parent.parent.parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def root():
    """Serve the web interface."""
    web_interface = static_dir / "index.html"
    if web_interface.exists():
        return FileResponse(web_interface)
    return {"message": "Jarvis Voice Assistant API", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Jarvis Voice Assistant",
        "version": "0.1.0",
    }


@app.post("/api/voice/process")
async def process_voice(audio: UploadFile = File(...)):
    """
    Process voice input: STT -> Agent -> TTS -> Return audio response.

    Args:
        audio: Audio file (WAV, WebM, etc.)

    Returns:
        JSON with transcription, response text, and audio URL
    """
    try:
        from src.voice.stt import transcribe_audio
        from src.voice.tts import synthesize_speech
        from src.agents.jarvis_agent import get_agent
        import uuid

        logger.info(f"Received audio file: {audio.filename}, type: {audio.content_type}")

        # Save uploaded audio temporarily
        temp_dir = Path("/app/data/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique ID for this request
        request_id = str(uuid.uuid4())[:8]

        audio_path = temp_dir / f"input_{request_id}.webm"
        with open(audio_path, "wb") as f:
            content = await audio.read()
            f.write(content)

        logger.info(f"Saved audio to {audio_path}, size: {len(content)} bytes")

        # Step 1: Speech-to-Text
        logger.info("Step 1: Transcribing audio...")
        transcription = await transcribe_audio(audio_path, language="fr")
        logger.info(f"Transcription: {transcription}")

        # Step 2: Agent processes the message
        logger.info("Step 2: Processing with agent...")
        agent = get_agent()
        agent_response = await agent.chat(transcription)
        logger.info(f"Agent response: {agent_response}")

        # Step 3: Text-to-Speech
        logger.info("Step 3: Synthesizing speech...")
        response_audio_path = static_dir / f"response_{request_id}.mp3"
        await synthesize_speech(agent_response, response_audio_path)

        response_audio_url = f"/static/response_{request_id}.mp3"
        logger.info(f"Audio response: {response_audio_url}")

        # Step 4: TODO - Update knowledge graph with conversation

        # Clean up input audio
        audio_path.unlink(missing_ok=True)

        return JSONResponse({
            "success": True,
            "transcription": transcription,
            "response": agent_response,
            "audio_url": response_audio_url,
        })

    except Exception as e:
        logger.error(f"Error processing voice: {e}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge/query")
async def query_knowledge(q: str):
    """
    Query the knowledge graph.

    Args:
        q: Query string

    Returns:
        Results from knowledge graph
    """
    try:
        # TODO: Implement GraphRAG query
        results = {
            "query": q,
            "results": [],
            "message": "GraphRAG query à implémenter"
        }

        return results

    except Exception as e:
        logger.error(f"Error querying knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/knowledge/add")
async def add_knowledge(data: dict):
    """
    Manually add knowledge to the graph.

    Args:
        data: Knowledge data to add

    Returns:
        Success status
    """
    try:
        # TODO: Implement knowledge addition
        logger.info(f"Adding knowledge: {data}")

        return {
            "success": True,
            "message": "Knowledge addition à implémenter"
        }

    except Exception as e:
        logger.error(f"Error adding knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info",
    )
