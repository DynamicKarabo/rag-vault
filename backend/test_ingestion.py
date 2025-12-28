from app.services.ingestion import IngestionService
import os

def test_ingestion():
    service = IngestionService()
    
    # Create dummy file
    test_file = "test_doc.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("A" * 600) # Should split into 2 chunks (512 + remainder)
        
    try:
        results = service.ingest(test_file, "doc-123")
        print(f"Chunks generated: {len(results)}")
        for i, chunk in enumerate(results):
            print(f"Chunk {i+1} length: {len(chunk['text'])}")
            print(f"Metadata: {chunk['metadata']}")
            
        assert len(results) >= 2
        print("TEST PASSED")
    except Exception as e:
        print(f"TEST FAILED: {e}")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    test_ingestion()
