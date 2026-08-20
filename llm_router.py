import os
import requests
from dotenv import load_dotenv
from memory import get_chat_history, search_knowledge_base, log_message

# Load environment variables
load_dotenv()
WINDOWS_GPU_IP = os.getenv("WINDOWS_GPU_IP")
MODEL_NAME = "llama3.1"


def query_desktop_gpu(prompt, chat_conn, vector_collection):
    """Routes chat history and vector database context to the Windows GPU."""
    url = f"{WINDOWS_GPU_IP}/api/chat"

    messages = get_chat_history(chat_conn, limit=10)
    relevant_context = search_knowledge_base(vector_collection, prompt)

    if relevant_context:
        messages.insert(0, {
            "role": "system",
            "content": f"Use this retrieved context to answer the user: {relevant_context}"
        })

    messages.append({"role": "user", "content": prompt})
    log_message(chat_conn, "user", prompt)

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        assistant_reply = response.json().get("message", {}).get("content", "No response.")
        log_message(chat_conn, "assistant", assistant_reply)
        return assistant_reply

    except requests.exceptions.RequestException as e:
        return f"Connection Failed: {e}"