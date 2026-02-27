from app.services.code_execution_service import run_code


async def evaluate_code(script: str, test_cases: list):

    results = []
    passed = 0

    for test in test_cases:

        execution = await run_code(
            script,
            stdin_input=test["input"]
        )

        output = execution["output"]

        success = output == test["output"]

        if success:
            passed += 1

        results.append({
            "input": test["input"],
            "expected": test["output"],
            "output": output,
            "passed": success
        })

    score = int((passed / len(test_cases)) * 10)

    return {
        "results": results,
        "passed": passed,
        "total": len(test_cases),
        "score": score
    }