from app.services.code_execution_service import run_code


async def evaluate_code(script: str, test_cases: list):

    results = []
    passed = 0

    for test in test_cases:

        execution = await run_code(
            script,
            stdin_input=test["input"]
        )

        output = execution.get("output", "").strip()
        error = execution.get("error", "").strip()
        status = execution.get("status", "failed")

        # ✅ if error exists → test automatically fails
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
            "error": error,          # ⭐ added
            "status": status,        # ⭐ added
            "passed": success
        })

    score = int((passed / len(test_cases)) * 10) if test_cases else 0

    return {
        "results": results,
        "passed": passed,
        "total": len(test_cases),
        "score": score
    }