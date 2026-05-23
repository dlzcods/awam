import os
import sys
from src import ingestion, rag_engine, config

def main():
    print("=== Legal RAG System (Double-Hop) ===")
    
    if not config.GOOGLE_API_KEY:
        print("ERROR: GOOGLE_API_KEY not found.")
        print("Please create a .env file with GOOGLE_API_KEY=your_key_here")
        return

    force_reindex = "--reindex" in sys.argv
    if force_reindex or not os.path.exists(config.INDEX_PATH):
        print("Building index from data folder...")
        try:
            ingestion.build_index()
        except Exception as e:
            print(f"Error building index: {e}")
            return
            
    print("Initializing RAG Engine...")
    try:
        engine = rag_engine.RAGEngine()
    except Exception as e:
        print(f"Failed to initialize engine: {e}")
        return
        
    print("\nSystem Ready! Type 'exit' or 'quit' to stop.")
    
    while True:
        try:
            user_query = input("\nYour Question: ")
            if user_query.lower() in ["exit", "quit"]:
                break
                
            if not user_query.strip():
                continue
                
            results = engine.process_query(user_query)
            
            print("\n=== FINAL ANSWER ===")
            print(results["answer"])
            print(f"\n[Duration: {results['execution_time']}s]")
            print("====================")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
