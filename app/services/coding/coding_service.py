import uuid
import time
import sys
from datetime import datetime

from app.core.firebase import db
from app.services.coding.coding_graph import coding_graph
from app.services.coding.coding_evaluation_service import evaluate_code
from app.services.llm.llm_core import llm


# =========================
# GENERATE CODING SET
# =========================
async def generate_coding_set(user_id: str):

    sys.stdout.write("\n========== generate_coding_set START ==========\n")
    sys.stdout.flush()

    total_start = time.time()

    # -------------------------
    sys.stdout.write("Fetching user...\n")
    sys.stdout.flush()

    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise ValueError("User not found")

    sys.stdout.write("User found\n")
    sys.stdout.flush()

    # -------------------------
    resume_data = user_doc.to_dict().get("resume_data")

    if not resume_data:
        raise ValueError("Resume missing")

    sys.stdout.write("Resume loaded\n")
    sys.stdout.flush()

    # -------------------------
    sys.stdout.write("Calling coding_graph...\n")
    sys.stdout.flush()

    graph_start = time.time()

    result = await coding_graph.ainvoke(
        {
            "resume_data": resume_data
        }
    )

    sys.stdout.write(
        f"coding_graph finished in {time.time()-graph_start:.2f}s\n"
    )
    sys.stdout.flush()

    # -------------------------
    coding_set_id = str(uuid.uuid4())
    questions = result["questions"]

    sys.stdout.write(f"Questions generated: {len(questions)}\n")
    sys.stdout.flush()

    # -------------------------
    sys.stdout.write("Saving to Firestore...\n")
    sys.stdout.flush()

    user_ref.collection("coding_questions") \
        .document(coding_set_id) \
        .set({
            "coding_set_id": coding_set_id,
            "questions": questions,
            "answers": {},
            "status": "pending",
            "created_at": datetime.utcnow()
        })

    sys.stdout.write("Saved successfully\n")
    sys.stdout.flush()

    sys.stdout.write(
        f"TOTAL TIME: {time.time()-total_start:.2f}s\n"
    )
    sys.stdout.flush()

    return coding_set_id, questions


# =========================
# SUBMIT SOLUTION
# =========================
async def submit_coding_solution(
    user_id: str,
    coding_set_id: str,
    question_index: int,
    code: str,
    language: str = "python"
):

    sys.stdout.write("\n========== submit_coding_solution ==========\n")
    sys.stdout.flush()

    doc_ref = db.collection("users") \
        .document(user_id) \
        .collection("coding_questions") \
        .document(coding_set_id)

    doc = doc_ref.get()

    if not doc.exists:
        raise ValueError("Coding set not found")

    data = doc.to_dict()
    question = data["questions"][question_index]

    sys.stdout.write("Running evaluation...\n")
    sys.stdout.flush()

    start = time.time()

    evaluation = await evaluate_code(
        code,
        question["test_cases"],
        language
    )

    sys.stdout.write(
        f"Evaluation finished in {time.time()-start:.2f}s\n"
    )
    sys.stdout.flush()

    doc_ref.update({
        f"submissions.q{question_index}": {
            "code": code,
            "evaluation": evaluation,
            "submitted_at": datetime.utcnow()
        }
    })

    sys.stdout.write("Submission saved\n")
    sys.stdout.flush()

    return evaluation


# =========================
# EXPLAIN QUESTION
# =========================
async def explain_question(state):

    sys.stdout.write("Explain question called\n")
    sys.stdout.flush()

    prompt = f"""
You are coding interviewer.

Explain problem to candidate.

Question:
{state["question"]}

Rules:
- explain clearly
- mention input output
- mention constraints
- do not give solution
- friendly interviewer tone
"""

    response = llm.chat([
        {"role": "user", "content": prompt}
    ])

    return response.content


# =========================
# TYPING HINT
# =========================
async def generate_typing_hint(state):

    sys.stdout.write("Typing hint called\n")
    sys.stdout.flush()

    prompt = f"""
You are coding interviewer watching typing.

Question:
{state["question"]}

Candidate code:
{state["code"]}

Previous code:
{state.get("previous_code")}

Rules:
- give hint only if needed
- otherwise return SILENT
- do not give solution
- short hint
"""

    res = llm.chat([
        {"role": "user", "content": prompt}
    ])

    return res.content.strip()


# =========================
# RUN HINT
# =========================
async def generate_run_hint(state):

    sys.stdout.write("Run hint called\n")
    sys.stdout.flush()

    prompt = f"""
Code execution finished.

Results:
{state["test_result"]}

Candidate code:
{state["code"]}

Give interviewer hint.
Do not give solution.
"""

    res = llm.chat([
        {"role": "user", "content": prompt}
    ])

    return res.content


# =========================
# GET CODING SETS
# =========================
async def get_coding_sets(user_id: str):

    sys.stdout.write("Fetching coding sets\n")
    sys.stdout.flush()

    docs = db.collection("users") \
        .document(user_id) \
        .collection("coding_questions") \
        .stream()

    result = []

    for doc in docs:
        data = doc.to_dict()

        result.append({
            "coding_set_id": data["coding_set_id"],
            "status": data.get("status"),
            "created_at": data.get("created_at")
        })

    return result


# =========================
# GET QUESTIONS
# =========================
async def get_coding_set_questions(user_id: str, coding_set_id: str):

    sys.stdout.write("Fetching questions\n")
    sys.stdout.flush()

    doc = db.collection("users") \
        .document(user_id) \
        .collection("coding_questions") \
        .document(coding_set_id) \
        .get()

    if not doc.exists:
        raise ValueError("Coding set not found")

    data = doc.to_dict()
    questions = data["questions"]

    for q in questions:
        q["test_cases"] = q.get("test_cases", [])[:3]

    return {
        "coding_set_id": coding_set_id,
        "questions": questions
    }