from fastapi import HTTPException
from app.core.firebase import db
from app.services.coding.code_execution_service import run_code


async def run_user_code_preview(
    user_id: str,
    coding_set_id: str,
    question_no: int,
    code: str,
    language: str = "python"
):

    # ---------- GET USER CODING SET ----------
    doc_ref = db.collection("users") \
        .document(user_id) \
        .collection("coding_questions") \
        .document(coding_set_id)

    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(404, "Coding set not found")

    data = doc.to_dict()

    questions = data.get("questions", [])

    # handle dict/list structure safely
    if isinstance(questions, dict):
        questions = list(questions.values())

    if question_no >= len(questions):
        raise HTTPException(404, "Question not found")

    question = questions[question_no]
    test_cases = question.get("test_cases", [])

    # ---------- RUN FIRST 3 TEST CASES ----------
    results = []
    passed = 0

    for test in test_cases[:3]:

        execution = await run_code(
            code,
            stdin_input=test["input"],
            language=language
        )

        output = execution.get("output", "").strip()
        error = execution.get("error", "").strip()
        status = execution.get("status", "failed")

        # ✅ if error exists → auto fail
        if error:
            success = False
        else:
            success = output == test["output"].strip()

        if success:
            passed += 1

        results.append({
            "input": test["input"],
            "expected": test["output"],
            "output": output,
            "error": error,        # ⭐ added
            "status": status,      # ⭐ added
            "passed": success
        })

        # ⭐ OPTIONAL: stop early on compile error
        if error and status != "success":
            break

    return {
        "question_no": question_no,
        "executed_cases": len(results),
        "passed": passed,
        "results": results
    }