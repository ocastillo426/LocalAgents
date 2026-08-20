import sqlite3
import chromadb


# ==========================================
# 1. SQLITE: SHORT-TERM CHAT HISTORY
# ==========================================
def init_chat_db():
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            role TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    return conn


def log_message(conn, role, content):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))
    conn.commit()


def get_chat_history(conn, limit=10):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, content FROM (
            SELECT role, content, timestamp FROM messages 
            ORDER BY timestamp DESC LIMIT ?
        ) ORDER BY timestamp ASC
    ''', (limit,))

    messages = []
    for row in cursor.fetchall():
        messages.append({"role": row[0], "content": row[1]})
    return messages


# ==========================================
# 2. CHROMADB: LONG-TERM KNOWLEDGE (RAG)
# ==========================================
def init_vector_db():
    chroma_client = chromadb.PersistentClient(path="./chroma_data")
    collection = chroma_client.get_or_create_collection(name="personal_knowledge")
    return collection


def add_to_knowledge_base(collection, document_text, doc_id, source_name):
    collection.upsert(
        documents=[document_text],
        metadatas=[{"source": source_name}],
        ids=[doc_id]
    )
    print(f"[*] Saved '{source_name}' to long-term memory!")


def search_knowledge_base(collection, query_text, n_results=2):
    """Searches the vector database and joins top matches into a single context string."""
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    if results['documents'] and results['documents'][0]:
        # Join retrieved doc fragments cleanly
        return "\n---\n".join(doc for doc in results['documents'][0] if doc)
    return ""