# ADR-0001: Capstone Framing — Question & Answer Bot

- **Status:** Draft v1
- **Date:** 30-Aug-2026
- **Author:** Karthik SR

## Context

I would like to build an advanced RAG Pipeline, that Retrieves and summarises documents based on user Query.
I would like to use BiC Model, tools and framewokes available to build this end to end pipeline that validates the input and output and returns the best possible answer to the user in the right format.

## Decision — Solution Framing Canvas

| Box | Your answer |
|-----|-------------|
| **Inputs** | A Natural Langualge Query mostly in English, but can also include translations as part of the pipeline|
| **Outputs** | A grounded Answer to the user quer, with Citations linking it to the source of the answer.  
| **Tools** | OpenAI Models, Agents, Input Dcouments vectorised
| **Memory** | probably durable history or we can use assitant to send historic chat info|
| **Autonomy level** | Agentic System, bec we will be using multiple agents, Tool Integration, MCP and such as part of this pipeline|
| **Decision boundaries** | it may answer any question whose retrieval confidence exceeds a threshold, otherwise birng Human in the loop

## Consequences

- **Positive:** Saves the user the headache of searching multiple documents to find the correnc answer.  The platform will give the user a correct grounded answer with Cited documents using a UI which makes it easier for NON TECH USERS
- **Negative / risks:** Halluciantion, bias, unethical content or answers could come in the resposne and we need to ensure there are gates to keey them away.
- **Things we'll re-visit:** Mostly will refine  parts of the ADR.