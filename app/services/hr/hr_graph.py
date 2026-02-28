import random
from typing import TypedDict, List, Dict

from langgraph.graph import StateGraph
from app.services.llm.llm_core import llm
from app.schemas.hr.hr_schema import HRQuestionSet

class HRGraphState(TypedDict):
    role: str
    company: str
    resume_data: Dict
    resume_context: str
    topics: List[str]
    questions: List[dict]

async def extract_resume_context_node(state: HRGraphState):

    resume = state["resume_data"]

    work_exp = resume.get("work_experience", [])
    achievements = resume.get("achievements", [])
    projects = resume.get("projects", [])

    context = "Candidate Background:\n"

    if work_exp:
        context += "\nWork Experience:\n"
        for w in work_exp:
            context += f"- {w.get('role')} at {w.get('company')}\n"

    if projects:
        context += "\nProjects:\n"
        for p in projects:
            context += f"- {p.get('project_name')}\n"

    if achievements:
        context += "\nAchievements:\n"
        for a in achievements:
            context += f"- {a}\n"

    return {"resume_context": context}

import random

async def select_hr_topics_node(state: HRGraphState):

    base_topics = [
        "leadership",
        "teamwork",
        "conflict resolution",
        "career goals",
        "strengths and weaknesses",
        "problem solving",
        "time management",
        "communication"
    ]

    resume = state["resume_data"]

    # Add dynamic topics
    if resume.get("work_experience"):
        base_topics.append("professional challenges")

    if resume.get("achievements"):
        base_topics.append("success stories")

    topics = random.sample(base_topics, 5)

    return {"topics": topics}


async def generate_hr_questions_node(state: HRGraphState):

    role = state["role"]
    company = state["company"]
    topics = state["topics"]
    resume_context = state["resume_context"]

    topics_text = "\n".join(topics)

    structured_llm = llm.with_structured_output(HRQuestionSet)

    prompt = f"""
    Generate 10 personalized HR interview questions with ideal answers.

    Target Role: {role}
    Company: {company}

    Candidate Resume:
    {resume_context}

    Focus Topics:
    {topics_text}

    Rules:
    - Ask behavioral and situational questions
    - Refer candidate background naturally
    - Include achievement-based questions
    - Include work experience discussion
    - Professional HR tone
    """

    result = await structured_llm.ainvoke(prompt)

    return {
        "questions": [q.model_dump() for q in result.questions]
    }

builder = StateGraph(HRGraphState)

builder.add_node("extract_resume", extract_resume_context_node)
builder.add_node("select_topics", select_hr_topics_node)
builder.add_node("generate_questions", generate_hr_questions_node)

builder.set_entry_point("extract_resume")

builder.add_edge("extract_resume", "select_topics")
builder.add_edge("select_topics", "generate_questions")

builder.set_finish_point("generate_questions")

hr_graph = builder.compile()