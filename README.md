# First AutoGen Agent

A single Microsoft AutoGen (v0.7) `AssistantAgent` with two tools, `calculator` and `get_current_time`. The model provider is picked in `.env`, so you can switch providers without changing any code.

## Setup (once)

```
py -3.14 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
```

Then fill in `.env`. Set `MODEL_PROVIDER` to `ollama`, `openai`, `openrouter` or `azure`, and fill the settings for that provider. Never commit `.env`.

## Run

```
.venv\Scripts\activate
python main.py
```

This starts a chat. The agent remembers earlier questions and answers in the same session. Type `exit` or `quit` to stop.

With OpenRouter, `OPENROUTER_FALLBACK_MODEL` (default `openrouter/free`) answers when `OPENROUTER_MODEL` is overloaded. Leave it empty to use only your chosen model.

## Test

```
python -m pytest tests/
```

The tests run offline. They don't call a model and need no API key.

## Layout

| Path | Purpose |
|---|---|
| `config/settings.py` | Loads `.env` |
| `models/model_client.py` | `get_model_client()`: provider factory |
| `agents/assistant.py` | `build_assistant()`: the AssistantAgent |
| `tools/basic_tools.py` | Tools the agent can call |
| `workflows/single_agent.py` | `run(task)`: streams one agent run to the console |
| `prompts/assistant_system.md` | System prompt |
| `main.py` | Entry point |
