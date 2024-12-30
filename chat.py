import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import json
from datetime import datetime

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Initialize Flask app
app = Flask(__name__)

# Chat history file
CHAT_HISTORY_FILE = "chat_history.json"

# Configure the generative model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 120,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="You are a doctor who specializes in mental health and helps users with mental health issues.",
)

# Function to save chat history
def save_chat_history(user_message, bot_response):
    try:
        with open(CHAT_HISTORY_FILE, "r") as file:
            history = json.load(file)
    except FileNotFoundError:
        history = []

    history.append({
        "timestamp": str(datetime.now()),
        "user_message": user_message,
        "bot_response": bot_response
    })

    with open(CHAT_HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)

# Function to retrieve chat history
def get_chat_history():
    try:
        with open(CHAT_HISTORY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message")
    
    # Start chat session and get response
    chat_session = model.start_chat(
        history=[
            {"role": "user", "parts": ["hi"]},
            {"role": "model", "parts": ["Hi there. How can I help you today? It's okay if you're not sure where to start. Just let me know what's on your mind. I'm here to listen.\n"]},
            {"role": "user", "parts": ["I'm having a lot of stress."]},
            {"role": "model", "parts": ["I understand. Stress is something a lot of people experience, and it can be difficult to manage. Can you tell me more about what's causing your stress? Knowing more can help us find ways to manage it."]}
        ]
    )

    response = chat_session.send_message(user_input)

    # Save chat history
    save_chat_history(user_input, response.text)

    return jsonify({"response": response.text})

@app.route('/history', methods=['GET'])
def history():
    return jsonify(get_chat_history())

if __name__ == '__main__':
    app.run(debug=True)
