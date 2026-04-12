import uuid
from datetime import datetime
from app.core.firebase import db
from app.services.coding.coding_graph import coding_graph
from app.services.coding.coding_evaluation_service import evaluate_code
from app.services.llm.llm_core import llm
async def generate_coding_set(user_id: str):

    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        raise ValueError("User not found")

    resume_data = user_doc.to_dict().get("resume_data")

    if not resume_data:
        raise ValueError("Resume missing")

    result = await coding_graph.ainvoke({
        "resume_data": resume_data
    })

    coding_set_id = str(uuid.uuid4())
    questions = result["questions"]

    user_ref.collection("coding_questions") \
        .document(coding_set_id) \
        .set({
            "coding_set_id": coding_set_id,
            "questions": questions,
            "answers": {},
            "status": "pending",
            "created_at": datetime.utcnow()
        })

    return coding_set_id, questions

async def submit_coding_solution(
    user_id: str,
    coding_set_id: str,
    question_index: int,
    code: str
):

    doc_ref = db.collection("users") \
        .document(user_id) \
        .collection("coding_questions") \
        .document(coding_set_id)

    doc = doc_ref.get()

    if not doc.exists:
        raise ValueError("Coding set not found")

    data = doc.to_dict()
    question = data["questions"][question_index]

    evaluation = await evaluate_code(
        code,
        question["test_cases"]
    )

    doc_ref.update({
        f"submissions.q{question_index}": {
            "code": code,
            "evaluation": evaluation,
            "submitted_at": datetime.utcnow()
        }
    })

    return evaluation







async def explain_question(state):

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


async def generate_typing_hint(state):

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


async def generate_run_hint(state):

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





async def get_coding_sets(user_id: str):

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



async def get_coding_set_questions(user_id: str, coding_set_id: str):

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

    doc = db.collection("users") \
        .document(user_id) \
        .collection("coding_questions") \
        .document(coding_set_id) \
        .get()

    if not doc.exists:
        raise ValueError("Coding set not found")

    data = doc.to_dict()

    questions = data["questions"]

    # return only first 3 test cases
    formatted_questions = []

    for q in questions:
        formatted_questions.append({
            "question": q["question"],
            "function_signature": q.get("function_signature"),
            "examples": q.get("examples"),
            "constraints": q.get("constraints"),
            "test_cases": q["test_cases"][:3]
        })

    return {
        "coding_set_id": coding_set_id,
        "questions": formatted_questions
    }