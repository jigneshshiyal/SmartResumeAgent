from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from agent import resume_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        async for message in websocket.iter_text():
            try:
                word = ""
                async for event in resume_agent.astream_events(
                    {"messages": ("user", message)},
                    config={"configurable": {"thread_id": 1}},
                    version="v1",
                ):
                    kind = event["event"]

                    if kind == "on_chat_model_stream":
                        token = event["data"]["chunk"].content
                        if token:
                            if token.startswith(" "):
                                if word:
                                    await websocket.send_text(word)
                                word = token
                            else:
                                word += token
                # Send the final partial message if any
                if word:
                    await websocket.send_text(word)
            except Exception as e:
                await websocket.send_text(f"Error: {e}")
    except Exception as e:
        await websocket.send_text(f"Error: {e}")




# ---------------- Run ----------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000)
