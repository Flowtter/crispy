from api import app
from api.models.highlight import Highlight


@app.get("/highlight")
async def get_video() -> dict:
    if not (highlight := Highlight.find_one()):
        highlight = Highlight({"title": "My highlight"})
        highlight = highlight.save()
        return {"new": True, "highlight": highlight}
    return {"new": False, "highlight": highlight}
