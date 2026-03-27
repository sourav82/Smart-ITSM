import requests
from google.cloud import aiplatform
from vertexai.preview.language_models import TextEmbeddingModel
from app.config import settings
import json

class ConfluenceServiceVertex:
    def __init__(self, project_id=settings.PROJECT_NUMBER, location=settings.REGION, index_endpoint_id=None, deployed_index_id=None):
        self.base_url = settings.get_secret("CONFLUENCE_URL", settings.PROJECT_ID)
        self.auth = (settings.get_secret("CONFLUENCE_USER", settings.PROJECT_ID), settings.get_secret("CONFLUENCE_TOKEN", settings.PROJECT_ID))

        self.project_id = project_id
        self.location = location
        self.index_id = index_endpoint_id  # Matching Engine Index ID (created separately in GCP)
        self.deployed_index_id = deployed_index_id

        # Initialize Vertex AI
        aiplatform.init(project=self.project_id, location=self.location)
        self.embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")

        if self.index_id and deployed_index_id:
            # Connect to deployed Matching Engine endpoint
            self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
                index_endpoint_name=f"projects/{self.project_id}/locations/{self.location}/indexEndpoints/{self.index_id}"
            )
            print(self.index_endpoint.public_endpoint_domain_name)
        else:
            self.index_endpoint = None

    # -----------------------------
    # 1️⃣ Fetch Confluence Pages
    # -----------------------------
    def fetch_pages(self, space_key="ITSM"):
        """
        Fetch all pages from a Confluence space.
        Returns a list of dicts: {title, content, url}
        """
        pages = []
        url = f"{self.base_url}/rest/api/content?spaceKey={space_key}&limit=100&expand=body.storage"
        start = 0
        while True:
            resp = requests.get(url + f"&start={start}", auth=self.auth)
            # Check response status
            if not resp.ok:
                raise Exception(f"Failed to fetch pages: {resp.status_code}, {resp.text}")
            
            data = resp.json()
            results = data.get("results", [])
            if not results:
                break
            for page in results:
                title = page["title"]
                print(f"Title: {title}")
                content = page["body"]["storage"]["value"]
                print(f"Content: {content}")
                page_url = f"{self.base_url}/pages/{page['id']}"
                print(f"Page URL: {page_url}")
                pages.append({"title": title, "content": content, "url": page_url})
            if "next" not in data.get("_links", {}):
                break
            start += len(results)
        return pages

    # -----------------------------
    # 2️⃣ Generate Embeddings
    # -----------------------------
    def embed_text(self, text: str):
        """
        Generate embedding vector for given text using Vertex AI Embeddings.
        """
        response = self.embedding_model.get_embeddings([text])
        return response[0].values

    # -----------------------------
    # 3️⃣ Prepare Matching Engine Index Data
    # -----------------------------
    def prepare_index_data(self, pages):
        """
        Returns a list of (embedding, metadata) ready for Matching Engine upload.
        """
        index_data = []
        for page in pages:
            embedding = self.embed_text(page["content"])
            metadata = {"title": page["title"], "url": page["url"]}
            index_data.append({"embedding": embedding, "metadata": metadata})
        return index_data

    def search_kb_1(self, query_embedding, top_k=3):
        """
        Search the deployed Vertex AI Matching Engine index for similar KB articles.
        
        Args:
            query_embedding (list[float]): The embedding vector of the query.
            top_k (int): Number of nearest neighbors to retrieve.

        Returns:
            List of matched datapoints.
        """
        from google.cloud import aiplatform_v1
        # Config: replace with your values or class attributes
        API_ENDPOINT = "1189106670.us-central1-678234794222.vdb.vertexai.goog"
        INDEX_ENDPOINT = "projects/678234794222/locations/us-central1/indexEndpoints/1463012370942001152"
        DEPLOYED_INDEX_ID = "kb_index_1774520133866"

        # Create the low-level MatchServiceClient
        client_options = {"api_endpoint": API_ENDPOINT}
        vector_search_client = aiplatform_v1.MatchServiceClient(client_options=client_options)
        query_embedding = self.embed_text(query_embedding)
        # Build the query datapoint
        datapoint = aiplatform_v1.IndexDatapoint(feature_vector=query_embedding)

        query = aiplatform_v1.FindNeighborsRequest.Query(
            datapoint=datapoint,
            neighbor_count=top_k
        )

        request = aiplatform_v1.FindNeighborsRequest(
            index_endpoint=INDEX_ENDPOINT,
            deployed_index_id=DEPLOYED_INDEX_ID,
            queries=[query],
            return_full_datapoint=True  # set True if you want the full metadata
        )

        try:
            response = vector_search_client.find_neighbors(request)
            results = []
            for neighbor_list in response.nearest_neighbors:
                 for neighbor in neighbor_list.neighbors:
                     if (neighbor.distance > 0.5):
                       title = neighbor.datapoint.datapoint_id if neighbor.datapoint.datapoint_id else None
                       print(f"{title}")
                       print(f"{neighbor.distance}")
                 results.append(f"{title}")

            return results

        except Exception as e:
            print(f"Error searching KB: {e}")
            return []

    # -----------------------------
    # 4️⃣ Search KB via Matching Engine
    # -----------------------------
    def search_kb(self, incident_description: str, top_k=3):
        """
        Search deployed Matching Engine for top-K relevant KB articles
        Returns list of strings: "Title: URL"
        """
        if not self.index_endpoint:
            raise Exception("Matching Engine endpoint not configured.")

        query_embedding = self.embed_text(incident_description)

        response = self.index_endpoint.match(
            deployed_index_id="kb_index_1774520133866",#self.deployed_index_id,
            queries=[query_embedding],
            num_neighbors=top_k
        )

        results = []
        for neighbor in response[0].neighbors:
            title = neighbor.metadata.get("title")
            url = neighbor.metadata.get("url")
            results.append(f"{title}: {url}")

        return results if results else None

    def upsert_pages(self, pages):
        """
        Convert Confluence pages to embeddings and upsert into Matching Engine.
        """
        if not self.index_endpoint:
            raise Exception("Matching Engine endpoint not configured.")

        datapoints = []
        for page in pages:
            if not page.get("content"):
                continue
            embedding = self.embed_text(page["content"])
            datapoints.append({
                "datapoint_id": page["title"],  # unique id per page
                "feature_vector": embedding
            })

        # Upsert into Index (not IndexEndpoint)
        index = aiplatform.MatchingEngineIndex(self.deployed_index_id)
        index.upsert_datapoints(datapoints)
        print(f"Upserted {len(datapoints)} pages into Vertex AI vector index")

    # **********************
    # Create a new KB article
    # ************************
    def create_page(self, space_key, title, content, parent_id=None):
        """
        Create a page in Confluence

        space_key : Confluence space key
        title     : Page title
        content   : HTML content
        parent_id : Optional parent page ID
        """

        url = f"{self.base_url}/wiki/rest/api/content"

        data = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }

        if parent_id:
            data["ancestors"] = [{"id": parent_id}]

        response = requests.post(
            url,
            headers=self.headers,
            auth=self.auth,
            data=json.dumps(data)
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create page: {response.text}")

        return response.json()