from typing import TypedDict, List
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

    resume = state["resume_data"]

    languages = [
        s for s in resume.get("skills", [])
        if s.lower() in ["python", "java", "c", "c++", "javascript", "php"]
    ]

    project_desc = "\n".join(
        [p.get("project_description", "") for p in resume.get("projects", [])]
    )

    context = f"""
Programming Languages:
{languages}

Project Descriptions:
{project_desc}
"""

    return {"tech_context": context}


# ---------- NODE 2 ----------
def research_node(state: CodingGraphState):

    resume = state["resume_data"]

    languages = [
        s for s in resume.get("skills", [])
        if s.lower() in ["python", "java", "c", "c++", "javascript", "php"]
    ]

    project_titles = [
        p.get("project_name", "")
        for p in resume.get("projects", [])
    ]

    query = f"""
Coding interview questions medium and hard level
for {', '.join(languages[:3])}
related to {', '.join(project_titles[:2])}
"""[:380]

    result = tavily.search(
        query=query,
        search_depth="basic",
        max_results=3
    )

    research = " ".join(
        [r.get("content", "") for r in result.get("results", [])]
    )

    return {"research_data": research}


# ---------- NODE 3 ----------
async def generate_questions_node(state: CodingGraphState):

    structured_llm = llm.with_structured_output(CodingQuestionSet)

    prompt = f"""
You are an expert FAANG interview problem designer.

IMPORTANT:
Generate REAL interview-level DSA problems.
DO NOT generate sample, example, tutorial, or practice explanations.

STRICT RULES:
- Problems must feel like real LeetCode interview questions.
- Each problem must be ORIGINAL and self-contained.
- DO NOT say "example problem", "sample problem", or "for practice".
- DO NOT include explanations about how to solve.
- DO NOT include hints or solutions.
- Output must look like an actual coding assessment question.

Generate EXACTLY:
1 Medium DSA problem
1 Hard DSA problem

Allowed DSA Topics ONLY:
Arrays, Strings, Hashing, Two Pointers, Sliding Window,
Stack, Queue, Linked List, Trees, BST,
Graphs (BFS/DFS), Greedy,
Dynamic Programming,
Binary Search,
Heap / Priority Queue,
Backtracking, Recursion.

NOT ALLOWED:
- Web/backend problems
- ML problems
- Theory questions
- System design
- Concept explanations

Each problem MUST include:
- clear algorithmic problem statement
- python function signature
- input format
- output format
- constraints
- EXACTLY 6 deterministic test cases
- edge cases included

NO solutions.
NO reasoning.
NO tutorial text.

Candidate Tech Context:
{state["tech_context"]}

Research Context:
{state["research_data"]}
"""

    result = await structured_llm.ainvoke(prompt)

    return {
        "questions": [q.model_dump() for q in result.questions]
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