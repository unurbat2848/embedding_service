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

#### Option A: Using Startup Scripts (Recommended)

```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

#### Option B: Using Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env to set custom port/host (optional)
# Then run:
python embedding_service.py
```

#### Option C: Direct with Custom Port

```bash
# Using environment variables
export EMBEDDING_SERVICE_PORT=8080
export EMBEDDING_SERVICE_HOST=0.0.0.0
python embedding_service.py

# Or using uvicorn directly
uvicorn embedding_service:app --host 0.0.0.0 --port 8000 --reload
```

The service will be available at: `http://localhost:8000` (or your custom port)

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

### Option 1: Deploy to Render.com (Recommended for Cloud)

See **[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)** for complete deployment guide.

Quick start:
1. Push code to GitHub/GitLab
2. Create new Web Service on Render
3. Use build command: `pip install -r requirements.txt`
4. Use start command: `uvicorn embedding_service:app --host 0.0.0.0 --port $PORT`
5. Deploy and get your URL: `https://your-service.onrender.com`

### Option 2: Run as Systemd Service (Linux)

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
Environment="EMBEDDING_SERVICE_HOST=0.0.0.0"
Environment="EMBEDDING_SERVICE_PORT=8000"
ExecStart=/path/to/venv/bin/python embedding_service.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl start acur-embedding
sudo systemctl enable acur-embedding
sudo systemctl status acur-embedding
```

### Option 2: Run with Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY embedding_service.py .

# Default environment variables (can be overridden)
ENV EMBEDDING_SERVICE_HOST=0.0.0.0
ENV EMBEDDING_SERVICE_PORT=8000

CMD ["python", "embedding_service.py"]
```

Build and run:
```bash
# Build image
docker build -t acur-embedding .

# Run with default port 8000
docker run -d -p 8000:8000 --name acur-embedding acur-embedding

# Run with custom port
docker run -d -p 8080:8080 \
  -e EMBEDDING_SERVICE_PORT=8080 \
  --name acur-embedding \
  acur-embedding
```

### Option 3: Run with PM2 (Node.js Process Manager)

```bash
npm install -g pm2
pm2 start "uvicorn embedding_service:app --host 0.0.0.0 --port 8000" --name acur-embedding
pm2 save
pm2 startup
```

## Configuration

### Environment Variables

The service supports the following environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_SERVICE_HOST` | `0.0.0.0` | Host to bind the service to. Use `127.0.0.1` for local-only access |
| `EMBEDDING_SERVICE_PORT` | `8000` | Port number for the service |

**Example usage:**

```bash
# Linux/Mac
export EMBEDDING_SERVICE_PORT=8080
export EMBEDDING_SERVICE_HOST=127.0.0.1
python embedding_service.py

# Windows (Command Prompt)
set EMBEDDING_SERVICE_PORT=8080
set EMBEDDING_SERVICE_HOST=127.0.0.1
python embedding_service.py

# Windows (PowerShell)
$env:EMBEDDING_SERVICE_PORT=8080
$env:EMBEDDING_SERVICE_HOST="127.0.0.1"
python embedding_service.py
```

### WordPress Plugin Configuration

Update the embedding service URL in your WordPress plugin to match your configuration:

```php
// In wp-config.php or plugin settings
define('ACUR_EMBEDDING_SERVICE_URL', 'http://localhost:8000');

// If using custom port
define('ACUR_EMBEDDING_SERVICE_URL', 'http://localhost:8080');

// Or programmatically
ACURCB_Embeddings::set_config('embedding_service_url', 'http://localhost:8000');
ACURCB_Matcher_V1::set_config('embedding_service_url', 'http://localhost:8000');
```

## Troubleshooting

### Service won't start
```bash
# Check if port 8000 is already in use
netstat -an | grep 8000

# Use a different port with environment variable
export EMBEDDING_SERVICE_PORT=8001
python embedding_service.py

# Or use uvicorn directly
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
