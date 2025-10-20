"""
Configuration file for the KidSafe Food Analyzer backend.
"""

from pathlib import Path

# Project structure
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "Data"
INPUT_DIR = DATA_DIR / "Input"

# PDF file path
FOOD_LABELING_PDF = INPUT_DIR / "Food-Labeling-Guide-(PDF).pdf"

# Model configurations
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200

# Vector store configurations
QDRANT_COLLECTION_NAME = "food_safety_knowledge"
QDRANT_LOCATION = ":memory:"  # In-memory for simplicity, can change to persistent later

# LLM Model names
CHAT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

