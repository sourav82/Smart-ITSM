from services.confluence_service import ConfluenceService

if __name__ == "__main__":
    confluence = ConfluenceService()
    pages = confluence.fetch_pages()
    confluence.ingest_pages_to_vectorstore(pages)
    print("Vectorstore created locally at vectorstore/faiss_index")