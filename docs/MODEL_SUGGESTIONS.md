# AI Agent Model Recommendations Guide

## Recommended Models by Agent Role

### Generation Agent (Idea/Hypothesis Generation)
Use powerful LLMs to produce creative hypotheses. For highest quality, state-of-the-art chat models like **GPT-4/GPT-4o** (OpenAI) or **Anthropic Claude 3** are top performers. GPT-4 significantly outperforms most others on complex reasoning, and Claude 3 has shown superior accuracy on many benchmarks with huge context windows.

Among open models:
- **Google's Gemma 3** (12B or 27B) is very strong - even Gemma-3 4B-IT matches older 27B models and the 27B version beats Google's own Gemini 1.5-Pro
- **Mistral 7B** (Apache 2.0) leads all 13B-scale LLMs in benchmarks and runs easily on one L4 GPU
- **Meta's LLaMA 3 series** (e.g. 405B open LLaMA 3.1) is now the largest open model, though too big for a single GPU

**In practice:** On an L4, lightweight models like Gemma 3 4B or Mistral 7B (or LLaMA 2-13B with quantization) can generate hypotheses cheaply, while if unconstrained one could use GPT-4/GPT-4o or Gemma 3 27B for best quality. (Gemma 3 models support 128K contexts, though long context isn't needed here.)

### Reflection (Critic) Agent
To critique and refine ideas, use models strong in reasoning and factuality. Again, **GPT-4/GPT-4o** or **Claude 3** are ideal for sophisticated critique (they lead in reasoning benchmarks).

Among open models:
- **Gemma 3** (12B or 27B) or **LLaMA 3/Gemini** are good choices
- A smaller model like **Mistral 7B-instruct** can still provide reasonable critiques and runs on an L4
- Even **LLaMA 2-70B** has shown near-human fact-checking ability, though it won't fit on L4 without cloud hosting

**Summary:** Use the same high-capacity models as Generation (GPT-4, Claude, Gemma) for reflection tasks; if limited to one L4 GPU, use Gemma 3 12B (with FP16) or Mistral 7B.

### Ranking Agent
The ranking agent scores and compares ideas. We can use LLM-based scoring or specialized models.

**For LLM scoring:** GPT-4 or Claude 3 can assign nuanced scores to outputs.

**For embeddings:** A lighter approach is embedding similarity - encode each hypothesis and compute distance. For embeddings:
- **OpenAI's latest models** (text-embedding-3-large or ada-002) are top performers
- Pinecone notes that "Ada is far from the best" and that newer embeddings (OpenAI's text-embedding-3 or Cohere's embed-english-v3.0) far outperform it
- One could embed each idea and use cosine similarity or a learned scorer to rank them

**On L4 GPU:** Even a 7B model (Mistral 7B) with a prompt could score ideas.

### Evolution Agent
This agent recombines or mutates top hypotheses. It is essentially a generative task – propose variations or merged ideas. Again, use a creative LLM.

**Options:**
- **Mistral 7B** or **Gemma 3 12B** would work on L4
- For best results, use **Gemma 3 27B** or **GPT-4/GPT-4o** if available (these large models can generate diverse alternatives)

Evolution often benefits from "self-play" prompts to the same LLM used above. Use the same model family as Generation, focusing on creative text generation.

### Proximity (Retrieval) Agent
This agent grounds ideas with existing knowledge via retrieval. We recommend a **Retrieval-Augmented Generation (RAG)** approach using a vector database.

**Recommended setup:**
- Use **Pinecone** with a high-quality embedding model
- **OpenAI's text-embedding-3-large** or **ada-002** with Pinecone can index scientific texts
- Pinecone's benchmarks rank these among the top, far ahead of older models
- Alternative open-source embed models: **intfloat/e5-base-v2** or **Cohere's embed-english-v3.0**

The proximity agent would take each hypothesis, embed it, and retrieve nearest-neighbor docs or past hypotheses from Pinecone. This vector-based RAG approach avoids web queries and runs on our own infrastructure.

### Meta-Review Agent
The final check should be done by a powerful LLM to ensure coherence and plan proposals. Use a flagship model like **GPT-4/GPT-4o** or **Claude 3** to combine all information and output polished experimental steps. These models are best at high-level summarization and synthesis.

**If restricted to on-premises models:**
- **Gemma 3 27B** (or at least 12B) or **LLaMA 3** (very large) would be top choices
- For a smaller L4-based option: **Gemma 3 12B-IT** or **LLaMA 2-70B** (in the cloud)

Meta-review may also use the same embedding retrieval as the Proximity agent to fetch relevant references for factual grounding.

## Hardware Constraints

### L4-capable Models
The **NVIDIA L4 GPU** (24 GB VRAM) can comfortably run up to ~12B-13B parameter models in mixed precision.

**Recommended for L4:**
- **Gemma 3** 4B/12B
- **Mistral 7B**
- **LLaMA 2** 7B/13B
- **Gemini 1.0/1.5-scale** models

These all fit in 24 GB (especially with FP16/8-bit quantization). For example, Gemma-3-12B (FP16) is just at the limit (≈24 GB).

### Larger Models
If you can use bigger hardware (multi-GPU or cloud), the "best" models include:
- **Gemma 3-27B**
- **LLaMA 3.1-405B** (largest open model)
- **GPT-4/GPT-4o**
- **Anthropic Claude 3**
- Other state-of-the-art (e.g. Google's Gemini Ultra)

These exceed a single L4's memory but deliver superior quality.

## Open-Source vs Proprietary

### Open-Source
- **Google's Gemma 3** (1B/4B/12B/27B) and **Meta's LLaMA 3** (various sizes up to 405B) are fully open models
- **Mistral 7B** (Apache 2.0) is a top-tier open model at 7B size
- **LLaMA 2** (7B/13B/70B) is also open and widely used
- These work well on Cloud Run L4 and can be fine-tuned

### Proprietary
For "best-of-breed" results, commercial models like **GPT-4** (and the multimodal GPT-4o) and **Claude 3** outperform most open models on many tasks.

Since this is a Google hackathon, Google's own offerings (Gemma/Gemini via Vertex AI, or Gemini API) are preferred when possible. However, we also mention GPT/Claude for completeness: if the hackathon rules allow API calls, GPT-4/GPT-4o or Anthropic's Claude can serve as the oracle critics or reviewers.

**In practice:** Open models like Gemma and LLaMA can often approximate these results at lower cost, especially in an on-prem GPU setting.

## Retrieval Approach (Proximity Agent)

We will use **local embedding-based RAG** (no web searches). Specifically, each hypothesis or query is sent through an embedding model and Pinecone is queried for relevant documents.

As noted, **OpenAI's latest embedding models** (text-embedding-3-large or ada-002) have very high semantic retrieval performance. Pinecone's own guides even recommend new models like **Cohere's embed-english-v3** or **Meta's E5** as state-of-art.

Our pipeline will index scientific texts (papers, notes, past hypotheses) in Pinecone, and the Proximity agent will use vector search to ground each hypothesis.

## Language and Context

We focus on **English only** (no multilingual requirement). Long-context support (>8k tokens) can be helpful if you incorporate large documents or long chat histories.

**Long context capabilities:**
- **Google's Gemma 3** and **Anthropic's Claude 3** support very long contexts
  - Gemma 3: up to 128K tokens
  - Claude 3: up to 200K tokens
- For most scientific prompts (a few paragraphs plus hypotheses), the standard 8–16K token context of smaller models is sufficient
  - Gemma 4B: 32K tokens
  - LLaMA2: 4K–32K depending on version

## Sources

We base these recommendations on published model benchmarks and provider documentation:
- Google's Gemma 3 (released Mar 2025) beats previous Gemini models
- Mistral 7B outperforms LLaMA-13B in benchmarks
- Independent tests show GPT-4/Claude 3 lead in accuracy
- Pinecone's guide shows that newer embedding models outperform Ada-002

These sources inform our model choices.
