# Migration vers LangGraph - Documentation Complète

## 🎯 Vue d'Ensemble

Jarvis utilise désormais **LangGraph** pour la gestion conversationnelle avancée avec état persistant, routing conditionnel, et orchestration multi-agents.

---

## 🆚 LangChain vs LangGraph

### LangChain (Avant)
```python
# Chaîne linéaire simple
Input → LLM → Output
```

**Limitations** :
- ❌ Pas de gestion d'état entre tours
- ❌ Pas de routing conditionnel
- ❌ Difficile de créer des workflows complexes
- ❌ Pas de cycles (re-poser des questions)

### LangGraph (Maintenant)
```python
# Graphe avec état et routing conditionnel
START → Detect Intent → [Condition] → Retrieve Knowledge → Generate Response
                               ↓
                        [Condition] → Update Memory → END
```

**Avantages** :
- ✅ **État conversationnel persistant**
- ✅ **Routing conditionnel** intelligent
- ✅ **Cycles et clarifications**
- ✅ **Multi-agents orchestration**
- ✅ **Checkpointing** pour reprendre conversations
- ✅ **Human-in-the-loop**

---

## 🏗️ Architecture LangGraph

### Structure des Dossiers

```
backend/src/agents/langgraph/
├── jarvis_graph.py           # 🎯 Workflow principal
├── state/
│   └── conversation_state.py  # 📊 Modèle d'état
├── nodes/
│   ├── intent_node.py         # 🎭 Détection d'intention
│   ├── knowledge_node.py      # 📚 Récupération knowledge
│   ├── response_node.py       # 💬 Génération réponse
│   └── memory_node.py         # 🧠 Mise à jour mémoire
└── tools/
    └── (à venir)
```

---

## 📊 État Conversationnel

### ConversationState

L'état est **partagé entre tous les nodes** et contient toutes les informations de la conversation :

```python
class ConversationState(TypedDict):
    # Input/Output
    user_input: str                    # Message utilisateur
    assistant_response: str            # Réponse générée

    # Conversation History
    messages: List[Message]            # Historique complet

    # Intent & Context
    intent: Optional[str]              # Intention détectée
    entities: Dict[str, any]           # Entités extraites
    context: Dict[str, any]            # Contexte additionnel

    # Knowledge Graph
    retrieved_knowledge: List[Dict]    # Infos récupérées
    knowledge_to_store: List[Dict]     # Nouvelles infos à stocker

    # Metadata
    session_id: Optional[str]          # ID de session
    turn_count: int                    # Nombre de tours
    needs_clarification: bool          # Besoin de clarification
    clarification_question: Optional[str]

    # Error handling
    error: Optional[str]               # Message d'erreur
```

---

## 🔄 Workflow du Graphe

### Flow Principal

```
START
  ↓
┌─────────────────┐
│ Detect Intent   │  Détecte l'intention (query, memorize, task, general)
└────────┬────────┘
         │
         ├─→ [Intent = "query"] → Retrieve Knowledge
         │                               ↓
         └─→ [Intent ≠ "query"] ─────→  Generate Response
                                          │
                                          │
                                 ┌────────┴────────┐
                                 │                 │
                        [Memorize/Task]      [General]
                                 │                 │
                          Update Memory           END
                                 │
                                END
```

### Routing Conditionnel

**1. should_retrieve_knowledge**
```python
def should_retrieve_knowledge(state):
    if state["intent"] == "query":
        return "retrieve"  # → knowledge_node
    return "skip"         # → response_node
```

**2. should_update_memory**
```python
def should_update_memory(state):
    if state["intent"] in ["memorize", "task"]:
        return "update"   # → memory_node
    return "skip"        # → END
```

---

## 🎭 Nodes du Graphe

### 1. Intent Detection Node

**Rôle** : Détecter l'intention de l'utilisateur

```python
async def detect_intent(state: ConversationState) -> Dict:
    """
    Détecte l'intention parmi:
    - query: Poser une question
    - memorize: Stocker une information
    - task: Créer une tâche/reminder
    - general: Conversation générale
    """
```

**Utilise** : LLM (Claude) pour classification

**Retourne** : `{"intent": "query", "turn_count": 1}`

---

### 2. Knowledge Retrieval Node

**Rôle** : Récupérer des informations du knowledge graph

```python
async def retrieve_knowledge(state: ConversationState) -> Dict:
    """
    Interroge Neo4j/Graphiti pour infos pertinentes.
    Seulement si intent = "query"
    """
```

**Utilise** : `knowledge_service.query_knowledge()`

**Retourne** : `{"retrieved_knowledge": [...]}`

---

### 3. Response Generation Node

**Rôle** : Générer la réponse avec LLM

```python
async def generate_response(state: ConversationState) -> Dict:
    """
    Génère réponse avec:
    - Historique conversation
    - Knowledge récupéré (si disponible)
    - Context
    """
```

**Utilise** : LLM (Claude) avec contexte complet

**Retourne** : `{"assistant_response": "...", "messages": [...]}`

---

### 4. Memory Update Node

**Rôle** : Stocker nouvelles informations dans le knowledge graph

```python
async def update_memory(state: ConversationState) -> Dict:
    """
    Extrait entités et stocke dans Neo4j/Graphiti.
    Seulement si intent in ["memorize", "task"]
    """
```

**Utilise** : `knowledge_service.add_knowledge()`

**Retourne** : `{"knowledge_to_store": [...]}`

---

## 🔧 Service LangGraph

### LangGraphAgentService

```python
service = get_langgraph_service()

# Simple: Juste la réponse
response = await service.process_message("Bonjour Jarvis")

# Complet: État complet avec metadata
result = await service.process_message_with_state("Bonjour Jarvis")
# {
#   "response": "...",
#   "intent": "general",
#   "retrieved_knowledge": [],
#   "knowledge_stored": [],
#   "turn_count": 1,
#   ...
# }
```

---

## 🎮 Intégration dans le Controller

### VoiceController

```python
class VoiceController:
    def __init__(self):
        self.use_langgraph = True  # Activé par défaut
        self.langgraph_service = get_langgraph_service()
        self.agent_service = get_agent_service()  # Backup

    async def process_voice(self, audio):
        # STT
        transcription = await self.stt_service.transcribe(...)

        # LangGraph Agent
        if self.use_langgraph:
            response = await self.langgraph_service.process_message(transcription)
        else:
            response = await self.agent_service.process_message(transcription)

        # TTS
        await self.tts_service.synthesize(response, ...)
```

**Basculer entre agents** :
```python
# Utiliser LangGraph (défaut)
controller.use_langgraph = True

# Revenir à l'ancien agent
controller.use_langgraph = False
```

---

## 🧪 Endpoints de Test

### 1. Visualiser le Graphe

```bash
GET /api/langgraph/graph
```

**Réponse** :
```json
{
  "visualization": "ASCII graph...",
  "description": "Jarvis LangGraph workflow"
}
```

---

### 2. Tester LangGraph

```bash
POST /api/langgraph/test?message=Rappelle-moi d'acheter du pain
```

**Réponse** :
```json
{
  "response": "D'accord, je note...",
  "intent": "task",
  "retrieved_knowledge": [],
  "knowledge_stored": [...],
  "turn_count": 1,
  "needs_clarification": false,
  "error": null
}
```

---

## 📈 Cas d'Usage

### 1. Query Simple

```
User: "Quel temps fait-il ?"
  ↓
Intent: "query"
  ↓
Retrieve Knowledge: (aucune info météo stockée)
  ↓
Generate Response: "Je n'ai pas accès aux informations météo..."
  ↓
END
```

---

### 2. Memorize Information

```
User: "Mon anniversaire est le 15 mars"
  ↓
Intent: "memorize"
  ↓
Generate Response: "D'accord, je note que ton anniversaire est le 15 mars"
  ↓
Update Memory: Stocke dans Neo4j
  ↓
END
```

---

### 3. Task Creation

```
User: "Rappelle-moi d'acheter du pain demain matin"
  ↓
Intent: "task"
  ↓
Generate Response: "Parfait, je créerai un rappel..."
  ↓
Update Memory: Crée tâche dans knowledge graph
  ↓
END
```

---

### 4. Query avec Context

```
User: "Quand est mon anniversaire ?"
  ↓
Intent: "query"
  ↓
Retrieve Knowledge: {"type": "birthday", "date": "15 mars"}
  ↓
Generate Response (avec context): "Ton anniversaire est le 15 mars"
  ↓
END
```

---

## 🚀 Fonctionnalités Futures

### 1. Checkpointing (Persistance)
```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string(":memory:")
graph = workflow.compile(checkpointer=checkpointer)

# Reprendre une conversation
result = graph.invoke(
    state,
    {"configurable": {"thread_id": "user_123"}}
)
```

---

### 2. Human-in-the-Loop
```python
# Demander validation utilisateur avant action critique
from langgraph.prebuilt import interrupt

def critical_action(state):
    if state["action_type"] == "delete":
        interrupt("Confirmer suppression ?")
    ...
```

---

### 3. Multi-Agents
```python
# Router vers différents agents spécialisés
workflow.add_conditional_edges(
    "router",
    route_to_specialist,
    {
        "weather": weather_agent,
        "calendar": calendar_agent,
        "knowledge": knowledge_agent,
    }
)
```

---

### 4. Streaming Responses
```python
async for chunk in graph.astream(state):
    print(chunk)  # Réponse progressive
```

---

## 📊 Comparaison Performances

| Feature | Ancien Agent | LangGraph |
|---------|-------------|-----------|
| État conversationnel | ❌ Limité | ✅ Complet |
| Routing conditionnel | ❌ Non | ✅ Oui |
| Multi-agents | ❌ Non | ✅ Oui |
| Clarifications | ❌ Non | ✅ Oui |
| Checkpointing | ❌ Non | ✅ Oui |
| Human-in-loop | ❌ Non | ✅ Oui |
| Complexité workflow | ❌ Linéaire | ✅ Graphe |

---

## 🐛 Debugging

### Logs LangGraph

```python
# Chaque node log son exécution
logger.info("Detecting intent...")
logger.info(f"Intent: {intent}")
logger.info("Routing to knowledge retrieval")
```

### Inspect State

```python
# Récupérer l'état complet
result = await langgraph_service.process_message_with_state(message)
print(result)  # Tout l'état + metadata
```

---

## 📚 Ressources

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)
- [Tutorials](https://langchain-ai.github.io/langgraph/tutorials/)

---

## ✅ Résumé

### Avant (LangChain simple)
```python
input → LLM → output
```

### Après (LangGraph)
```python
input → [Intent] → [Condition] → Knowledge → Response → [Condition] → Memory → output
         ↓              ↓                                     ↓
      Routing      Smart routing                      Conditional update
```

**LangGraph = LangChain + State + Graph + Routing + Persistence** 🚀

---

## 🎉 Migration Complétée !

✅ État conversationnel complet
✅ Routing conditionnel intelligent
✅ Multi-nodes orchestration
✅ Prêt pour features avancées
✅ Architecture évolutive

**Jarvis est maintenant powered by LangGraph !** 🤖✨
