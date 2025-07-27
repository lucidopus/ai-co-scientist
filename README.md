# 🧬 AI Co-Scientist
https://youtu.be/89Gq8mapY8w

A sophisticated multi-agent AI system that generates novel scientific hypotheses through collaborative agent-based reasoning. Built for scientific research acceleration and hypothesis discovery.

## 🎯 Overview

AI Co-Scientist is an advanced research tool that employs multiple specialized AI agents to analyze scientific queries and generate well-reasoned, novel hypotheses. The system leverages state-of-the-art language models including **Gemma 3 12B** (hosted on Google Cloud's L4 GPU) for critical query generation and hypothesis creation, ensuring high-quality scientific outputs.

### 🏗️ System Architecture

The system implements a sophisticated **intelligent orchestrated** 6-stage multi-agent pipeline with **Claude Opus 4** as the orchestration brain:

**🧠 Smart Orchestrator** - **Claude Opus 4** analyzes tasks and assigns optimal models based on task requirements

1. **🔬 Generation Agent** - Creates novel scientific hypotheses using **dynamically assigned model**
2. **📚 Proximity Agent** - Retrieves and analyzes relevant knowledge using **dynamically assigned model**
3. **🔍 Reflection Agent** - Provides scientific critique and evaluation using **dynamically assigned model**
4. **📊 Ranking Agent** - Ranks hypotheses by multiple criteria using **dynamically assigned model**
5. **🧬 Evolution Agent** - Refines and evolves top hypotheses using **dynamically assigned model**
6. **📋 Meta-Review Agent** - Conducts final review and experimental planning using **dynamically assigned model**

## 🚀 Key Features

- **🧠 Intelligent Orchestration**: **Claude Opus 4** dynamically assigns optimal models based on task analysis
- **🎯 Smart Model Selection**: 9 specialized models automatically matched to task requirements
- **📊 Model Strengths Database**: Comprehensive mapping of model capabilities and strengths
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

### Intelligent Multi-Agent System

The system features **Claude Opus 4** as the orchestration brain that dynamically assigns optimal models from 9 available options:

#### **🧠 Smart Orchestrator**
- **Claude Opus 4**: Analyzes tasks and assigns optimal models based on requirements and strengths

#### **Available Models for Dynamic Assignment:**
1. **Llama 3.3 70B**: Complex reasoning and hypothesis generation
2. **Qwen 3 32B**: Advanced mathematical and logical reasoning  
3. **Gemma 3 12B**: Efficient processing with Google Cloud L4 GPU acceleration
4. **Llama 4 Scout**: Exploration and discovery tasks
5. **GPT o3 mini**: Workflow orchestration and agent coordination
6. **Mistral 7B**: Specialized analysis and critique tasks
7. **Gemini 2.5 Pro**: Advanced multimodal reasoning tasks
8. **Claude Opus 4**: Comprehensive scientific review and analysis
9. **DeepSeek R1**: Deep reasoning and reflection tasks

#### **Agent Assignment Process:**
1. **Task Analysis**: Claude Opus 4 analyzes each workflow step
2. **Model Matching**: Optimal model selected based on task requirements and model strengths
3. **Dynamic Assignment**: Agents receive the best-suited model for their specific task
4. **Performance Tracking**: System monitors model assignments and performance

### Gemma 3 12B Usage Areas
- **Query Generation**: Powers the `/sample` endpoint for generating scientific research queries
- **Hypothesis Creation**: Core engine for generating novel scientific hypotheses in the main pipeline
- **Cloud Deployment**: Hosted on Google Cloud Run with NVIDIA L4 GPU for optimal performance

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud account (for Gemma 3 12B deployment)
- API keys for required services:
  - **Anthropic API** (for Claude Opus 4 orchestrator) 🆕
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
│   ├── smart_orchestrator.py        # 🧠 Intelligent orchestrator (Claude Opus 4) 🆕
│   ├── enhanced_workflow_orchestrator.py  # 🚀 Enhanced pipeline with smart orchestration 🆕
│   ├── generation_agent.py          # Hypothesis generation (dynamically assigned)
│   ├── reflection_agent.py          # Scientific critique (dynamically assigned)
│   ├── ranking_agent.py             # Hypothesis ranking (dynamically assigned)
│   ├── evolution_agent.py           # Hypothesis evolution (dynamically assigned)
│   ├── proximity_agent.py           # Knowledge retrieval (dynamically assigned)
│   └── meta_review_agent.py         # Final review (dynamically assigned)
├── utils/                     # Core utilities and services
│   ├── pipelines.py          # 🚀 Enhanced pipeline with smart orchestration 🆕
│   ├── helper.py             # Gemma 3 12B client functions
│   ├── config.py             # 📊 Environment + MODEL_STRENGTHS database 🆕
│   ├── models.py             # Pydantic data models
│   └── memory_service.py     # Enhanced memory management
├── docs/                      # Documentation
│   ├── MODEL_DEPLOYMENT.md   # Gemma 3 12B deployment guide
│   └── *.md                  # Additional documentation
├── main.py                   # FastAPI application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```
## 🧠 Intelligent Orchestration System

### **How Smart Model Assignment Works**

The AI Co-Scientist now features an **intelligent orchestration system** powered by **Claude Opus 4** that automatically assigns the optimal model for each task:

#### **🔍 Task Analysis Process**
1. **Query Analysis**: Claude Opus 4 analyzes the incoming scientific query
2. **Workflow Decomposition**: Breaks down the workflow into individual tasks
3. **Requirement Mapping**: Maps each task's requirements to model capabilities
4. **Optimal Assignment**: Selects the best model based on MODEL_STRENGTHS database

#### **📊 Model Strengths Database**
Each model is characterized by its core strengths:

- **Llama 3.3 70B**: Complex reasoning, hypothesis generation, creative problem-solving
- **Qwen 3 32B**: Mathematical reasoning, quantitative analysis, precise calculations
- **Gemma 3 12B**: Efficient processing, fast inference, resource optimization
- **Llama 4 Scout**: Exploration, discovery, novel approach generation
- **GPT o3 mini**: Workflow orchestration, task coordination, systematic planning
- **Mistral 7B**: Specialized analysis, critical evaluation, detailed assessment
- **Gemini 2.5 Pro**: Multimodal reasoning, visual analysis, integrated processing
- **Claude Opus 4**: Comprehensive analysis, thorough evaluation, scientific rigor
- **DeepSeek R1**: Deep reasoning, reflection, metacognitive analysis

#### **🎯 Dynamic Assignment Examples**
- **Hypothesis Generation** → Assigned to **Llama 3.3 70B** for complex reasoning
- **Mathematical Analysis** → Assigned to **Qwen 3 32B** for quantitative tasks
- **Critical Review** → Assigned to **Mistral 7B** for specialized analysis
- **Final Meta-Review** → Assigned to **Claude Opus 4** for comprehensive evaluation

#### **📈 Performance Optimization**
- **Task-Model Matching**: Ensures each task uses the most suitable model
- **Quality Improvement**: Better results through optimal model selection
- **Resource Efficiency**: Avoids over/under-powered model usage
- **Adaptive Learning**: System learns from assignment performance

### **Configuration Options**

```python
# Enable/disable intelligent orchestration
use_smart_orchestration = True  # Default: True

# Use legacy fixed assignments
use_smart_orchestration = False
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
