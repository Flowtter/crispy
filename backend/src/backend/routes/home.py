from typing import Any, Dict

from utils.constants import app
from backend.json_handling import get_session_json, new_json


@app.get("/")
def home() -> Dict[Any, Any]:
    return get_session_json()


@app.get("/reload")
async def reload() -> Dict[Any, Any]:
    new_json()
    return get_session_json()
