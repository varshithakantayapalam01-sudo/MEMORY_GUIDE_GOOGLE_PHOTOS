import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app.services import session_manager, library_service, upload_service, image_understanding_service, embedding_service
from app.routes.sessions import helper_rescore_and_partition, query_initial_description
from app.models.api import QueryRequest
from app.models.library import LibraryImage

# Create research session
session = session_manager.create_session(mode="research")
session_id = session.session_id
print("Created session:", session_id)

# Register dummy image
dummy_img = LibraryImage(
    image_id=f"res_img_{session_id[-6:]}_0001",
    session_id=session_id,
    source="research",
    stored_filename="test.jpg",
    file_path=os.path.abspath("test.jpg"),
    image_url=f"/api/v1/sessions/{session_id}/images/res_img_0001",
    content_type="image/jpeg",
    file_size=100
)
library_service.register_research_images(session_id, [dummy_img])
image_understanding_service.index_research_library(session_id)
embedding_service.index_research_embeddings(session_id)

# Execute rescore
try:
    active, reserve = helper_rescore_and_partition(session_id)
    print("Rescore success. Active:", len(active), "Reserve:", len(reserve))
except Exception as e:
    import traceback
    print("RESCORE EXCEPTION:")
    traceback.print_exc()

# Execute query request
import asyncio
try:
    payload = QueryRequest(query="cake")
    res = asyncio.run(query_initial_description(session_id, payload))
    print("Query success:", res)
except Exception as e:
    import traceback
    print("QUERY EXCEPTION:")
    traceback.print_exc()
