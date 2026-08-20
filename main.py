from memory import init_chat_db, init_vector_db, add_to_knowledge_base
from mac_tools import get_ai_folder_notes, get_apple_calendar_events
from llm_router import query_desktop_gpu

if __name__ == "__main__":
    print("Initializing Modular Mac Agent...\n")

    chat_db = init_chat_db()
    vector_collection = init_vector_db()

    # --- AUTOMATED RAG INGESTION PIPELINE ---
    ai_notes = get_ai_folder_notes(folder_name="AI Notes")

    print(f"--> Syncing {len(ai_notes)} notes from 'AI Notes' to vector memory...")
    for i, note in enumerate(ai_notes):
        add_to_knowledge_base(
            vector_collection,
            document_text=note["content"],
            doc_id=f"ai_note_{i}",
            source_name=note["title"]
        )

    # --- CALENDAR INGESTION ---
    calendar_text = get_apple_calendar_events(calendar_name="7shifts")

    if calendar_text and not calendar_text.startswith("Error"):
        add_to_knowledge_base(
            vector_collection,
            document_text=calendar_text,
            doc_id="apple_calendar_7shifts",
            source_name="Apple Calendar"
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