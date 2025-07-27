# 🧬 AI Co-Scientist
https://youtu.be/89Gq8mapY8w

A sophisticated multi-agent AI system that generates novel scientific hypotheses through collaborative agent-based reasoning. Built for scientific research acceleration and hypothesis discovery.

## 🎯 Overview

AI Co-Scientist is an advanced research tool that employs multiple specialized AI agents to analyze scientific queries and generate well-reasoned, novel hypotheses. The system leverages state-of-the-art language models including **Gemma 3 12B** (hosted on Google Cloud's L4 GPU) for critical query generation and hypothesis creation, ensuring high-quality scientific outputs.

### 🏗️ System Architecture

The system implements a sophisticated 6-stage multi-agent pipeline:

1. **🔬 Generation Agent** - Creates novel scientific hypotheses using **Gemma 3 12B**
2. **📚 Proximity Agent** - Retrieves and analyzes relevant knowledge using Llama 4 Scout 17B
3. **🔍 Reflection Agent** - Provides scientific critique and evaluation using OpenAI o3-mini
4. **📊 Ranking Agent** - Ranks hypotheses by multiple criteria using Qwen 3 32B
5. **🧬 Evolution Agent** - Refines and evolves top hypotheses using Llama 3.3 70B
6. **📋 Meta-Review Agent** - Conducts final review and experimental planning using OpenAI o3-mini

## 🚀 Key Features

- **Multi-Model Architecture**: Leverages the strengths of different LLMs for specialized tasks
- **Scientific Rigor**: Implements critique, ranking, and evolution cycles for hypothesis refinement
- **Knowledge Integration**: Incorporates external knowledge retrieval and literature analysis
- **Experimental Planning**: Generates detailed experimental approaches for each hypothesis
- **Scalable API**: RESTful FastAPI backend with comprehensive documentation
- **Real-time Processing**: Advanced terminal UI with progress tracking and colored output
- **Data Persistence**: MongoDB integration with JSON fallback for query/response storage
- **Memory System**: Enhanced memory service for session and hypothesis tracking

## 🔧 Gemma 3 12B Integration

**Gemma 3 12B is deployed on Google Cloud's L4 GPU** and serves two critical functions in the pipeline:

### 1. Sample Query Generation (`/sample` endpoint)
- Generates diverse, high-quality scientific research queries
- Used for testing and demonstrating the system capabilities
- Accessed via `utils/helper.py::generate_sample_query()`

### 2. Hypothesis Generation (Core Pipeline)
- Primary model for novel scientific hypothesis creation
- Deployed on NVIDIA L4 GPU (24GB VRAM, 7424 CUDA cores)
- Configured for optimal inference with 8 vCPUs and 32GB RAM
- Accessed via `agents/generation_agent.py` using the `ask_gemma()` function

**Deployment Details:**
- **Hardware**: Google Cloud Run with NVIDIA L4 GPU
- **Service URL**: Configured via `GEMMA_SERVICE_URL` environment variable
- **Performance**: ~50-100 tokens/second with 2-10 second response times
- **Cost**: ~$0.62/hour when active (scales to zero when idle)

## 🛠️ API Endpoints

### Generate Hypotheses
```http
POST /query
Content-Type: application/json
X-API-Key: your-api-key

{
  "query": "How can we develop targeted therapies for rare genetic disorders?",
  "max_hypotheses": 5
}
```

### Auto Query Generation
```http
GET /sample
X-API-Key: your-api-key
```

**Response:**
```json
{
  "query_id": "uuid-string",
  "generated_query": "How can we develop bio-inspired filtration systems for microplastic removal from water sources?",
  "domain": "Environmental Science",
  "complexity_level": "intermediate",
  "estimated_hypotheses": 5,
  "generation_metadata": {
    "subdomain": "Water Treatment",
    "key_concepts": ["bio-inspired", "filtration", "microplastics"],
    "research_approach": "Biomimicry and nanotechnology",
    "potential_impact": "Sustainable water purification",
    "feasibility_factors": ["scalable", "low-cost"],
    "interdisciplinary_elements": ["nanotechnology", "biomimicry"]
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

### Health Check
```http
GET /health
```

## 🏗️ Architecture

### Multi-Agent System
The system uses specialized AI models for different phases:

1. **Generation Agent** - **Gemma 3 12B** (deployed on Google Cloud L4 GPU): Novel hypothesis generation
2. **Proximity Agent** - Llama 4 Scout 17B: Knowledge retrieval and grounding
3. **Reflection Agent** - OpenAI o3-mini: Scientific critique and evaluation
4. **Ranking Agent** - Qwen 3 32B: Multi-criteria hypothesis ranking
5. **Evolution Agent** - Llama 3.3 70B: Iterative hypothesis refinement
6. **Meta-Review Agent** - OpenAI o3-mini: Final review and experimental planning

### Gemma 3 12B Usage Areas
- **Query Generation**: Powers the `/sample` endpoint for generating scientific research queries
- **Hypothesis Creation**: Core engine for generating novel scientific hypotheses in the main pipeline
- **Cloud Deployment**: Hosted on Google Cloud Run with NVIDIA L4 GPU for optimal performance

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud account (for Gemma 3 12B deployment)
- API keys for required services:
  - GROQ API (for Llama models)
  - OpenAI API (for o3-mini)
  - Tavily API (for knowledge retrieval)
- MongoDB instance (optional, JSON fallback available)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/ai-co-scientist.git
   cd ai-co-scientist
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Deploy Gemma 3 12B:**
   Follow the detailed guide in `docs/MODEL_DEPLOYMENT.md` to deploy Gemma 3 12B on Google Cloud Run with L4 GPU.

### Start the API server:
```bash
python main.py
```

The server will start on `http://localhost:8000`

### API Endpoints:

#### Generate Hypotheses
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "query": "How might quantum entanglement be leveraged for biological information processing?",
    "max_hypotheses": 3
  }'
```

#### Generate Sample Query
```bash
curl -X GET "http://localhost:8000/sample" \
  -H "X-API-Key: your_api_key"
```

#### Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

### Interactive Documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔬 Example Usage

### Input Query:
```json
{
  "query": "What novel approaches could enhance CRISPR gene editing precision?",
  "max_hypotheses": 3
}
```

### System Response:
The system will process through all 6 agents and return:
- **3 novel hypotheses** with detailed descriptions and reasoning
- **Scientific critique** and validity assessments
- **Feasibility scores** and confidence ratings
- **Experimental plans** for each hypothesis
- **Literature recommendations** and collaboration suggestions
- **Processing metadata** including execution times and model information

### Python Client Example:
```python
import requests

# Generate a sample scientific query using Gemma 3 12B
response = requests.get(
    "http://localhost:8000/sample",
    headers={"X-API-Key": "your-api-key"}
)

generated_query = response.json()['generated_query']

# Use the generated query to create hypotheses
query_request = {
    "query": generated_query,
    "max_hypotheses": 3
}

hypothesis_response = requests.post(
    "http://localhost:8000/query",
    json=query_request,
    headers={"X-API-Key": "your-api-key"}
)

results = hypothesis_response.json()
print(f"Generated {len(results['hypotheses'])} hypotheses in {results['total_processing_time']:.2f}s")
```

## 🏗️ Project Structure

```
ai-co-scientist/
├── agents/                    # Multi-agent system components
│   ├── generation_agent.py   # Hypothesis generation (Gemma 3 12B)
│   ├── reflection_agent.py   # Scientific critique (o3-mini)
│   ├── ranking_agent.py      # Hypothesis ranking (Qwen 3 32B)
│   ├── evolution_agent.py    # Hypothesis evolution (Llama 3.3 70B)
│   ├── proximity_agent.py    # Knowledge retrieval (Llama 4 Scout)
│   └── meta_review_agent.py  # Final review (o3-mini)
├── utils/                     # Core utilities and services
│   ├── pipelines.py          # Main processing pipeline
│   ├── helper.py             # Gemma 3 12B client functions
│   ├── config.py             # Environment configuration
│   ├── models.py             # Pydantic data models
│   └── memory_service.py     # Enhanced memory management
├── docs/                      # Documentation
│   ├── MODEL_DEPLOYMENT.md   # Gemma 3 12B deployment guide
│   └── *.md                  # Additional documentation
├── main.py                   # FastAPI application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```
## 🔧 Configuration

### Performance Settings
- **Concurrency**: 4 simultaneous requests per instance
- **Memory**: 32GB RAM allocation
- **GPU**: Single NVIDIA L4 (24GB VRAM)
- **Timeout**: 600 seconds for complex processing

## 🔍 Monitoring & Debugging

### Real-time Terminal Output
The system provides comprehensive colored terminal output including:
- 🔄 Progress bars for multi-step processing
- 🤖 Agent activity logs with timing information
- 📊 Hypothesis summaries with scoring metrics
- ✅ Success/error indicators with detailed messages

## 💾 Data Storage

### Query Responses
All query/response pairs are stored in:
- **Primary**: MongoDB collection (`requests`)
- **Fallback**: JSON file (`results/query_responses.json`)

### Memory System
Enhanced memory service stores:
- Research sessions with metadata
- Individual hypotheses with evaluations
- Processing steps and agent outputs
- Confidence scores and quality metrics

## 💰 Cost Optimization

### Gemma 3 12B Hosting Costs
- **Active usage**: ~$0.62/hour (L4 GPU + compute)
- **Idle time**: $0/hour (scales to zero)
- **Monthly estimates**: $31-124 depending on usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For questions, issues, or contributions:
- 📧 Email: [Support Contact](harshilpatel30402@gmail.com)
- 🐛 Issues: [GitHub Issues](https://github.com/your-/ai-co-scientist/issues)
- 📖 Docs: See the `docs/` directory for detailed guides

---
