from services.confluence_service import ConfluenceServiceVertex
from app.config import settings 

# Initialize the service with your deployed Matching Engine IDs
confluence = ConfluenceServiceVertex(
    index_endpoint_id=settings.INDEX_ENDPOINT_ID,
    deployed_index_id=settings.DEPLOYED_INDEX_ID
)

# Fetch pages from Confluence
pages = confluence.fetch_pages("KB")
print(f"Fetched {len(pages)} pages from Confluence.")

# Upsert into Matching Engine
confluence.upsert_pages(pages)
print("All pages upserted into Matching Engine.")