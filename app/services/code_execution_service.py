import httpx

CODE_RUNNER_URL = "https://code-runner-ujh8.onrender.com/execute"


async def run_code(script: str, stdin_input: str = "", language: str = "python"):

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                CODE_RUNNER_URL,
                json={
                    "language": language,
                    "code": script,
                    "stdin": stdin_input
                }
            )

        # Server error
        if response.status_code != 200:
            return {
                "status": "error",
                "output": "",
                "error": response.text,
                "exit_code": None
            }

        result = response.json()

        stdout = result.get("stdout", "")
        stderr = result.get("stderr", "")
        exit_code = result.get("exit_code", 1)

        return {
            "status": "success" if exit_code == 0 else "failed",
            "output": stdout.strip(),
            "error": stderr.strip(),
            "exit_code": exit_code
        }

    # ✅ Network / timeout errors
    except httpx.RequestError as e:
        return {
            "status": "error",
            "output": "",
            "error": f"Code runner connection failed: {str(e)}",
            "exit_code": None
        }

    # ✅ Unexpected crash protection
    except Exception as e:
        return {
            "status": "error",
            "output": "",
            "error": f"Internal execution error: {str(e)}",
            "exit_code": None
        }