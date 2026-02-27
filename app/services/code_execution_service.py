import httpx

CODE_RUNNER_URL = "https://code-runner-ujh8.onrender.com/execute"


async def run_code(script: str, stdin_input: str = "", language: str = "python"):

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            CODE_RUNNER_URL,
            json={
                "language": language,
                "code": script,
                "stdin": stdin_input
            }
        )

    if response.status_code != 200:
        return {
            "status": "error",
            "output": response.text
        }

    result = response.json()

    return {
        "status": "success",
        "output": result.get("stdout", "").strip()
    }