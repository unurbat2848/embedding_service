# ACUR Embedding Service

Python FastAPI service for generating sentence embeddings using `all-MiniLM-L6-v2` model.

## Quick Start

### 1. Install Python Dependencies

```bash
cd embedding_service

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Service

```bash
# Development mode (auto-reload)
uvicorn embedding_service:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn embedding_service:app --host 0.0.0.0 --port 8000 --workers 2
```

The service will be available at: `http://localhost:8000`

### 3. Test the Service

Visit `http://localhost:8000/docs` for interactive API documentation.

Or test with curl:

```bash
# Health check
curl http://localhost:8000/health

# Generate embedding
curl -X POST http://localhost:8000/embed \
  -H "Content-Type: application/json" \
  -d '{"text": "Can I submit unfinished work?"}'
```

## API Endpoints

### GET /
Root endpoint with service information

### GET /health
Health check endpoint
- Returns: Service status and model information

### GET /info
Model information endpoint
- Returns: Model details (name, dimension, max sequence length)

### POST /embed
Generate embedding for a single text

**Request:**
```json
{
  "text": "Can I submit unfinished work?",
  "normalize": true
}
```

**Response:**
```json
{
  "embedding": [0.023, -0.145, 0.891, ...],  // 384 floats
  "dimension": 384,
  "processing_time_ms": 45.23
}
```

### POST /embed_batch
Generate embeddings for multiple texts (more efficient)

**Request:**
```json
{
  "texts": [
    "Can I submit unfinished work?",
    "What is the registration fee?",
    "Do I need to do a presentation?"
  ],
  "normalize": true
}
```

**Response:**
```json
{
  "embeddings": [
    [0.023, -0.145, ...],
    [0.156, 0.234, ...],
    [-0.089, 0.456, ...]
  ],
  "dimension": 384,
  "count": 3,
  "processing_time_ms": 98.45
}
```

### POST /similarity
Calculate similarity between query and multiple texts

**Request:**
```json
{
  "query": "Can I submit unfinished work?",
  "texts": [
    "Is incomplete research allowed?",
    "What is the registration fee?",
    "Can group projects be submitted?"
  ]
}
```

**Response:**
```json
{
  "query": "Can I submit unfinished work?",
  "similarities": [0.87, 0.23, 0.45],
  "count": 3
}
```

## Performance

- **Model Load Time:** ~2-5 seconds (on first startup)
- **Single Embedding:** ~30-50ms
- **Batch (10 texts):** ~80-120ms
- **Memory Usage:** ~500MB (model loaded in RAM)

## Production Deployment

### Option 1: Run as Systemd Service (Linux)

Create `/etc/systemd/system/acur-embedding.service`:

```ini
[Unit]
Description=ACUR Embedding Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/chatbot-acur-wp-plugin/embedding_service
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn embedding_service:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl start acur-embedding
sudo systemctl enable acur-embedding
```

### Option 2: Run with Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY embedding_service.py .

CMD ["uvicorn", "embedding_service:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t acur-embedding .
docker run -d -p 8000:8000 --name acur-embedding acur-embedding
```

### Option 3: Run with PM2 (Node.js Process Manager)

```bash
npm install -g pm2
pm2 start "uvicorn embedding_service:app --host 0.0.0.0 --port 8000" --name acur-embedding
pm2 save
pm2 startup
```

## Configuration in WordPress

Update the embedding service URL in your WordPress plugin:

```php
// In wp-config.php or plugin settings
define('ACUR_EMBEDDING_SERVICE_URL', 'http://localhost:8000');

// Or programmatically
ACURCB_Embeddings::set_config('embedding_service_url', 'http://localhost:8000');
ACURCB_Matcher_V1::set_config('embedding_service_url', 'http://localhost:8000');
```

## Troubleshooting

### Service won't start
```bash
# Check if port 8000 is already in use
netstat -an | grep 8000

# Use a different port
uvicorn embedding_service:app --port 8001
```

### Out of memory errors
```bash
# Reduce number of workers
uvicorn embedding_service:app --workers 1

# Or increase system memory
```

### Connection refused from WordPress
```bash
# Check firewall rules
sudo ufw allow 8000

# If running on different server, update the URL
ACURCB_Embeddings::set_config('embedding_service_url', 'http://your-server-ip:8000');
```

## Model Information

**Model:** `all-MiniLM-L6-v2`
- **Size:** ~80MB
- **Dimension:** 384
- **Max Sequence Length:** 256 tokens
- **Language:** English
- **Performance:** Fast and lightweight
- **Accuracy:** High quality semantic representations

**Why this model?**
- Small and fast (perfect for real-time applications)
- High quality embeddings for FAQ matching
- Well-tested and widely used
- Free and open source

## Alternative Deployment Options

### Use External API (No Self-Hosting)

If you prefer not to host your own service, you can use:

1. **HuggingFace Inference API** (Free tier available)
2. **OpenAI Embeddings API** ($0.0001/1K tokens)
3. **Cohere Embeddings API** (Free tier available)

## Monitoring

Check service health:
```bash
curl http://localhost:8000/health
```

View logs:
```bash
# If running directly
# Logs appear in terminal

# If running with systemd
sudo journalctl -u acur-embedding -f

# If running with Docker
docker logs -f acur-embedding

# If running with PM2
pm2 logs acur-embedding
```
