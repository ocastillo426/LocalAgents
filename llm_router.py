import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from memory import get_chat_history, search_knowledge_base, log_message

load_dotenv()
WINDOWS_GPU_IP = os.getenv("WINDOWS_GPU_IP")
MODEL_NAME = "llama3.1"


def query_desktop_gpu(prompt, chat_conn, vector_collection):
    """Routes chat history and vector database context to the Windows GPU."""
    url = f"{WINDOWS_GPU_IP}/api/chat"

    messages = get_chat_history(chat_conn, limit=10)
    relevant_context = search_knowledge_base(vector_collection, prompt, n_results=2)

    # --- DATE MATH INJECTION ---
    now = datetime.now()
    tomorrow = now + timedelta(days=1)

    today_str = now.strftime("%A, %B %d, %Y")
    tomorrow_str = tomorrow.strftime("%A, %B %d, %Y")

    system_instruction = (
        f"Today is {today_str}. Tomorrow is {tomorrow_str}.\n"
        "Strict Rule: Do not make up schedules or hallucinate times. "
        "Only use the provided context to answer.\n"
    )

    if relevant_context:
        system_instruction += f"\nRelevant retrieved knowledge base data:\n{relevant_context}"

    messages.insert(0, {
        "role": "system",
        "content": system_instruction
    })
    # ---------------------------

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