🤖 Agentic PMS Gateway: Python Tool-Server
This repository demonstrates a scratch-built tool-serving architecture designed to give Large Language Models (LLMs) structured, permissioned, and observable access to a Property Management System (PMS).

🏗️ Architectural Philosophy
Unlike "no-code" nodes that hide logic, this gateway is built as a Python-first Action Layer. It treats AI as a system user that requires:
 * Strict Schema Enforcement: Utilizing Pydantic to ensure the LLM cannot trigger malformed API requests.
 * Stateless Execution: Built on FastAPI for high-concurrency, asynchronous tool execution.
 * Observability: Every "action" taken by the agent is logged, allowing for a "Closed-Loop" feedback system where the agent can report its own success or failure back to the business systems.
   
🚀 Key Features
 * Structured Tool Definitions: Exposes business logic as executable functions via OpenAI/Gemini Function Calling.
 * Environment Parity: Developed on Linux (Zorin OS) and fully Dockerized to ensure absolute consistency between development and production.
 * REST Integration: Custom-built HTTP client logic (using httpx) to interface directly with 3rd-party PMS endpoints.

🛠️ Tech Stack
 * Language: Python 3.11+
 * Framework: FastAPI
 * Validation: Pydantic v2
 * Containerization: Docker
 * Dev Environment: Linux (Zorin OS / Ubuntu)

📖 How it works (The Agentic Loop)
 * Reasoning: The LLM receives a guest request (e.g., "Can I check out at 2 PM?").
 * Tool Selection: The model identifies the extend_checkout tool defined in this gateway.
 * Validation: Our server validates the model's generated arguments against the BookingUpdate schema.
 * Execution: The Python logic performs the "Action" via the PMS API.
 * Observation: The result is returned to the model to confirm the "Loop" is closed and the guest is notified.
