from typing import TypedDict, List
import random
import time

from langgraph.graph import StateGraph
from tavily import TavilyClient

from app.services.llm.llm_core import llm
from app.core.config import settings
from app.schemas.coding.coding_schema import CodingQuestionSet


tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)


# ---------- STATE ----------
class CodingGraphState(TypedDict):
    resume_data: dict
    tech_context: str
    research_data: str
    questions: List[dict]


# ---------- NODE 1 ----------
def extract_tech_context_node(state: CodingGraphState):

    start = time.time()
    print("\n========== NODE: extract_context ==========", flush=True)

    resume = state["resume_data"]
    print("Resume keys:", resume.keys(), flush=True)

    languages = [
        s for s in resume.get("skills", [])
        if s.lower() in ["python", "java", "c", "c++", "javascript", "php"]
    ]

    print("Detected Languages:", languages, flush=True)

    project_desc = "\n".join(
        [p.get("project_description", "") for p in resume.get("projects", [])]
    )

    print("Project description length:", len(project_desc), flush=True)

    context = f"""
Programming Languages:
{languages}

Project Descriptions:
{project_desc}
"""

    print(
        f"extract_context finished in {time.time()-start:.2f}s",
        flush=True
    )

    return {"tech_context": context}


# ---------- NODE 2 ----------
def research_node(state: CodingGraphState):

    start = time.time()
    print("\n========== NODE: research ==========", flush=True)

    topics = [
        "sliding window hard",
        "graph dfs bfs hard",
        "tree dp hard",
        "heap priority queue medium",
        "binary search tricky",
        "dynamic programming hard",
        "backtracking recursion hard",
        "two pointers tricky",
        "monotonic stack hard",
        "union find graph",
        "topological sort hard",
        "shortest path dijkstra",
        "segment tree range query",
        "interval merging tricky",
        "matrix bfs dfs"
    ]

    selected_topics = random.sample(topics, 3)
    print("Selected Topics:", selected_topics, flush=True)

    query = f"""
LeetCode style FAANG coding interview problems
{", ".join(selected_topics)}

Include:
- medium and hard
- tricky constraints
- DSA problems
- real interview questions
"""[:400]

    print("Calling Tavily...", flush=True)

    tavily_start = time.time()

    result = tavily.search(
        query=query,
        search_depth="advanced",
        max_results=5
    )

    print(
        f"Tavily finished in {time.time()-tavily_start:.2f}s",
        flush=True
    )

    research = " ".join(
        [r.get("content", "") for r in result.get("results", [])]
    )

    print("Research data length:", len(research), flush=True)

    print(
        f"research node finished in {time.time()-start:.2f}s",
        flush=True
    )

    return {"research_data": research}


# ---------- NODE 3 ----------
async def generate_questions_node(state: CodingGraphState):

    start = time.time()
    print("\n========== NODE: generate_questions ==========", flush=True)

    seed = random.randint(1, 100000)
    print("Random Seed:", seed, flush=True)

    structured_llm = llm.with_structured_output(CodingQuestionSet)

    prompt = f"""
Random Seed: {seed}

You are an expert FAANG interview problem designer.

IMPORTANT:
Generate REAL interview-level DSA problems.

TIME DIFFICULTY:
Medium → 35-50 minutes
Hard → 60-90 minutes

STRICT RULES:
- Problems must feel like real LeetCode interview questions
- Must require optimal solution
- Brute force must TLE
- Include tricky edge cases
- Use multiple data structures
- Problems must be ORIGINAL

DIVERSITY RULE:
The two questions MUST be from DIFFERENT topics.

Each problem MUST include:
- clear algorithmic problem statement
- python function signature
- input format
- output format
- constraints
- EXACTLY 6 deterministic test cases

NO solutions
NO hints

Candidate Tech Context:
{state["tech_context"][:500]}

Research Context:
{state["research_data"][:500]}

Generate EXACTLY:
1 Medium DSA problem
1 Hard DSA problem

DO NOT generate known LeetCode problems.
DO NOT generate:
- connect sticks
- three subarrays
- two sum
- merge intervals
- longest substring

Create NEW unseen problems.
Never repeat previous problem patterns:
- subarray sum
- sorting swaps
- greedy merging
- heap merging

Use new topic each time.
"""

    print("Prompt length:", len(prompt), flush=True)
    print("Calling LLM...", flush=True)

    llm_start = time.time()

    result = await structured_llm.ainvoke(prompt)

    print(
        f"LLM finished in {time.time()-llm_start:.2f}s",
        flush=True
    )

    questions = [q.model_dump() for q in result.questions]

    print("Generated Questions Count:", len(questions), flush=True)

    for i, q in enumerate(questions):
        print(
            f"Question {i+1}: {q.get('title','No title')}",
            flush=True
        )

    print(
        f"generate_questions finished in {time.time()-start:.2f}s",
        flush=True
    )

    return {
        "questions": questions
    }


# ---------- GRAPH ----------
builder = StateGraph(CodingGraphState)

builder.add_node("extract_context", extract_tech_context_node)
builder.add_node("research", research_node)
builder.add_node("generate_questions", generate_questions_node)

builder.set_entry_point("extract_context")

builder.add_edge("extract_context", "research")
builder.add_edge("research", "generate_questions")

builder.set_finish_point("generate_questions")

coding_graph = builder.compile()