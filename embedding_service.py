"""
ACUR Chatbot Embedding Service
FastAPI service for generating sentence embeddings using all-MiniLM-L6-v2

This service provides:
- /embed endpoint: Generate embedding for a single text
- /embed_batch endpoint: Generate embeddings for multiple texts
- /health endpoint: Health check
- /info endpoint: Model information

Usage:
    uvicorn embedding_service:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from typing import List, Optional
import numpy as np
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ACUR Embedding Service",
    description="Sentence embedding service using all-MiniLM-L6-v2",
    version="1.0.0"
)

# Add CORS middleware to allow requests from WordPress
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance (loaded once at startup)
MODEL_NAME = 'all-MiniLM-L6-v2'
model = None


@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    global model
    logger.info(f"Loading model: {MODEL_NAME}")
    start_time = time.time()

    try:
        model = SentenceTransformer(MODEL_NAME)
        load_time = time.time() - start_time
        logger.info(f"Model loaded successfully in {load_time:.2f} seconds")
        logger.info(f"Model dimension: {model.get_sentence_embedding_dimension()}")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise


# Request/Response models
class EmbedRequest(BaseModel):
    text: str = Field(..., description="Text to embed", min_length=1, max_length=5000)
    normalize: bool = Field(default=True, description="Normalize embedding to unit length")


class EmbedBatchRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to embed", min_items=1, max_items=100)
    normalize: bool = Field(default=True, description="Normalize embeddings to unit length")


class EmbedResponse(BaseModel):
    embedding: List[float] = Field(..., description="Embedding vector")
    dimension: int = Field(..., description="Embedding dimension")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class EmbedBatchResponse(BaseModel):
    embeddings: List[List[float]] = Field(..., description="List of embedding vectors")
    dimension: int = Field(..., description="Embedding dimension")
    count: int = Field(..., description="Number of embeddings")
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")


class HealthResponse(BaseModel):
    status: str
    model: str
    dimension: int
    message: str


class InfoResponse(BaseModel):
    model_name: str
    dimension: int
    max_seq_length: int
    description: str


# Endpoints
@app.get("/", tags=["General"])
async def root():
    """Root endpoint"""
    return {
        "service": "ACUR Embedding Service",
        "status": "online",
        "model": MODEL_NAME,
        "endpoints": {
            "/embed": "POST - Generate single embedding",
            "/embed_batch": "POST - Generate multiple embeddings",
            "/health": "GET - Health check",
            "/info": "GET - Model information"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return HealthResponse(
        status="healthy",
        model=MODEL_NAME,
        dimension=model.get_sentence_embedding_dimension(),
        message="Service is running"
    )


@app.get("/info", response_model=InfoResponse, tags=["General"])
async def model_info():
    """Get model information"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return InfoResponse(
        model_name=MODEL_NAME,
        dimension=model.get_sentence_embedding_dimension(),
        max_seq_length=model.max_seq_length,
        description="all-MiniLM-L6-v2 is a sentence-transformers model that maps sentences to a 384-dimensional dense vector space"
    )


@app.post("/embed", response_model=EmbedResponse, tags=["Embedding"])
async def create_embedding(request: EmbedRequest):
    """
    Generate embedding for a single text

    Args:
        request: EmbedRequest containing text to embed

    Returns:
        EmbedResponse with embedding vector and metadata
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        start_time = time.time()

        # Generate embedding
        embedding = model.encode(
            request.text,
            convert_to_numpy=True,
            normalize_embeddings=request.normalize
        )

        processing_time = (time.time() - start_time) * 1000  # Convert to ms

        logger.info(f"Generated embedding for text of length {len(request.text)} in {processing_time:.2f}ms")

        return EmbedResponse(
            embedding=embedding.tolist(),
            dimension=len(embedding),
            processing_time_ms=round(processing_time, 2)
        )

    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")


@app.post("/embed_batch", response_model=EmbedBatchResponse, tags=["Embedding"])
async def create_embeddings_batch(request: EmbedBatchRequest):
    """
    Generate embeddings for multiple texts (batch processing)

    Args:
        request: EmbedBatchRequest containing list of texts

    Returns:
        EmbedBatchResponse with list of embeddings and metadata
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        start_time = time.time()

        # Generate embeddings in batch (more efficient)
        embeddings = model.encode(
            request.texts,
            convert_to_numpy=True,
            normalize_embeddings=request.normalize,
            show_progress_bar=False
        )

        processing_time = (time.time() - start_time) * 1000  # Convert to ms

        logger.info(f"Generated {len(request.texts)} embeddings in {processing_time:.2f}ms")

        return EmbedBatchResponse(
            embeddings=embeddings.tolist(),
            dimension=embeddings.shape[1],
            count=len(embeddings),
            processing_time_ms=round(processing_time, 2)
        )

    except Exception as e:
        logger.error(f"Error generating batch embeddings: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating embeddings: {str(e)}")


@app.post("/similarity", tags=["Utility"])
async def calculate_similarity(query: str, texts: List[str]):
    """
    Calculate cosine similarity between a query and multiple texts

    Args:
        query: Query text
        texts: List of texts to compare against

    Returns:
        List of similarity scores (0-1)
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Encode query and texts
        query_embedding = model.encode(query, convert_to_numpy=True, normalize_embeddings=True)
        text_embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

        # Calculate cosine similarity (dot product since normalized)
        similarities = np.dot(text_embeddings, query_embedding)

        return {
            "query": query,
            "similarities": similarities.tolist(),
            "count": len(similarities)
        }

    except Exception as e:
        logger.error(f"Error calculating similarities: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating similarities: {str(e)}")


# Run with: uvicorn embedding_service:app --host 0.0.0.0 --port 8000 --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
