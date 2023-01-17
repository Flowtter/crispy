from api import app
from api.models.highlight import Highlight


@app.get("/highlight")
async def get_video() -> dict:
    if not (highlight := await Highlight.find_one()):
        highlight = Highlight({"title": "My highlight"})
        highlight = await highlight.save()
        return {"new": True, "highlight": highlight}
    return {"new": False, "highlight": highlight}
