from memory import init_chat_db, init_vector_db, add_to_knowledge_base
from mac_tools import get_all_note_names, get_apple_note
from llm_router import query_desktop_gpu

if __name__ == "__main__":
    print("Initializing Modular Mac Agent...\n")

    chat_db = init_chat_db()
    vector_collection = init_vector_db()

    # --- AUTOMATED RAG INGESTION PIPELINE ---
    all_titles = get_all_note_names()

    print(f"--> Found {len(all_titles)} notes. Syncing to vector memory...")
    for i, title in enumerate(all_titles):
        text = get_apple_note(title)
        if text and not text.startswith("Error"):
            add_to_knowledge_base(
                vector_collection,
                document_text=text,
                doc_id=f"note_{i}",
                source_name=title
            )
    print("--> Sync complete! Agent is ready.\n")
    # ----------------------------------------

    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Shutting down agent...")
            break

        answer = query_desktop_gpu(user_input, chat_db, vector_collection)
        print(f"\n[Llama 3.1]:\n{answer}\n")