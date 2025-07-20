# AI Co-Scientist

A multi-agent AI system for generating scientific hypotheses and research plans using advanced language models.

## 🚀 Features

### Core Functionality
- **Multi-Agent Hypothesis Generation**: Uses 6 specialized AI agents to generate, validate, and refine scientific hypotheses
- **Knowledge Grounding**: Systematic literature review and knowledge validation
- **Scientific Critique**: Rigorous evaluation of hypothesis validity and feasibility
- **Ranking & Evolution**: Multi-criteria ranking and iterative hypothesis refinement
- **Experimental Planning**: Detailed research plans and implementation strategies

### Auto Query Generation
- **`/sample` Endpoint**: Automatically generate diverse scientific research queries
- **Domain Diversity**: Queries span multiple scientific domains (biomedical, materials science, environmental, AI/ML, etc.)
- **Quality Assurance**: Generated queries are scientifically sound and testable
- **Metadata Rich**: Includes complexity levels, estimated hypotheses, and research approaches

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

### AI Agents
1. **Generation Agent** (Gemma 3 12B): Novel hypothesis generation
2. **Proximity Agent** (Gemma 2 9B): Knowledge retrieval and grounding
3. **Reflection Agent** (OpenAI o3-mini): Scientific critique and evaluation
4. **Ranking Agent** (Gemma 2 9B): Multi-criteria hypothesis ranking
5. **Evolution Agent** (Llama 3.3 70B): Iterative hypothesis refinement
6. **Meta-Review Agent** (OpenAI o3-mini): Final review and experimental planning

### Auto Query Generation
- **Model**: Gemma 3 12B for query generation
- **Prompt Engineering**: Specialized prompts for diverse scientific domains
- **Quality Control**: JSON validation and metadata enrichment
- **Error Handling**: Robust error handling for malformed responses

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB (optional, for response storage)
- API keys for required services

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd ai-co-scientist

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables
```bash
# Required
API_KEY=your-api-key
GEMMA_SERVICE_URL=http://localhost:11434

# Optional
GROQ_API_KEY=your-groq-key
OPENAI_API_KEY=your-openai-key
TAVILY_API_KEY=your-tavily-key
MONGODB_URI=your-mongodb-uri
```

### Running the Application
```bash
# Start the server
python main.py

# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Testing the Auto Query Generation
```bash
# Run the test script
python test_sample_endpoint.py

# Or test manually with curl
curl -X GET "http://localhost:8000/sample" \
  -H "X-API-Key: your-api-key"
```

## 📊 Example Usage

### Generate Sample Queries
```python
import requests

# Generate a sample scientific query
response = requests.get(
    "http://localhost:8000/sample",
    headers={"X-API-Key": "your-api-key"}
)

if response.status_code == 200:
    query_data = response.json()
    print(f"Generated Query: {query_data['generated_query']}")
    print(f"Domain: {query_data['domain']}")
    print(f"Complexity: {query_data['complexity_level']}")
```

### Use Generated Query for Hypothesis Generation
```python
# Use the generated query to create hypotheses
query_request = {
    "query": query_data['generated_query'],
    "max_hypotheses": 5
}

hypothesis_response = requests.post(
    "http://localhost:8000/query",
    json=query_request,
    headers={"X-API-Key": "your-api-key"}
)
```

## 🧪 Testing

### Run Tests
```bash
# Test the sample endpoint
python test_sample_endpoint.py

# Test the main hypothesis generation
python test_adk_agents.py
```

### Test Coverage
- ✅ API endpoint functionality
- ✅ Authentication and authorization
- ✅ Response format validation
- ✅ Error handling
- ✅ Domain diversity testing
- ✅ Performance testing

## 📈 Performance Metrics

### Auto Query Generation
- **Response Time**: < 30 seconds
- **Success Rate**: > 95% valid JSON responses
- **Domain Diversity**: 8+ scientific domains
- **Query Quality**: Clear, specific, and scientifically sound

### Hypothesis Generation
- **Processing Time**: 2-5 minutes per query
- **Hypothesis Quality**: Multi-agent validation
- **Scientific Rigor**: Literature grounding and critique

## 🔧 Configuration

### Model Configuration
```python
# utils/config.py
PRIMARY_MODEL = "llama-3.3-70b-versatile"  # For complex reasoning
SECONDARY_MODEL = "gemma2-9b-it"  # For faster operations
```

### Prompt Customization
Edit `prompts.py` to customize:
- Query generation guidelines
- Domain examples
- Output format requirements
- Quality criteria

## 🚨 Error Handling

### Common Issues
1. **GEMMA_SERVICE_URL not configured**: Ensure Gemma service is running
2. **Invalid API Key**: Check your API key configuration
3. **Malformed JSON Response**: The system handles parsing errors gracefully
4. **Timeout Issues**: Increase timeout for complex queries

### Debugging
```bash
# Check logs
tail -f ai_co_scientist_*.log

# Test individual components
python test_prompts.py
python test_mongodb.py
```

## 📚 Documentation

- [Auto Query Generation Guide](docs/AUTO_QUERY_GENERATION.md)
- [Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)
- [Model Deployment Guide](docs/MODEL_DEPLOYMENT.md)
- [Memory System Guide](docs/MEMORY_SYSTEM_GUIDE.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with FastAPI and modern Python practices
- Powered by multiple AI models (Gemma, Llama, OpenAI)
- Inspired by collaborative scientific research methodologies
