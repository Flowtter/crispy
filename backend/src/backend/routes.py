import os

from typing import List, Any, Union, Dict
from fastapi import HTTPException
from fastapi.responses import FileResponse

from AI.network import NeuralNetwork
from utils.IO import io
from utils.constants import CUT, TMP_PATH, app, FRONTEND_PATH, IMAGES_PATH, NEURAL_NETWORK_PATH, IMAGE
import video.video as vid
from backend.json_handling import load_json, save_json, new_json
from backend.dto import Reorder

NN = NeuralNetwork([4000, 120, 15, 2], 0.01)
NN.load(NEURAL_NETWORK_PATH)

JSON_INFO = load_json()


@app.get("/")
def home() -> Dict[Any, Any]:
    return JSON_INFO


@app.get("/reload")
async def reload() -> Dict[Any, Any]:
    new_json()
    save_json(JSON_INFO)
    return JSON_INFO


@app.post("/reorder")
async def reorder(data: List[Reorder]) -> Dict[Any, Any]:
    objects = JSON_INFO["objects"]
    new_objects = []
    for datum in data:
        image = next(filter(lambda x: x["name"] == datum.name, objects), None)
        new_objects.append(image)
    JSON_INFO["objects"] = new_objects

    save_json(JSON_INFO)
    return JSON_INFO


@app.get("/objects/{filename}/image")
async def get_image(filename: str) -> FileResponse:
    return FileResponse(os.path.join(IMAGES_PATH, filename + ".jpg"))


@app.get("/objects/{filename}/video")
async def get_video(filename: str) -> FileResponse:
    return FileResponse(os.path.join(FRONTEND_PATH, filename + ".mp4"))


@app.get("/objects/{filename}/info")
async def get_image_info(
        filename: str) -> Union[Dict[Any, Any], HTTPException]:
    objects = JSON_INFO["objects"]
    image = next(filter(lambda x: x["name"] == filename, objects), None)

    if not image:
        return HTTPException(status_code=404, detail="Object not found")

    return image


@app.get("/objects/{filename}/switch")
async def switch(filename: str) -> Union[Dict[Any, Any], HTTPException]:
    objects = JSON_INFO["objects"]
    image = next(filter(lambda x: x["name"] == filename, objects), None)

    if not image:
        return HTTPException(status_code=404, detail="Object not found")

    index = objects.index(image)

    image["enabled"] = not image["enabled"]
    objects[index] = image

    JSON_INFO["objects"] = objects

    save_json(JSON_INFO)

    return image["enabled"]


# @app.get("/generate-cuts")
# async def generate_cuts() -> str:
#     objects = JSON_INFO["objects"]
#     for object in objects:
#         if object["enabled"]:
#             no_ext = object["name"]
#             images_path = os.path.join(TMP_PATH,
#                                        io.generate_clean_name(no_ext), IMAGE)
#             query_array = vid.get_query_array_from_video(NN, images_path)
#             kill_array = vid.get_kill_array_from_query_array(query_array)
#             kill_array = vid.post_processing_kill_array(kill_array)
#             vid.segment_video_with_kill_array(no_ext + ".mp4", kill_array)


@app.get("/objects/{filename}/generate-cuts")
async def single_video_generate_cuts(
        filename: str) -> Union[List[str], HTTPException]:
    objects = JSON_INFO["objects"]
    obj = next(filter(lambda x: x["name"] == filename, objects), None)

    if not obj:
        return HTTPException(status_code=404, detail="Object not found")

    if obj["enabled"]:
        no_ext = obj["name"]
        images_path = os.path.join(TMP_PATH, io.generate_clean_name(no_ext),
                                   IMAGE)
        query_array = vid.get_query_array_from_video(NN, images_path)
        kill_array = vid.get_kill_array_from_query_array(query_array)
        kill_array = vid.post_processing_kill_array(kill_array)
        vid.segment_video_with_kill_array(no_ext + ".mp4", kill_array)

        cut_path = os.path.join(TMP_PATH, io.generate_clean_name(no_ext), CUT)
        cuts = os.listdir(cut_path)
        cuts.sort()
        cuts = [io.remove_extension(cut) for cut in cuts]
        JSON_INFO["objects"][objects.index(obj)]["cuts"] = cuts

        save_json(JSON_INFO)

        return cuts
    return HTTPException(status_code=403)


@app.get("/send")
async def send() -> str:
    return "Not implemented"


@app.get("/status")
async def status() -> str:
    return "Not implemented"
