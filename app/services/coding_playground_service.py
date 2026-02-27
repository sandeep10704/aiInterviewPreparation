from app.services.code_execution_service import run_code


async def run_playground_code(
    code: str,
    language: str,
    stdin: str
):

    result = await run_code(
        script=code,
        stdin_input=stdin,
        language=language
    )

    return {
        "language": language,
        "input": stdin,
        "output": result.get("output")
    }