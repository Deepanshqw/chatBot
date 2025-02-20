from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import openai
import gradio as gr
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask app
app = Flask(__name__)
CORS(app) 
limiter = Limiter(app, key_func=get_remote_address)


def get_chat_response(user_query):
    """
    Generates a chatbot response using OpenAI GPT-4.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a knowledgeable FinTech assistant."},
                {"role": "user", "content": user_query}
            ]
        )
        return response["choices"][0]["message"]["content"].strip()
    
    except Exception as e:
        return f"Error: {str(e)}"


@app.route("/chat", methods=["POST"])
@limiter.limit("5 per minute")
def chat():
    """
    API endpoint to receive user queries and return chatbot responses.
    """
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    response = get_chat_response(user_message)
    return jsonify({"response": response})


# Gradio interface
def chat_interface(message):
    return get_chat_response(message)


if __name__ == "__main__":
    import threading

    def launch_gradio():
        iface = gr.ChatInterface(fn=chat_interface, title="WeCredit Chatbot")
        iface.launch(share=True)

    threading.Thread(target=launch_gradio).start()

    app.run(debug=True, port=5000)
