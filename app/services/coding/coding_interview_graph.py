from typing import TypedDict
from langgraph.graph import StateGraph, END

from app.services.coding.coding_service import generate_typing_hint
from app.services.coding.coding_service import generate_run_hint
from app.services.coding.coding_runner_service import run_user_code_preview


class CodingInterviewState(TypedDict):
    question: str
    test_cases: list
    code: str
    previous_code: str
    event: str
    hint: str
    skip: bool
    test_result: dict
    force: bool

    user_id: str
    coding_set_id: str
    question_no: int


# ----------------------------
# ROUTER
# ----------------------------

async def router(state):

    if state["event"] == "run":
        return "run_node"

    if state["event"] == "suggest":
        return "force_hint"

    return "typing_decision"


# ----------------------------
# TYPING DECISION
# ----------------------------

async def typing_decision(state):

    prev = state.get("previous_code", "")
    curr = state["code"]

    if abs(len(curr) - len(prev)) < 8:
        state["skip"] = True
        return state

    state["skip"] = False
    return state


# ----------------------------
# TYPING HINT
# ----------------------------

async def typing_hint(state):

    if state.get("skip"):
        return state

    hint = await generate_typing_hint(state)

    if hint == "SILENT":
        state["skip"] = True
        return state

    state["hint"] = hint
    return state


# ----------------------------
# FORCE HINT
# ----------------------------

async def force_hint(state):

    hint = await generate_typing_hint(state)

    state["hint"] = hint
    state["skip"] = False

    return state


# ----------------------------
# RUN NODE
# ----------------------------

async def run_node(state):

    result = await run_user_code_preview(
        user_id=state["user_id"],
        coding_set_id=state["coding_set_id"],
        question_no=state["question_no"],
        code=state["code"],
        language="python"
    )

    state["test_result"] = result
    return state


# ----------------------------
# RUN HINT
# ----------------------------

async def run_hint(state):

    hint = await generate_run_hint(state)

    state["hint"] = hint
    return state


# ----------------------------
# GRAPH
# ----------------------------

builder = StateGraph(CodingInterviewState)

builder.add_node("typing_decision", typing_decision)
builder.add_node("typing_hint", typing_hint)
builder.add_node("force_hint", force_hint)
builder.add_node("run_node", run_node)
builder.add_node("run_hint", run_hint)

# conditional entry
builder.set_conditional_entry_point(router)

# typing flow
builder.add_edge("typing_decision", "typing_hint")
builder.add_edge("typing_hint", END)

# force flow
builder.add_edge("force_hint", END)

# run flow
builder.add_edge("run_node", "run_hint")
builder.add_edge("run_hint", END)

coding_interview_graph = builder.compile()