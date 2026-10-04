from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel


LibrarySource = Literal["demo", "research"]


class LibraryImage(BaseModel):
    image_id: str
    session_id: Optional[str] = None
    source: LibrarySource
    stored_filename: str
    file_path: str
    image_url: Optional[str] = None
    content_type: Optional[str] = None
    file_size: Optional[int] = None

    # Placeholder demo metadata (optional)
    cluster_id: Optional[str] = None
    manual_label: Optional[str] = None
