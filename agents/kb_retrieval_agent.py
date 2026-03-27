from services.confluence_service import ConfluenceServiceVertex
from app.config import settings

# -----------------------------
# Initialize KB Agent (Singleton)
# -----------------------------
kb_agent = ConfluenceServiceVertex(
    project_id=settings.PROJECT_ID,
    location=settings.REGION,
    index_endpoint_id=settings.INDEX_ENDPOINT_ID,
    deployed_index_id=settings.DEPLOYED_INDEX_ID
)

# -----------------------------
# Public function to search KB
# -----------------------------
def search_kb(incident_description: str, top_k: int = 3):
    """
    Search Confluence KB for the given incident description using Vertex AI Matching Engine.
    Returns list of strings: ["Title: URL", ...]
    """

    try:
        kb_results = kb_agent.search_kb_1(incident_description, top_k=top_k)
        if not kb_results:
            print("No matching KB articles found.")
            return []
        return kb_results
    except Exception as e:
        print(f"Error searching KB: {e}")
        return []