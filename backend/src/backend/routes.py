import os
import json

from typing import List, Any, Tuple, Union, Dict

from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.encoders import jsonable_encoder

from AI.network import NeuralNetwork
from utils.IO import io
from utils.constants import CUT, MUSICS_PATH, SETTINGS_PATH, TMP_PATH, VIDEOS_PATH, app, FRONTEND_PATH, IMAGES_PATH, NEURAL_NETWORK_PATH, IMAGE
import video.video as vid
from backend.json_handling import load_json, save_json, new_json
from backend.dto import Filters, Reorder
from backend.startup import extract_first_image_of_video

NN = NeuralNetwork([4000, 120, 15, 2], 0.01)
NN.load(NEURAL_NETWORK_PATH)

JSON_INFO = load_json()

# FIXME: rename image in obj


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


# FIXME: The next four functions could use a query parameter
# To avoid code duplication
@app.get("/objects/{filename}/info")
async def get_object_info(
        filename: str) -> Union[Dict[Any, Any], HTTPException]:
    objects = JSON_INFO["objects"]
    image = next(filter(lambda x: x["name"] == filename, objects), None)

    if not image:
        return HTTPException(status_code=404, detail="Object not found")

    return image


@app.get("/objects/{filename}/{cut}/info")
async def get_cut_info(filename: str,
                       cut: str) -> Union[Dict[Any, Any], HTTPException]:
    objects = JSON_INFO["objects"]
    image = next(filter(lambda x: x["name"] == filename, objects), None)

    if not image:
        return HTTPException(status_code=404, detail="Object not found")
    cut = next(filter(lambda x: x[0] == cut, image["cuts"]), None)

    if not cut:
        return HTTPException(status_code=404, detail="Cut not found")

    return {"enabled": cut[1]}


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


@app.get("/objects/{filename}/{cut}/switch")
async def switch_cut(filename: str,
                     cut: str) -> Union[Dict[Any, Any], HTTPException]:
    objects = JSON_INFO["objects"]
    image = next(filter(lambda x: x["name"] == filename, objects), None)

    if not image:
        return HTTPException(status_code=404, detail="Object not found")

    found_cut = next(filter(lambda x: x[0] == cut, image["cuts"]), None)

    if not found_cut:
        return HTTPException(status_code=404, detail="Cut not found")

    index = objects.index(image)
    objects[index] = image

    c = image["cuts"].index(found_cut)
    image["cuts"][c] = (image["cuts"][c][0], not image["cuts"][c][1])
    objects[index] = image

    JSON_INFO["objects"] = objects

    save_json(JSON_INFO)

    return image["enabled"]


def convert_filters(name: str) -> Dict[Any, Any]:
    objects = JSON_INFO["objects"]
    obj = next(filter(lambda x: x["name"] == name, objects), None)
    if not obj:
        return {}
    result: Dict[Any, Any] = {name: {}}
    for f in obj["filters"]:
        if not obj["filters"][f]["box"]:
            continue
        if f == "scale":
            result[name][f] = "w=" + str(int(
                obj["filters"][f]["w"])) + ":h=" + str(
                    int(obj["filters"][f]["h"]))
        elif "value" in obj["filters"][f]:
            result[name][f] = obj["filters"][f]["value"]
        else:
            result[name][f] = True
    return result


def convert_session_to_settings() -> None:
    videos = os.listdir(VIDEOS_PATH)
    videos.sort()
    filters = {}
    for video in videos:
        if video.endswith(".mp4"):
            no_ext = io.remove_extension(video)
            filt = convert_filters(no_ext)
            if filt[no_ext]:
                filters[no_ext] = filt[no_ext]

    with open(SETTINGS_PATH, "r") as f:
        settings = json.load(f)

    settings["clips"] = filters

    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=4)


@app.get("/objects/{filename}/generate-cuts")
async def single_video_generate_cuts(
        filename: str) -> Union[List[Tuple[Any, bool]], HTTPException]:
    convert_session_to_settings()
    objects = JSON_INFO["objects"]
    obj = next(filter(lambda x: x["name"] == filename, objects), None)

    if not obj:
        return HTTPException(status_code=404, detail="Object not found")

    if obj["enabled"]:
        no_ext = obj["name"]
        images_path = os.path.join(TMP_PATH, io.generate_clean_name(no_ext),
                                   IMAGE)
        # DEBUG
        c = os.path.join(TMP_PATH, io.generate_clean_name(no_ext), CUT)
        if len(os.listdir(c)) == 0:
            query_array = vid.get_query_array_from_video(NN, images_path)
            kill_array = vid.get_kill_array_from_query_array(query_array)
            kill_array = vid.post_processing_kill_array(kill_array)
            vid.segment_video_with_kill_array(no_ext + ".mp4", kill_array)

        cut_path = os.path.join(TMP_PATH, io.generate_clean_name(no_ext), CUT)
        cuts = os.listdir(cut_path)
        cuts.sort()
        cuts = [(io.remove_extension(cut), True) for cut in cuts]
        JSON_INFO["objects"][objects.index(obj)]["cuts"] = cuts

        save_json(JSON_INFO)

        return cuts
    return HTTPException(status_code=403)


@app.get("/objects/{filename}/{cut}")
def get_cut(filename: str, cut: str) -> FileResponse:
    return FileResponse(
        os.path.join(TMP_PATH, io.generate_clean_name(filename), CUT,
                     cut + ".mp4"))


@app.get("/generate-result")
async def generate_result() -> None:
    clips = []
    for obj in JSON_INFO["objects"]:
        if obj["enabled"]:
            clips.append(obj)

    cuts = []
    for obj in clips:
        for cut in obj["cuts"]:
            if cut[1]:
                cn = io.generate_clean_name(obj["name"])
                cuts.append(os.path.join(TMP_PATH, cn, CUT, cut[0] + ".mp4"))

    print(cuts)
    vid.merge_cuts_with_files(cuts)
    if os.path.exists("merged.jpg"):
        os.remove("merged.jpg")
    extract_first_image_of_video("merged.mp4", "merged")
    print("Done")


@app.get("/result/video")
def get_result_video() -> FileResponse:
    return FileResponse("merged.mp4")


@app.get("/result/image")
def get_result_image() -> FileResponse:
    return FileResponse("merged.jpg")


@app.get("/musics/{filename}")
async def get_music(filename: str) -> FileResponse:
    return FileResponse(os.path.join(MUSICS_PATH, filename + ".mp3"))


# TODO: Refactor next two functions
@app.get("/musics/{filename}/switch")
async def switch_music(filename: str) -> Union[Dict[Any, Any], HTTPException]:
    musics = JSON_INFO["musics"]
    image = next(filter(lambda x: x["name"] == filename, musics), None)

    if not image:
        return HTTPException(status_code=404, detail="Object not found")

    index = musics.index(image)

    image["enabled"] = not image["enabled"]
    musics[index] = image

    JSON_INFO["musics"] = musics

    save_json(JSON_INFO)

    return image["enabled"]


@app.post("/musics/reorder")
async def music_reorder(data: List[Reorder]) -> Dict[Any, Any]:
    musics = JSON_INFO["musics"]
    new_musics = []
    for datum in data:
        music = next(filter(lambda x: x["name"] == datum.name, musics), None)
        new_musics.append(music)
    JSON_INFO["musics"] = new_musics

    save_json(JSON_INFO)
    return JSON_INFO


@app.get("/objects/filters/{filename}/read")
def filters_read(filename: str) -> Union[Dict[Any, Any], HTTPException]:
    objects = JSON_INFO["objects"]
    obj = next(filter(lambda x: x["name"] == filename, objects), None)
    if not obj:
        return HTTPException(status_code=404, detail="Object not found")

    return obj["filters"]


@app.post("/objects/filters/{filename}/save")
def filters_save(data: Filters,
                 filename: str) -> Union[Dict[Any, Any], HTTPException]:
    objects = JSON_INFO["objects"]
    obj = next(filter(lambda x: x["name"] == filename, objects), None)
    if not obj:
        return HTTPException(status_code=404, detail="Object not found")

    obj["refresh"] = True
    obj["filters"] = jsonable_encoder(data)
    JSON_INFO["objects"] = objects
    save_json(JSON_INFO)

    return obj["filters"]


@app.get("/objects/filters/{filename}/update")
def update(filename: str) -> Union[bool, HTTPException]:
    objects = JSON_INFO["objects"]
    obj = next(filter(lambda x: x["name"] == filename, objects), None)
    if not obj:
        return HTTPException(status_code=404, detail="Object not found")
    if "refresh" in obj:
        save = obj["refresh"]
    else:
        save = False
    obj["refresh"] = False
    JSON_INFO["objects"] = objects
    save_json(JSON_INFO)

    return save
