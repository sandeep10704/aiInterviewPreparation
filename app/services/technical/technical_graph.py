import os
import asyncio
import random
from typing import TypedDict, List, Dict
from tavily import TavilyClient
from langgraph.graph import StateGraph
from app.services.llm.llm_core import llm
from app.schemas.technical.technical_schema import QuestionSet
from app.core.config import settings 

class GraphState(TypedDict):
    resume_data: dict
    topics: List[str]
    research_data: Dict[str, str]
    questions: List[dict]


tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)


# ---------- NODE 1 ----------
async def select_topics_node(state: GraphState):
    resume = state["resume_data"]

    pool = (
        resume.get("skills", []) +
        [p["project_name"] for p in resume.get("projects", [])] 
    )

    if not pool:
        raise ValueError("No topics found in resume")

    count = max(1, min(4, len(pool) // 2))
    topics = random.sample(pool, count)

    return {"topics": topics}


# ---------- NODE 2 ----------
async def tavily_research_node(state: GraphState):
    topics = state["topics"]

    async def fetch(topic):
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: tavily.search(query=topic, search_depth="basic")
        )

        content = " ".join(
            [r["content"] for r in result["results"][:2]]
        )

        return topic, content[:2000]  # limit tokens

    results = await asyncio.gather(*[fetch(t) for t in topics])

    return {"research_data": dict(results)}


# ---------- NODE 3 ----------
async def generate_questions_node(state: GraphState):
    topics = state["topics"]
    research = state["research_data"]

    research_text = ""
    for topic, content in research.items():
        research_text += f"\nTopic: {topic}\n{content}\n"

    structured_llm = llm.with_structured_output(QuestionSet)

    prompt = f"""
    Generate 10 technical interview Q&A.
    Cover multiple topics.
    Use research context below.

    Research:
    {research_text}
    """

    result = await structured_llm.ainvoke(prompt)

    return {"questions": [q.model_dump() for q in result.questions]}


# ---------- BUILD GRAPH ----------
builder = StateGraph(GraphState)

builder.add_node("select_topics", select_topics_node)
builder.add_node("research", tavily_research_node)
builder.add_node("generate_questions", generate_questions_node)

builder.set_entry_point("select_topics")

builder.add_edge("select_topics", "research")
builder.add_edge("research", "generate_questions")

builder.set_finish_point("generate_questions")

technical_graph = builder.compile()