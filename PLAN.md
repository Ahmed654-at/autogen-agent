# Plan: First AI Agent with Microsoft AutoGen + Ollama

Goal: build a working AutoGen agent inside the `Claude Code` folder, running on an open-source model through Ollama, with the project ready to switch to OpenAI, OpenRouter or Azure later by changing `.env` only.

---

## Important corrections before we start

1. **Model size.** A 600B+ parameter model cannot run on a normal PC. It needs roughly 400 GB+ of RAM/VRAM. Big models running locally are also *slower*, not faster. Two realistic options:
   - **Local model (fully offline, free):** 4B–32B, chosen by your hardware (table in Phase 3).
   - **Ollama Cloud model (600B-class "brain"):** runs on Ollama's servers but uses the same local Ollama commands and the same AutoGen code. Free plan = light usage, one model at a time. Some of the largest models need a paid plan.
2. **Where classes live.** `AssistantAgent` is in `autogen_agentchat.agents`. Model clients are in `autogen_ext.models.*` (ollama / openai / azure).
3. **OpenRouter has no separate extension.** It uses the OpenAI client with `base_url="https://openrouter.ai/api/v1"`.

---

## Phase 0 — Prerequisite checks

| Check | Command (Windows) | Command (Mac/Linux) |
|---|---|---|
| Python 3.12+ | `py -3.12 --version` | `python3.12 --version` |
| Ollama installed | `ollama --version` | `ollama --version` |
| RAM | `systeminfo \| findstr "Total Physical Memory"` | `free -h` / About This Mac |
| NVIDIA GPU (optional) | `nvidia-smi` | `nvidia-smi` |

- If Python 3.12 is missing: install from https://www.python.org/downloads/
- If Ollama is missing: install from https://ollama.com/download

**Done when:** Python ≥ 3.12 and Ollama both print a version, and RAM/GPU is known.

---

## Phase 1 — Project structure

```
Claude Code/
├── .env                  # real keys and settings (never committed)
├── .env.example          # same keys, empty values (committed)
├── .gitignore
├── README.md
├── PLAN.md
├── requirements.txt
├── main.py               # entry point: python main.py
├── config/
│   ├── __init__.py
│   └── settings.py       # loads .env with python-dotenv
├── models/
│   ├── __init__.py
│   └── model_client.py   # Step 1: model client factory (ollama/openai/openrouter/azure)
├── agents/
│   ├── __init__.py
│   └── assistant.py      # Step 2: AssistantAgent builder
├── tools/
│   ├── __init__.py
│   └── basic_tools.py    # Python functions the agent can call
├── workflows/
│   ├── __init__.py
│   └── single_agent.py   # runs one agent on a task (multi-agent teams later)
├── prompts/
│   └── assistant_system.md
├── tests/
│   └── test_smoke.py
├── logs/
└── .venv/                # virtual environment (ignored by git)
```

**`.gitignore`** must include: `.venv/`, `.env`, `__pycache__/`, `*.pyc`, `logs/`, `.vscode/`, `.DS_Store`

**`.env.example`:**
```
MODEL_PROVIDER=ollama          # ollama | openai | openrouter | azure

OLLAMA_MODEL=qwen3:8b
OLLAMA_HOST=http://localhost:11434

OPENAI_API_KEY=
OPENAI_MODEL=

OPENROUTER_API_KEY=
OPENROUTER_MODEL=

AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT=
AZURE_OPENAI_API_VERSION=
```

**Done when:** all folders and files exist and `.env` is copied from `.env.example`.

---

## Phase 2 — Virtual environment + dependencies

**`requirements.txt`:**
```
autogen-agentchat
autogen-ext[openai,ollama,azure]
python-dotenv
pytest
```

Commands:
```
# Windows
py -3.12 -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3.12 -m venv .venv
source .venv/bin/activate

# Both
python -m pip install --upgrade pip
pip install -r requirements.txt
pip show autogen-agentchat autogen-ext
```

In VS Code: Ctrl+Shift+P → "Python: Select Interpreter" → choose `.venv`.

**Done when:** `python --version` inside the venv shows 3.12+, and `pip show` lists both AutoGen packages.

---

## Phase 3 — Choose and download the model ("brain")

| Your hardware | Model | Command |
|---|---|---|
| 8 GB RAM, no GPU | `qwen3:4b` or `llama3.2:3b` | `ollama pull qwen3:4b` |
| 16 GB RAM or 6–8 GB GPU | `qwen3:8b` (recommended start) | `ollama pull qwen3:8b` |
| 32 GB RAM or 12–16 GB GPU | `qwen3:14b` or `gpt-oss:20b` | `ollama pull qwen3:14b` |
| 64 GB RAM or 24 GB GPU | `qwen3:32b` | `ollama pull qwen3:32b` |
| Any PC, big "brain" via cloud | `gpt-oss:120b-cloud` (free plan) | `ollama signin` then `ollama pull gpt-oss:120b-cloud` |

- The model must support **tool calling** for agents. All models above do.
- Check https://ollama.com/search (local) and https://ollama.com/search?c=cloud (cloud) for newer versions before pulling. Cloud models in the 600B+ range may require a paid Ollama plan.
- Test the model alone first: `ollama run qwen3:8b "Say hello"`

**Done when:** `ollama list` shows the model and `ollama run` replies.

---

## Phase 4 — Step 1: Configure the model client (`models/model_client.py`)

One function, `get_model_client()`, reads `MODEL_PROVIDER` from `.env` and returns:

- **ollama:** `OllamaChatCompletionClient(model=..., host=..., model_info={vision: False, function_calling: True, json_output: True, structured_output: True, family: "unknown"})`
- **openai:** `OpenAIChatCompletionClient(model=..., api_key=...)`
- **openrouter:** `OpenAIChatCompletionClient(model=..., api_key=..., base_url="https://openrouter.ai/api/v1", model_info={...})`
- **azure:** `AzureOpenAIChatCompletionClient(azure_deployment=..., model=..., api_version=..., azure_endpoint=..., api_key=...)`

Imports: `autogen_ext.models.ollama`, `autogen_ext.models.openai`. (The Azure OpenAI client is also in `autogen_ext.models.openai`.)

**Done when:** a small test prints a reply from `client.create(...)` with Ollama.

---

## Phase 5 — Step 2: Build the AssistantAgent (`agents/assistant.py`)

- `AssistantAgent(name="assistant", model_client=..., tools=[...], system_message=<from prompts/assistant_system.md>, reflect_on_tool_use=True)`
- Tools in `tools/basic_tools.py` (start with 2 simple ones):
  - `get_current_time()` — returns the current date/time
  - `calculator(expression: str)` — safe math evaluation
- Each tool needs type hints and a docstring (AutoGen uses them to describe the tool to the model).

**Done when:** the agent object builds without errors.

---

## Phase 6 — Run it (`workflows/single_agent.py` + `main.py`)

- `single_agent.py`: `async def run(task)` → `await Console(agent.run_stream(task=task))` → `await model_client.close()`
- `main.py`: asks for a task in the terminal (or uses a default) and calls `asyncio.run(run(task))`
- Run: `python main.py`

**Done when:** the agent answers a question that requires a tool (e.g. "What is 2345 × 67 and what time is it?") and the console shows the tool call and the final answer.

---

## Phase 7 — Testing checklist (you)

- [ ] Plain question with no tools → sensible answer
- [ ] Question needing the calculator → tool is called, answer is correct
- [ ] Question needing both tools → both are called
- [ ] Ollama stopped → clear error message, no crash with a confusing trace
- [ ] Switch `OLLAMA_MODEL` to a different model in `.env` → still works without code changes
- [ ] (Optional) `MODEL_PROVIDER=openrouter` with a free OpenRouter model → still works
- [ ] `pytest tests/` passes

---

## Phase 8 — Git

```
git init
git add .
git commit -m "First AutoGen agent with Ollama"
```

Check that `.env` and `.venv/` are **not** in the commit (`git status`).

---

## Next steps after this session

- Add a second agent and run them as a team (`RoundRobinGroupChat`)
- Add real tools: web search, file reading, Supabase, n8n webhook calls
- Add memory/state saving between runs
