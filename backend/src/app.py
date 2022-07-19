import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from utils.constants import app, VIDEOS_PATH

# FIXME: Refactor most of this code
# Most routes are poorly named and not very descriptive

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home() -> None:
    print(VIDEOS_PATH)


if __name__ == "__main__":
    uvicorn.run("app:app",
                host="127.0.0.1",
                port=5001,
                log_level="info",
                reload=True)
