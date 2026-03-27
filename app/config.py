import os
from dotenv import load_dotenv
from google.cloud import secretmanager

load_dotenv()

class Settings:
    PROJECT_ID = os.getenv("PROJECT_ID")
    PROJECT_NUMBER = os.getenv("PROJECT_NUMBER")
    REGION = os.getenv("REGION")

    SERVICENOW_INSTANCE = os.getenv("SERVICENOW_INSTANCE")
    SERVICENOW_USER = os.getenv("SERVICENOW_USER")
    SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD")

    CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
    CONFLUENCE_USER = os.getenv("CONFLUENCE_USER")
    CONFLUENCE_TOKEN = os.getenv("CONFLUENCE_TOKEN")

    INDEX_ENDPOINT_ID = os.getenv("INDEX_ENDPOINT_ID")
    DEPLOYED_INDEX_ID=os.getenv("DEPLOYED_INDEX_ID")

    EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
    EMAIL_SMTP_PORT=os.getenv("EMAIL_SMTP_PORT")

    def get_secret(self, secret_id, project_id):
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")

settings = Settings()