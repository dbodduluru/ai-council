from flask import Flask, request, jsonify, render_template
import ollama
from http import HTTPStatus
import json
import logging
import re

app = Flask(__name__)
history = []
actions = []

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load mock messages
with open('mock_messages.txt', 'r') as f:
    MOCK_MESSAGES = f.read()

def clean_json(text):
    """Extract valid JSON list from text, ignoring non-JSON prefixes/suffixes."""
    # Find the first valid JSON list block
    match = re.search(r'\[\s*(".*?"\s*,?\s*)*\]', text, re.DOTALL)
    if match:
        return match.group(0)
    logger.warning(f"No valid JSON list found in: {text}")
    return '[]'  # Fallback to empty list

def agent_extract(messages):
    """Agent 1: Extract raw actions from messages."""
    prompt = f"{messages}\n\nExtract action items as a JSON list (e.g., ['Call John at 9 AM', 'Send report']). Output **ONLY a valid JSON list**—no reasoning, no extra text, no tags like <think>. If no actions, return []."
    try:
        response = ollama.chat(model="deepseek-r1:7b", messages=[{"role": "user", "content": prompt}])
        raw_output = response['message']['content'].strip()
        logger.debug(f"Extractor raw response: {raw_output}")
        cleaned_json = clean_json(raw_output)
        actions = json.loads(cleaned_json)
        return actions if actions else []  # Ensure non-empty or []
    except Exception as e:
        logger.error(f"Extractor failed: {e}, raw output: {raw_output}")
        return []

def agent_validate(actions):
    """Agent 2: Validate actions for feasibility."""
    prompt = f"Actions: {json.dumps(actions)}\n\nValidate feasibility (e.g., time conflicts, clarity). Output **ONLY a valid JSON list**—no extra text. If no changes, return input list."
    try:
        response = ollama.chat(model="deepseek-r1:7b", messages=[{"role": "user", "content": prompt}])
        raw_output = response['message']['content'].strip()
        logger.debug(f"Validator raw response: {raw_output}")
        cleaned_json = clean_json(raw_output)
        return json.loads(cleaned_json)
    except Exception as e:
        logger.error(f"Validator failed: {e}, raw output: {raw_output}")
        return actions

def agent_decide(actions):
    """Agent 3: Finalize concise actions."""
    prompt = f"Actions: {json.dumps(actions)}\n\nDecide final actions concisely. Output **ONLY a valid JSON list**—no extra text. If no changes, return input list."
    try:
        response = ollama.chat(model="deepseek-r1:7b", messages=[{"role": "user", "content": prompt}])
        raw_output = response['message']['content'].strip()
        logger.debug(f"Decider raw response: {raw_output}")
        cleaned_json = clean_json(raw_output)
        return json.loads(cleaned_json)
    except Exception as e:
        logger.error(f"Decider failed: {e}, raw output: {raw_output}")
        return actions

@app.route('/')
def index():
    """Serve the UI."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Process user input through AI council."""
    try:
        user_input = request.json.get('message', '').strip()
        if not user_input:
            return jsonify({"error": "No message provided"}), HTTPStatus.BAD_REQUEST

        logger.info(f"Received input: {user_input}")
        history.append({"role": "user", "content": user_input})
        extracted = agent_extract(MOCK_MESSAGES)
        logger.info(f"Extracted actions: {extracted}")
        validated = agent_validate(extracted)
        logger.info(f"Validated actions: {validated}")
        final = agent_decide(validated)
        logger.info(f"Final actions: {final}")
        actions.extend(final)
        response = "Actions set: " + ", ".join(final) if final else "No actions found."
        return jsonify({"response": response, "actions": final})
    except Exception as e:
        logger.error(f"Error in /chat: {str(e)}", exc_info=True)
        return jsonify({"error": "Something went wrong"}), HTTPStatus.INTERNAL_SERVER_ERROR

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)