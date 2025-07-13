# 📑 Scenario II — AI Triage Service: Theory Questions

## 1️⃣ Python Concurrency
Compare `asyncio`, native threads, and multiprocessing for I/O-bound vs. CPU-bound tasks in a FastAPI microservice.  
Provide code fragments or pseudocode.

Async IO

This is best suited for I/O based tasks as it runs an event loop in single thread and thus GIL doesn't block when you await. This is 
not good for CPU bound tasks

Native Threads

This is also best suited for I/O based tasks and there is now concept of await GIL will still block if we try to use multi threading
to execute tasks. Also, this is bad for CPU intensive tasks.

Multiprocessing

This is best for CPU bound tasks as task are executed in separate processes and thus GIL doesn't block achieveing true parallelism. In context
of fast API we could use process pools to achieve this.


## 2️⃣ LLM Cost Modeling
Build a simple cost equation for running your triage service (Scenario II) on AWS using an open-source model hosted on GPU-backed EC2.  
Include capex vs. opex components and break-even analysis vs. an API-based commercial LLM.

Never worked on LLMs so far

## 3️⃣ RAG Pipeline
Explain the RAG pipeline you designed on Scenario II.  
Provide your reasoning for designing it like that.  
What would you recommend as an improvement or next steps?

Never worked on LLMs so far

## 4️⃣ RAG Evaluation
Propose a quantitative framework to measure hallucination in a RAG system without human labeling.  
Describe the metrics.

Never worked on LLMs so far

## 5️⃣ Prompt Injection Mitigation
Outline a layered defense strategy (code, infra, and policy) against prompt-injection attacks.

Never worked on LLMs so far