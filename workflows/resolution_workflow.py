from agents.kb_creator_agent import create_kb
from services.confluence_service import ConfluenceServiceVertex

async def process_resolution(payload):

    description = payload["description"]
    resolution = payload["resolution_notes"]

    title, content = create_kb(description, resolution)

    confluence = ConfluenceServiceVertex()

    confluence.create_page("KB", title, content)

    return {"status": "kb created"}