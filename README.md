# Autonomous CI/CD Remediation Agent

An AI-powered DevOps agent that monitors GitHub Actions, diagnoses CI failures with repository-aware context, and opens fix pull requests. The system combines a FastAPI backend, LangGraph/LangChain orchestration, PostgreSQL/pgvector memory, provider-neutral CD diagnostics, Telegram approval workflows, and a React dashboard.

## Highlights

- **Autonomous CI fixer:** Receives GitHub `workflow_run` webhooks, fetches failed job logs, builds context from the Repository Structure Index (RSI), generates a patch, and opens a GitHub fix PR.
- **Repository Structure Index:** Parses repo files into PostgreSQL tables for file roles, symbols, imports, sensitivity flags, and repo summaries so the agent can retrieve targeted context instead of sending the whole codebase to the LLM.
- **Episodic memory:** Stores merged fix knowledge in `agent_memory` with OpenAI embeddings, pgvector `vector(1024)`, HNSW indexing, and cosine similarity for few-shot RAG on future failures.
- **PR review workflow:** Reviews pull requests with RSI context, quality thresholds, Telegram approval actions, and optional fix generation for low-scoring changes.
- **Cloud-agnostic CD diagnostics:** Normalizes AWS, GCP, Azure, and custom webhook failures into a shared `CDFailureContext` before LLM diagnosis.
- **Portfolio-ready deployment:** Includes Dockerfiles, Docker Compose with PostgreSQL/pgvector, environment templates, and benchmark tooling for measuring debugging-time reduction.
## Architecture
<img width="6548" height="2766" alt="fossflow-export-2026-04-16T17_33_18 977Z" src="https://github.com/user-attachments/assets/88bad79f-94b5-40d3-89a1-820b7f0eb261" />


## Technology Stack

**Backend:**
- Python 3.13+, FastAPI, Uvicorn
- LangChain, LangGraph, Model Context Protocol (MCP)
- PostgreSQL (asyncpg) for RSI storage and event history
- SSE (Server-Sent Events) for real-time frontend logs

**Frontend:**
- React 19, TypeScript, Vite
- Tailwind CSS 4
- React Router

## Setup & Installation

### Prerequisites
- Python 3.13+
- Node.js 20+
- PostgreSQL instance running
- GitHub App with Webhook access configured
- Telegram Bot Token

### Backend Setup

1. **Navigate to the server directory**:
   ```bash
   cd server
   ```
2. **Install dependencies** (assuming a virtual environment):
   ```bash
   uv sync
   ```
3. **Configuration**:
   Ensure you have configured environment variables (GitHub tokens, OpenAI/LLM keys, Database URL, Telegram tokens).
4. **Run the API server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Frontend Setup

1. **Navigate to the client directory**:
   ```bash
   cd client
   ```
2. **Install dependencies**:
   ```bash
   npm install
   ```
3. **Run the dev server**:
   ```bash
   npm run dev
   ```

### Agent Workflow Dynamics

Our agent orchestrates multiple distinct operational flows simultaneously based on real-time triggers.

```mermaid
stateDiagram-v2
    START --> EventRouter

    state EventRouter {
        [*] --> CI_Failure: GitHub (check_run)
        [*] --> PR_Action: GitHub (pull_request)
        [*] --> CD_Anomaly: Cloud Webhook
    }

    state CI_Failure {
        AnalyzeTrace --> FetchRSIContext: Extract Failed Specs
        FetchRSIContext --> QueryMemory: Semantic Search (pgvector)
        QueryMemory --> GenerateFix: Inject Context + Past Fixes
        GenerateFix --> SubmitPR: LangGraph Node
    }

    state PR_Action {
        ReviewCode --> CalculateScore: Analyze Diffs + RSI Context
        CalculateScore --> ScoreGated: Score >= 75
        ScoreGated --> Clear to merge
        CalculateScore --> ScoreWarning: Score 50-74
        ScoreWarning --> RequestTelegramApproval: Gate CI/CD
        CalculateScore --> ScoreFailed: Score < 50
        ScoreFailed --> BlockStatus
        ScoreFailed --> TriggerFixAgent: Suggest Improvements
    }
    
    state CD_Anomaly {
        NormalizeMetrics --> HealthCheck: CD Adapters
        HealthCheck --> RootCauseAnalysis: LLM Diagnosis
        RootCauseAnalysis --> EvaluateRisk
        EvaluateRisk --> SendTelegramReport
    }

    CI_Failure --> END
    PR_Action --> END
    CD_Anomaly --> END
```

## 🧠 Agent Episodic Memory

Rather than solving the same errors from scratch, the platform utilizes a pgvector-powered episodic memory system to "remember" successful past fixes.

- **Continuous Learning:** When an agent successfully merges a fix for a CI failure, the original error trace, root cause, and the files changed are embedded into an `agent_memory` schema utilizing a `vector(1024)` HNSW index (via Cosine similarity).
- **Dynamic Few-Shot RAG:** When a new CI failure occurs, the LangGraph agent queries this vector database against the new error signature. If a highly similar past scenario is found, it dynamically injects the previous successful methodology directly into its reasoning prompt, dramatically reducing resolution time and token usage.

## Preventing Vendor Lock-in (CD Monitoring)

A major feature of this project is its robust abstraction layer for Continuous Deployment (CD) failures, completely decoupling the platform from any single cloud provider's proprietary webhook or logging ecosystem.

- **Unified Interface:** We use an adapter pattern (`cd_providers.get_cd_adapter()`) that dynamically parses failures based on the exact deployment target.
- **Normalized Context:** Whether the failure comes from AWS (CloudWatch/CodeDeploy), GCP (Cloud Logging), Azure (Monitor), or a custom internal webhook, it undergoes normalization into a standardized `CDFailureContext`. 
- **LLM Agnostic Diagnosis:** Because the AI agent only interfaces with the abstracted `CDFailureContext` to diagnose errors and generate root cause report, teams can migrate across cloud providers without changing their root-cause analysis pipelines.

## RSI (Repository Structure Index) Schema

To feed the LangGraph agent with precise codebase context without blowing up the LLM token limit, our RSI system maps the entire codebase into a vector-backed PostgreSQL schema:

- `rsi_file_map`: Stores file paths, role tags (`source`, `config`), line counts, and short AI-generated descriptions for every codebase file.
- `rsi_symbol_map`: Tracks the exact line boundaries of defined classes and functions to allow targeted, high-precision code retrieval.
- `rsi_imports`: Acts as a dependency graph index. Traces module connections backward and forward to assess the blast radius of proposed code changes.
- `rsi_repo_summary`: A high-level cache holding the tech stack footprint, global entry points, and project description, functioning as a lightweight `CLAUDE.md`.
- `agent_memory`: Stores the HNSW vector embeddings of past successful CI fixes for episodic memory retrieval.
---
