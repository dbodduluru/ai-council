# AI Council

A multi-agent AI system that reviews messages and decides on actions—voice-enabled!

## Features
- Three agents (Extractor, Validator, Decider) process mock Outlook/Teams messages.
- Extracts and refines actions (e.g., “Prep slides for 3 PM, send report by 5 PM”).
- Voice input/output via Web Speech API.

## Tech Stack
- **LLM**: DeepSeek-R1 (7B) via Ollama
- **Backend**: Flask (Python)
- **Frontend**: HTML/JavaScript
- **Container**: Docker

## Setup
1. **Clone**:
   ```bash
   git clone https://github.com/dbodduluru/ai-council.git
   cd ai-council