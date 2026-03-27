import vertexai
from app.config import settings

vertexai.init(
    project=settings.PROJECT_ID,
    location=settings.REGION
)