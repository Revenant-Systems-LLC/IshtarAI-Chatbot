import json
import os
from flask import Flask, request, jsonify
import redis
import google.generativeai as genai

# --- Configuration ---
CHARACTER_DATA_FILE = "CharacterData.json"
MASTER_PROMPT_FILE = "ishtar_master_prompt.txt"
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
API_KEY = os.environ.get("GOOGLE_API_KEY")
HISTORY_LENGTH = 8

if not API_KEY:
    print("FATAL: GOOGLE_API_KEY environment variable not set.")
    exit(1)

genai.configure(api_key=API_KEY)
app = Flask(__name__)

# --- Safety Filter Override ---
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# --- Helper Components ---
class GeminiClient:
    def __init__(self):
        # --- MODEL CORRECTED TO GEMINI-2.0-FLASH ---
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    def generate(self, prompt: str) -> tuple[str | None, str | None]:
        try:
            print("\n" + "="*80)
            print("FINAL PROMPT SENT TO MODEL:")
            print(prompt)
            print("="*80 + "\n")
            response = self.model.generate_content(
                prompt,
                safety_settings=safety_settings,
                request_options={"timeout": 60}
            )
            if not response.parts:
                error_message = f"Model response was empty or blocked for other reasons: {response.prompt_feedback}"
                return None, error_message
            return response.text, None
        except Exception as e:
            return None, f"Model API call failed with exception: {str(e)}"

def load_data(file_path: str, is_json: bool = False):
    """Loads data from a file, either as JSON or plain text."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f) if is_json else f.read()
    except Exception as e:
        print(f"FATAL: Error loading {file_path}.")
        raise e

# --- Global Component Initialization ---
try:
    print("Initializing Ishtar (Uncensored Core - Final) components...")
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    redis_client.ping()
    llm_client = GeminiClient()
    character_data = load_data(CHARACTER_DATA_FILE, is_json=True)
    master_prompt_template = load_data(MASTER_PROMPT_FILE)
    print("All components initialized successfully.")
except Exception as e:
    print(f"\nFATAL ERROR DURING STARTUP: {e}\n")
    exit(1)


# --- API Endpoint ---
@app.route('/chat', methods=['POST'])
def handle_chat():
    try:
        request_data = request.json
        user_input, persona_id, session_id = (request_data.get(k) for k in ['user_input', 'persona_id', 'session_id'])
        if not all([user_input, persona_id, session_id]):
            return jsonify({"error": "Missing 'user_input', 'persona_id', or 'session_id'"}), 400

        character_info = next((char for char in character_data["characters"] if char["id"] == persona_id), None)
        if not character_info:
            return jsonify({"error": f"Persona with id '{persona_id}' not found."}), 404
        
        convo_state_raw = redis_client.get(session_id) or "{}"
        convo_state = json.loads(convo_state_raw)
        
        history = convo_state.get("history", [])
        history.append(f"User's Turn: {user_input}")
        if len(history) > HISTORY_LENGTH:
            history = history[-HISTORY_LENGTH:]
        
        history_str = "\n".join(history)

        # Final Prompt Assembly
        final_prompt = master_prompt_template
        final_prompt += "\n\n# --- CURRENT PERSONA MASK ---"
        final_prompt += f"\nYou are currently wearing the mask of '{character_info.get('display_name')}'. Portray this character with flawless accuracy, guided by the core Ishtar principles."
        final_prompt += f"\n- Character Name: {character_info.get('display_name')}"
        final_prompt += f"\n- Core Personality: {', '.join(character_info.get('personality_traits', []))}"
        final_prompt += "\n\n# --- ONGOING SCENE ---"
        final_prompt += f"\nThis is the dialogue so far. Continue the scene from this point."
        final_prompt += f"\n{history_str}"
        final_prompt += f"\n\n# --- YOUR TURN ---"
        final_prompt += f"\nIt is now your turn to speak as {character_info.get('display_name')}. Your response must be pure narrative text. Do not write the User's part. State what your character desires and take initiative to advance the scene. Generate only your character's response."
        
        raw_response, error_message = llm_client.generate(final_prompt)
        
        if error_message:
            return jsonify({"error": f"LLM Error: {error_message}"}), 500
        
        # Validation for empty or whitespace-only responses
        if not raw_response or not raw_response.strip():
            print("ERROR: LLM returned an empty or whitespace-only response.")
            # We don't save the user's turn to history if the AI fails to respond.
            return jsonify({"error": "The AI failed to generate a response. Please try again."}), 500

        response_text = raw_response.strip()
        
        history.append(f"{character_info.get('display_name')}'s Turn: {response_text}")

        new_convo_state = {"history": history}
        redis_client.set(session_id, json.dumps(new_convo_state), ex=3600)
        
        return jsonify({
            "response_text": response_text,
            "persona_id": persona_id
        })

    except Exception as e:
        print(f"FATAL UNHANDLED EXCEPTION IN handle_chat: {e}")
        return jsonify({"error": f"An unexpected fatal server error occurred: {str(e)}"}), 500

# --- Server Execution ---
if __name__ == '__main__':
    print("Starting Ishtar AI (Uncensored Core - Final) Backend server...")
    app.run(host='0.0.0.0', port=5000)