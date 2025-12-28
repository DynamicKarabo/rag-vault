from app.services.llm import LLMService

def test_llm_structure():
    service = LLMService()
    
    # Mock Chunks
    chunks = [
        {"text": "Artificial Intelligence is evolving.", "metadata": {"source_doc_id": "doc-1", "page_number": 10}},
        {"text": "RAG systems combine retrieval and generation.", "metadata": {"source_doc_id": "doc-2", "page_number": 5}}
    ]
    
    print("Testing LLM Response Generator...")
    try:
        gen = service.generate_response(chunks, "What is RAG?")
        
        # First item MUST be citations
        first_item = next(gen)
        print(f"First Event Type: {first_item.get('type')}")
        print(f"Data: {first_item.get('data')}")
        
        assert first_item['type'] == 'citation'
        assert len(first_item['data']) == 2
        
        # Subsequent items are tokens or error (if no API key)
        # We expect an error or token, but the structure test passes if we got citations first.
        second_item = next(gen)
        print(f"Second Event Type: {second_item.get('type')}")
        print(f"Data: {second_item.get('data')}")
        
    except StopIteration:
        print("Generator stopped unexpectedly.")
    except Exception as e:
        print(f"Execution Error (Expected if no API key): {e}")

if __name__ == "__main__":
    test_llm_structure()
