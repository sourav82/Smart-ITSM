from vertexai.generative_models import GenerativeModel
from utils.vertex_client import *
import json

model = GenerativeModel("gemini-2.5-flash")

def create_kb(description: str, resolution: str):

    prompt = f"""
Create a knowledge base article.

Incident:
{description}

Resolution:
{resolution}

Format:

Title
Problem
Root Cause
Resolution
Steps

Please understand from the incident resolution description notes if new KB article is required.
If the engineer mention that no new KB articles required, then no need to create any KB articles.

Return ONLY JSON:

{{
"title": "...",
"content": "..."
}}

"""

    response = model.generate_content(prompt)

    result = json.loads(response.text)

    return result["title"], result["content"]