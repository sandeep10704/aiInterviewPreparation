import json
from app.core.firebase import db
from app.services.coding.coding_interview_graph import coding_interview_graph
from app.services.coding.coding_service import explain_question


async def coding_ws_handler(websocket, user_id):

    state = {
        "started": False,
        "previous_code": "",
        "suggestions": []
    }

    try:
        while True:

            data = await websocket.receive_text()
            parsed = json.loads(data)

            event = parsed.get("type")
            coding_set_id = parsed.get("coding_set_id")
            question_no = parsed.get("question_no")

            # -----------------------------
            # LOAD QUESTION (SAFE)
            # -----------------------------

            if "question" not in state:

                if not coding_set_id:
                    await websocket.send_json({"error": "coding_set_id required"})
                    continue

                doc = db.collection("users") \
                    .document(user_id) \
                    .collection("coding_questions") \
                    .document(coding_set_id) \
                    .get()

                if not doc.exists:
                    await websocket.send_json({"error": "invalid coding_set"})
                    continue

                question = doc.to_dict()["questions"][question_no]

                state["question"] = question["problem_statement"]
                state["test_cases"] = question["test_cases"]

            # -----------------------------
            # FIRST EXPLANATION
            # -----------------------------

            if event == "start" and not state["started"]:

                explanation = await explain_question(state)

                await websocket.send_json({
                    "type": "explanation",
                    "message": explanation
                })

                state["started"] = True
                continue

            # -----------------------------
            # NORMAL FLOW
            # -----------------------------

            state["event"] = event
            state["force"] = event == "suggest"
            state["code"] = parsed.get("code", "")
            state["time"] = parsed.get("time")
            state["coding_set_id"] = coding_set_id
            state["question_no"] = question_no
            state["user_id"] = user_id
            try:
                result = await coding_interview_graph.ainvoke(state)
                state.update(result)

            except Exception as e:
                print("GRAPH ERROR:", e)

                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })

                continue

            if result.get("skip") and not state["force"]:
                continue

            await websocket.send_json({
                "type": "hint",
                "hint": result.get("hint"),
                "test_result": result.get("test_result")
            })

            state["previous_code"] = state["code"]

    except Exception as e:
        print("CODING WS CLOSED:", e)