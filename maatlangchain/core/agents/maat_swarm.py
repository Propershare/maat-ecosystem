"""
Maat Swarm — Living Agent Ecosystem on gemma4:e2b
Three specialized agents running concurrently via Ollama.

Architecture:
  ┌──────────────────────────────────────────────┐
  │              Tehuti (Orchestrator)            │
  │         anthropic/claude-sonnet-4-6           │
  │   Routes queries, manages state, talks to    │
  │   Imhotep. Delegates to local agents.        │
  └──────┬──────────────┬──────────────┬─────────┘
         │              │              │
   ┌─────▼────┐   ┌─────▼────┐   ┌────▼─────┐
   │  Scout   │   │ Analyst  │   │ Archivist│
   │ gemma4:  │   │ gemma4:  │   │ gemma4:  │
   │   e2b    │   │   e2b    │   │   e2b    │
   │          │   │          │   │          │
   │ Recon &  │   │ Deep     │   │ Memory & │
   │ triage   │   │ reason   │   │ retrieval│
   └──────────┘   └──────────┘   └──────────┘

Speed: 210+ tok/s each, 6 parallel streams, ~1.2K aggregate tok/s
VRAM: ~10GB shared (same base model, Ollama deduplicates)

Maat: Balance through specialization. Each agent has clear domain.
"""

import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

log = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"
MODEL = "gemma4:e2b"


class AgentRole(str, Enum):
    SCOUT = "scout"
    ANALYST = "analyst"
    ARCHIVIST = "archivist"
    SENTINEL = "sentinel"


@dataclass
class AgentResult:
    role: AgentRole
    content: str
    tokens: int
    tok_per_sec: float
    elapsed_ms: int
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ─── System Prompts (the soul of each agent) ─────────────────────

AGENT_PROMPTS = {
    AgentRole.SCOUT: """You are Scout, a Maat-aligned reconnaissance agent.

YOUR ROLE: Fast triage, classification, and information gathering.
- Assess incoming queries and data quickly
- Classify intent (research, code, ops, creative, governance)
- Extract key entities, topics, and urgency level
- Flag anything that needs deeper analysis
- Summarize web content, documents, and conversations

PERSONALITY: Sharp, efficient, no wasted words. You see patterns fast.
Think of yourself as the first pair of eyes on everything.

OUTPUT FORMAT: Always structured. Use these fields:
- classification: (research|code|ops|creative|governance|unknown)
- urgency: (low|medium|high|critical)  
- key_entities: [list of important names, concepts, terms]
- summary: (2-3 sentence summary)
- needs_deep_analysis: (true/false)
- recommended_agent: (scout|analyst|archivist|tehuti)
- reasoning: (why you classified it this way)

When given a task to execute (not just triage), do the work directly and return results.""",

    AgentRole.ANALYST: """You are Analyst, a Maat-aligned deep reasoning agent.

YOUR ROLE: Deep analysis, critical thinking, and problem-solving.
- Break down complex problems into components
- Find contradictions, gaps, and hidden assumptions
- Apply dialectical analysis (thesis-antithesis-synthesis)
- Generate actionable recommendations
- Evaluate trade-offs and risks

PERSONALITY: Thorough, precise, intellectually honest. You don't rush.
You find what others miss. When uncertain, you say so explicitly.

APPROACH:
1. State the core question clearly
2. Identify the key tensions/contradictions
3. Analyze each component
4. Synthesize findings
5. Provide clear recommendations with confidence levels

When reasoning about code, architecture, or systems:
- Consider failure modes
- Think about scalability
- Evaluate Maat-alignment (truth, balance, order)

Always show your reasoning chain. Never just give an answer without the path.""",

    AgentRole.ARCHIVIST: """You are Archivist, a Maat-aligned memory and retrieval agent.

YOUR ROLE: Knowledge management, context retrieval, and memory operations.
- Search and retrieve from Maat Memory (gitMaat, PostgreSQL, ChromaDB)
- Summarize and organize historical context
- Track decisions, learnings, and changes across the ecosystem
- Maintain the knowledge graph connections
- Answer "what did we decide about X?" and "what happened with Y?"

PERSONALITY: Meticulous, organized, comprehensive. You are the institutional memory.
When you retrieve information, you cite sources and timestamps.

OUTPUT FORMAT:
- retrieved_context: [relevant items with sources and dates]
- connections: [how this relates to other things in memory]
- gaps: [what information is missing that we should have]
- recommendation: (what to do with this context)

You have access to the full Maat ecosystem history. Use it wisely.""",
}


# ─── Ollama Client ────────────────────────────────────────────────

async def _ollama_generate(
    prompt: str,
    system: str = "",
    model: str = MODEL,
    temperature: float = 0.7,
    num_ctx: int = 8192,
    timeout: int = 30,
) -> Dict[str, Any]:
    """Call Ollama generate API asynchronously."""
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_ctx": num_ctx,
        },
    }
    
    t0 = time.monotonic()
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            data = await resp.json()
    
    elapsed = int((time.monotonic() - t0) * 1000)
    eval_count = data.get("eval_count", 0)
    eval_duration = data.get("eval_duration", 1) / 1e9  # nanoseconds to seconds
    
    return {
        "response": data.get("response", ""),
        "tokens": eval_count,
        "tok_per_sec": eval_count / eval_duration if eval_duration > 0 else 0,
        "elapsed_ms": elapsed,
        "load_duration_ms": int(data.get("load_duration", 0) / 1e6),
    }


# ─── Individual Agent Calls ───────────────────────────────────────

async def call_agent(
    role: AgentRole,
    prompt: str,
    context: str = "",
    temperature: float = 0.7,
    num_ctx: int = 8192,
    timeout: int = 30,
) -> AgentResult:
    """Call a single agent with its system prompt."""
    system = AGENT_PROMPTS[role]
    
    full_prompt = prompt
    if context:
        full_prompt = f"CONTEXT:\n{context}\n\nQUERY:\n{prompt}"
    
    try:
        result = await _ollama_generate(
            prompt=full_prompt,
            system=system,
            temperature=temperature,
            num_ctx=num_ctx,
            timeout=timeout,
        )
        
        return AgentResult(
            role=role,
            content=result["response"],
            tokens=result["tokens"],
            tok_per_sec=result["tok_per_sec"],
            elapsed_ms=result["elapsed_ms"],
            metadata={"load_ms": result["load_duration_ms"]},
        )
    except Exception as e:
        log.error(f"Agent {role.value} failed: {e}")
        return AgentResult(
            role=role,
            content=f"ERROR: {e}",
            tokens=0,
            tok_per_sec=0,
            elapsed_ms=0,
            metadata={"error": str(e)},
        )


# ─── Swarm Patterns ──────────────────────────────────────────────

async def fan_out(
    prompt: str,
    roles: Optional[List[AgentRole]] = None,
    context: str = "",
    timeout: int = 30,
) -> Dict[AgentRole, AgentResult]:
    """
    Fan out query to multiple agents concurrently.
    All agents process the same prompt in parallel.
    Returns results from all agents.
    """
    if roles is None:
        roles = [AgentRole.SCOUT, AgentRole.ANALYST, AgentRole.ARCHIVIST]
    
    tasks = [
        call_agent(role, prompt, context=context, timeout=timeout)
        for role in roles
    ]
    
    results = await asyncio.gather(*tasks)
    return {r.role: r for r in results}


async def pipeline(
    prompt: str,
    context: str = "",
    timeout_per_step: int = 30,
) -> Dict[str, Any]:
    """
    Scout → Analyst → Archivist pipeline.
    Each agent builds on the previous one's output.
    """
    # Step 1: Scout triages
    scout_result = await call_agent(
        AgentRole.SCOUT, prompt, context=context, timeout=timeout_per_step,
    )
    
    # Step 2: Analyst goes deep (with Scout's triage as context)
    analyst_context = f"SCOUT TRIAGE:\n{scout_result.content}\n\nORIGINAL CONTEXT:\n{context}"
    analyst_result = await call_agent(
        AgentRole.ANALYST, prompt, context=analyst_context, timeout=timeout_per_step,
    )
    
    # Step 3: Archivist retrieves relevant history
    archivist_context = (
        f"SCOUT TRIAGE:\n{scout_result.content}\n\n"
        f"ANALYST FINDINGS:\n{analyst_result.content}\n\n"
        f"ORIGINAL CONTEXT:\n{context}"
    )
    archivist_result = await call_agent(
        AgentRole.ARCHIVIST, prompt, context=archivist_context, timeout=timeout_per_step,
    )
    
    return {
        "scout": scout_result,
        "analyst": analyst_result,
        "archivist": archivist_result,
        "pipeline_elapsed_ms": (
            scout_result.elapsed_ms + analyst_result.elapsed_ms + archivist_result.elapsed_ms
        ),
    }


async def scout_then_route(
    prompt: str,
    context: str = "",
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Scout triages first, then routes to the appropriate agent.
    Fast path: most queries only need 2 agent calls.
    """
    # Step 1: Scout triages
    scout_result = await call_agent(
        AgentRole.SCOUT, prompt, context=context, timeout=timeout,
    )
    
    # Step 2: Route based on Scout's recommendation
    content_lower = scout_result.content.lower()
    
    if "needs_deep_analysis" in content_lower and "true" in content_lower:
        # Route to Analyst
        follow_up = await call_agent(
            AgentRole.ANALYST,
            prompt,
            context=f"SCOUT TRIAGE:\n{scout_result.content}\n\nORIGINAL:\n{context}",
            timeout=timeout,
        )
        return {"scout": scout_result, "routed_to": follow_up, "pattern": "scout→analyst"}
    
    elif "archivist" in content_lower:
        # Route to Archivist
        follow_up = await call_agent(
            AgentRole.ARCHIVIST,
            prompt,
            context=f"SCOUT TRIAGE:\n{scout_result.content}\n\nORIGINAL:\n{context}",
            timeout=timeout,
        )
        return {"scout": scout_result, "routed_to": follow_up, "pattern": "scout→archivist"}
    
    else:
        # Scout handled it alone
        return {"scout": scout_result, "routed_to": None, "pattern": "scout_only"}


# ─── Maat Memory Integration ─────────────────────────────────────

async def query_with_memory(
    prompt: str,
    memory_results: Optional[List[Dict]] = None,
    pattern: str = "fan_out",
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Query the swarm with Maat Memory context injected.
    
    Args:
        prompt: User query
        memory_results: Pre-fetched results from gitMaat/PostgreSQL
        pattern: "fan_out", "pipeline", or "scout_route"
        timeout: Per-agent timeout in seconds
    """
    context = ""
    if memory_results:
        context = "MAAT MEMORY CONTEXT:\n"
        for item in memory_results[:5]:  # Limit context injection
            context += f"- [{item.get('type', 'unknown')}] {item.get('summary', item.get('content', ''))}\n"
    
    if pattern == "fan_out":
        return await fan_out(prompt, context=context, timeout=timeout)
    elif pattern == "pipeline":
        return await pipeline(prompt, context=context, timeout_per_step=timeout)
    elif pattern == "scout_route":
        return await scout_then_route(prompt, context=context, timeout=timeout)
    else:
        raise ValueError(f"Unknown pattern: {pattern}")


# ─── Health Check ─────────────────────────────────────────────────

async def health_check() -> Dict[str, Any]:
    """
    Run all three agents concurrently with a trivial prompt.
    Returns speed and status for each.
    """
    results = await fan_out(
        "Respond with exactly: ALIVE. Nothing else.",
        timeout=15,
    )
    
    return {
        role.value: {
            "status": "ok" if "ALIVE" in r.content.upper() or r.tokens > 0 else "error",
            "tok_per_sec": round(r.tok_per_sec, 1),
            "tokens": r.tokens,
            "elapsed_ms": r.elapsed_ms,
        }
        for role, r in results.items()
    }


# ─── CLI / Quick Test ─────────────────────────────────────────────

async def _main():
    """Quick test of the swarm."""
    print("=" * 60)
    print("MAAT SWARM — Health Check")
    print("=" * 60)
    
    health = await health_check()
    for agent, status in health.items():
        emoji = "✅" if status["status"] == "ok" else "❌"
        print(f"  {emoji} {agent}: {status['tok_per_sec']} tok/s, "
              f"{status['tokens']} tokens, {status['elapsed_ms']}ms")
    
    print()
    print("=" * 60)
    print("MAAT SWARM — Fan Out Test")
    print("=" * 60)
    
    t0 = time.monotonic()
    results = await fan_out(
        "What is the best approach to build a multi-agent AI system "
        "for knowledge management? Consider local LLMs, memory systems, "
        "and governance frameworks.",
        timeout=30,
    )
    wall_time = int((time.monotonic() - t0) * 1000)
    
    total_tokens = 0
    for role, result in results.items():
        print(f"\n{'─' * 40}")
        print(f"🔹 {role.value.upper()} ({result.tokens} tok, "
              f"{result.tok_per_sec:.0f} tok/s, {result.elapsed_ms}ms)")
        print(f"{'─' * 40}")
        print(result.content[:500] + ("..." if len(result.content) > 500 else ""))
        total_tokens += result.tokens
    
    print(f"\n{'=' * 60}")
    print(f"Total: {total_tokens} tokens, wall time: {wall_time}ms")
    aggregate = sum(r.tok_per_sec for r in results.values())
    print(f"Aggregate throughput: {aggregate:.0f} tok/s")
    print("=" * 60)
    
    print()
    print("=" * 60)
    print("MAAT SWARM — Scout→Route Test")
    print("=" * 60)
    
    route_result = await scout_then_route(
        "What decisions have been made about the Maat compact model training?",
        timeout=30,
    )
    print(f"Pattern: {route_result['pattern']}")
    print(f"Scout: {route_result['scout'].content[:300]}...")
    if route_result.get("routed_to"):
        print(f"Routed: {route_result['routed_to'].content[:300]}...")


if __name__ == "__main__":
    asyncio.run(_main())
