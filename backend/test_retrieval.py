from app.services.retrieval import RetrievalService
import shutil
import os

def test_retrieval():
    # Cleanup previous db for clean test
    if os.path.exists("./test_chroma_db"):
        shutil.rmtree("./test_chroma_db")
        
    service = RetrievalService(persist_dir="./test_chroma_db")
    
    # 1. Add Data
    print("Indexing documents...")
    texts = [
        "The secret ingredient to the soup is saffron.",
        "The capital of France is Paris.",
        "Python is a great programming language.",
        "RAG stands for Retrieval Augmented Generation."
    ]
    metadatas = [
        {"collection_id": "col-A", "source": "recipe.txt"},
        {"collection_id": "col-A", "source": "geo.txt"},
        {"collection_id": "col-B", "source": "coding.txt"}, # Different collection
        {"collection_id": "col-A", "source": "ai.txt"}
    ]
    ids = ["1", "2", "3", "4"]
    
    service.add_texts(texts, metadatas, ids)
    
    # 2. Search in Collection A
    print("\nSearching in Collection A for 'soup'...")
    results_a = service.search("col-A", "What is the secret ingredient?", top_k=2)
    for res in results_a:
        print(f" - Found: {res['text']} (Dist: {res['distance']})")
        assert res['metadata']['collection_id'] == "col-A"
    
    assert any("saffron" in r['text'] for r in results_a)
    assert not any("Python" in r['text'] for r in results_a) # Should filter out Col-B
    
    # 3. Search in Collection B
    print("\nSearching in Collection B for 'code'...")
    results_b = service.search("col-B", "programming", top_k=2)
    for res in results_b:
        print(f" - Found: {res['text']}")
        assert res['metadata']['collection_id'] == "col-B"
        
    assert any("Python" in r['text'] for r in results_b)
    
    print("\nTEST PASSED")

if __name__ == "__main__":
    test_retrieval()
