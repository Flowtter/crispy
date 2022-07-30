import os
import json

from typing import List, Any, Tuple, Union, Dict

from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.encoders import jsonable_encoder

from AI.network import NeuralNetwork
from utils.IO import io
from utils.constants import CUT, FILTERS_PATH, MUSICS_PATH, TMP_PATH, VIDEOS_PATH, app, FRONTEND_PATH, IMAGES_PATH, NEURAL_NETWORK_PATH, IMAGE
import video.video as vid
from backend.json_handling import load_json, save_json, new_json
from backend.dto import Filters, Reorder
from backend.startup import extract_first_image_of_video

# FIXME: routes are taking too long
# Should instead create a job in the bg
# and ping it till it ends instead of
# blocking the backend
# But since ffmpeg uses 100% of the cpu
# This might not be possible
# We should then create a thread handling ffmpeg
# and allocate only a fraction of the cpu's power

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
        obj = next(filter(lambda x: x["name"] == datum.name, objects), None)
        new_objects.append(obj)
    JSON_INFO["objects"] = new_objects

    with open(os.path.join(TMP_PATH, "recompile.json"), "w") as f:
        f.write("{}")

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
    obj = next(filter(lambda x: x["name"] == filename, objects), None)

    if not obj:
        return HTTPException(status_code=404, detail="Object not found")

    return obj


@app.get("/objects/{filename}/{cut}/info")
async def get_cut_info(filename: str,
                       cut: str) -> Union[Dict[Any, Any], HTTPException]:
    objects = JSON_INFO["objects"]
    obj = next(filter(lambda x: x["name"] == filename, objects), None)

    if not obj:
        return HTTPException(status_code=404, detail="Object not found")
    cut = next(filter(lambda x: x[0] == cut, obj["cuts"]), None)

    if not cut:
        return HTTPException(status_code=404, detail="Cut not found")

    return {"enabled": cut[1]}


@app.get("/objects/{filename}/switch")
async def switch(filename: str) -> Union[Dict[Any, Any], HTTPException]:
    objects = JSON_INFO["objects"]
    obj = next(filter(lambda x: x["name"] == filename, objects), None)

    if not obj:
        return HTTPException(status_code=404, detail="Object not found")

    index = objects.index(obj)

    obj["enabled"] = not obj["enabled"]
    objects[index] = obj

    JSON_INFO["objects"] = objects

    save_json(JSON_INFO)

    return obj["enabled"]


@app.get("/objects/{filename}/{cut}/switch")
async def switch_cut(filename: str,
                     cut: str) -> Union[Dict[Any, Any], HTTPException]:
    objects = JSON_INFO["objects"]
    obj = next(filter(lambda x: x["name"] == filename, objects), None)

    if not obj:
        return HTTPException(status_code=404, detail="Object not found")

    found_cut = next(filter(lambda x: x[0] == cut, obj["cuts"]), None)

    if not found_cut:
        return HTTPException(status_code=404, detail="Cut not found")

    index = objects.index(obj)
    objects[index] = obj

    c = obj["cuts"].index(found_cut)
    obj["cuts"][c] = (obj["cuts"][c][0], not obj["cuts"][c][1])
    objects[index] = obj

    JSON_INFO["objects"] = objects

    save_json(JSON_INFO)

    return obj["enabled"]


# TODO: Merge two next functions
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


def convert_global_filters() -> Dict[Any, Any]:
    obj = JSON_INFO

    result: Dict[Any, Any] = {"filters": {}}
    for f in obj["filters"]:
        if not obj["filters"][f]["box"]:
            continue
        if f == "scale":
            result["filters"][f] = "w=" + str(int(
                obj["filters"][f]["w"])) + ":h=" + str(
                    int(obj["filters"][f]["h"]))
        elif "value" in obj["filters"][f]:
            result["filters"][f] = obj["filters"][f]["value"]
        else:
            result["filters"][f] = True
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

    final_filters = {}

    final_filters["filters"] = convert_global_filters()["filters"]

    final_filters["clips"] = filters
    with open(FILTERS_PATH, "w") as f:
        json.dump(final_filters, f, indent=4)


#FIXME: bad usage of a "thread lock"
GENERATING = False


@app.get("/generating")
def get_generating() -> bool:
    return GENERATING


@app.get("/objects/{filename}/generate-cuts")
async def single_video_generate_cuts(
        filename: str) -> Union[List[Tuple[Any, bool]], HTTPException]:
    global GENERATING
    if GENERATING:
        return HTTPException(status_code=503, detail="Generating")
    GENERATING = True
    convert_session_to_settings()
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
        old_cuts = JSON_INFO["objects"][objects.index(obj)]["cuts"]
        cuts = [(io.remove_extension(cut), True) for cut in cuts]
        if old_cuts:
            for i in range(len(cuts)):
                if cuts[i][0] == old_cuts[i][0]:
                    cuts[i] = old_cuts[i]
        cuts.sort(key=lambda x: int(x[0].split("-")[0]))
        JSON_INFO["objects"][objects.index(obj)]["cuts"] = cuts

        save_json(JSON_INFO)

        GENERATING = False
        return cuts

    GENERATING = False
    return HTTPException(status_code=403)


@app.get("/objects/{filename}/{cut}")
async def get_cut(filename: str, cut: str) -> FileResponse:
    return FileResponse(
        os.path.join(TMP_PATH, io.generate_clean_name(filename), CUT,
                     cut + ".mp4"))


@app.get("/generate-result/{filename}")
async def generate_result_for_file(
        filename: str) -> Union[HTTPException, None]:
    global GENERATING
    if GENERATING:
        return HTTPException(status_code=503, detail="Generating")
    GENERATING = True
    objects = JSON_INFO["objects"]
    obj = next(filter(lambda x: x["name"] == filename, objects), None)

    if not obj:
        return HTTPException(status_code=404, detail="Object not found")
    if not obj["enabled"]:
        return HTTPException(status_code=403)

    cuts = []
    used = []
    for cut in obj["cuts"]:
        used.append(cut[1])
        if cut[1]:
            cn = io.generate_clean_name(obj["name"])
            cuts.append(os.path.join(TMP_PATH, cn, CUT, cut[0] + ".mp4"))
    folder = os.path.join(TMP_PATH, io.generate_clean_name(obj["name"]))
    save_path = os.path.join(folder, "merged.mp4")

    with open(os.path.join(folder, "info.json"), "r") as f:
        info = json.load(f)

    # print(info["used"], used)

    if info["recompile"] or not "used" in info or info["used"] != used:
        with open(os.path.join(TMP_PATH, "recompile.json"), "w") as f:
            f.write(json.dumps({"filename": obj["name"]}))

        vid.merge_cuts_with_files(cuts, save_path)
        info["recompile"] = False
        info["used"] = used
        with open(os.path.join(folder, "info.json"), "w") as f:
            json.dump(info, f, indent=4)

    GENERATING = False
    return None


@app.get("/generate-result")
async def generate_result() -> Union[HTTPException, None]:
    global GENERATING
    if GENERATING:
        return HTTPException(status_code=503, detail="Generating")
    GENERATING = True

    if not os.path.exists(os.path.join(TMP_PATH, "recompile.json")):
        GENERATING = False
        return None

    os.remove(os.path.join(TMP_PATH, "recompile.json"))

    clips = []
    for obj in JSON_INFO["objects"]:
        if obj["enabled"]:
            cn = io.generate_clean_name(obj["name"])
            clips.append(os.path.join(TMP_PATH, cn, "merged.mp4"))

    print("final clips", clips)
    vid.merge_cuts_with_files(clips)
    if os.path.exists("merged.jpg"):
        os.remove("merged.jpg")
    extract_first_image_of_video("merged.mp4", "merged")
    GENERATING = False
    return None


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
    obj = next(filter(lambda x: x["name"] == filename, musics), None)

    if not obj:
        return HTTPException(status_code=404, detail="Object not found")

    index = musics.index(obj)

    obj["enabled"] = not obj["enabled"]
    musics[index] = obj

    JSON_INFO["musics"] = musics

    save_json(JSON_INFO)

    return obj["enabled"]


@app.post("/musics/reorder")
async def music_reorder(data: List[Reorder]) -> Dict[Any, Any]:
    musics = JSON_INFO["musics"]
    new_musics = []
    for datum in data:
        music = next(filter(lambda x: x["name"] == datum.name, musics), None)
        new_musics.append(music)
    JSON_INFO["musics"] = new_musics

    with open(os.path.join(TMP_PATH, "recompile.json"), "w") as f:
        f.write("{}")

    save_json(JSON_INFO)
    return JSON_INFO


@app.get("/objects/filters/{filename}/read")
async def filters_read(filename: str) -> Union[Dict[Any, Any], HTTPException]:
    objects = JSON_INFO["objects"]
    obj = next(filter(lambda x: x["name"] == filename, objects), None)
    if not obj:
        return HTTPException(status_code=404, detail="Object not found")

    return obj["filters"]


@app.post("/objects/filters/{filename}/save")
async def filters_save(data: Filters,
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
async def update(filename: str) -> Union[bool, HTTPException]:
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


@app.get("/filters/read")
async def global_filters_read() -> Union[Dict[Any, Any], HTTPException]:
    filters = JSON_INFO["filters"]
    if not filters:
        return HTTPException(status_code=404, detail="Object not found")

    return filters


@app.post("/filters/save")
async def global_filters_save(
        data: Filters) -> Union[Dict[Any, Any], HTTPException]:
    filters = JSON_INFO["filters"]
    if not filters:
        return HTTPException(status_code=404, detail="Object not found")

    f = jsonable_encoder(data)
    JSON_INFO["filters"] = f
    save_json(JSON_INFO)

    return filters
