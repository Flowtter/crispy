import json
import os
import sys

from typing import Any, Dict, List, Tuple, Union

from fastapi import HTTPException
from fastapi.responses import FileResponse

from AI.network import NeuralNetwork
import video.video as vid
from utils.IO import io
from utils.constants import ASSETS, FILTERS_PATH, IMAGE, MUSICS_PATH, VIDEOS_PATH, app, CUT, TMP_PATH
from backend.json_handling import get_session_json, save_json
from backend.startup import extract_first_image_of_video


@app.get("/result/generate-result/{filename}")
async def generate_result_for_file(
        filename: str) -> Union[HTTPException, None]:

    session = get_session_json()
    objects = session["objects"]

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

    if info["recompile"] or not "used" in info or info["used"] != used:
        with open(os.path.join(TMP_PATH, "recompile.json"), "w") as f:
            f.write(json.dumps({"filename": obj["name"]}))

        vid.merge_cuts_with_files(cuts, save_path)
        info["recompile"] = False
        info["used"] = used
        with open(os.path.join(folder, "info.json"), "w") as f:
            json.dump(info, f, indent=4)

    return None


# TODO: Merge two next functions
def convert_filters(name: str) -> Dict[Any, Any]:
    session = get_session_json()
    objects = session["objects"]

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
    session = get_session_json()

    result: Dict[Any, Any] = {"filters": {}}
    for f in session["filters"]:
        if not session["filters"][f]["box"]:
            continue
        if f == "scale":
            result["filters"][f] = "w=" + str(int(
                session["filters"][f]["w"])) + ":h=" + str(
                    int(session["filters"][f]["h"]))
        elif "value" in session["filters"][f]:
            result["filters"][f] = session["filters"][f]["value"]
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


# @app.get("/generating")
# def get_generating() -> bool:
#     return False


def create_neural_network() -> NeuralNetwork:
    session = get_session_json()
    game = session["game"]

    if game == "overwatch":
        nn = NeuralNetwork([10000, 120, 15, 2], 0.01)
    elif game == "valorant":
        nn = NeuralNetwork([4000, 120, 15, 2], 0.01)
    elif game == "valorant-review":
        nn = NeuralNetwork([616, 120, 15, 2], 0.01)
    else:
        print(f"Game {game} not found")
        sys.exit(1)

    nn.load(os.path.join(ASSETS, game + "_trained_network_latest.npy"))

    return nn


NN = create_neural_network()

# TODO: move function convert_session, done every time should only be done once


@app.get("/result/{filename}/generate-cuts")
async def single_video_generate_cuts(
        filename: str) -> Union[List[Tuple[Any, bool]], HTTPException]:
    convert_session_to_settings()

    session = get_session_json()
    objects = session["objects"]
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
        old_cuts = session["objects"][objects.index(obj)]["cuts"]
        cuts = [(io.remove_extension(cut), True) for cut in cuts]
        if old_cuts:
            for i in range(len(cuts)):
                if cuts[i][0] == old_cuts[i][0]:
                    cuts[i] = old_cuts[i]
        cuts.sort(key=lambda x: int(x[0].split("-")[0]))
        session["objects"][objects.index(obj)]["cuts"] = cuts

        save_json(session)

        return cuts

    return HTTPException(status_code=403)


def get_music_list() -> List[str]:
    session = get_session_json()
    musics = session["musics"]

    res = []

    for music in musics:
        if music["enabled"]:
            res.append(os.path.join(MUSICS_PATH, music["name"] + ".mp3"))

    return res


@app.get("/result/generate-result")
async def generate_result() -> Union[HTTPException, None]:
    if not os.path.exists(os.path.join(TMP_PATH, "recompile.json")):
        return None

    os.remove(os.path.join(TMP_PATH, "recompile.json"))

    session = get_session_json()
    objects = session["objects"]

    clips = []
    for obj in objects:
        if obj["enabled"]:
            for cut in obj["cuts"]:
                if cut[1]:
                    cn = io.generate_clean_name(obj["name"])
                    clips.append(os.path.join(TMP_PATH, cn, "merged.mp4"))
                    break

    print("final clips", clips)
    vid.merge_cuts_with_files(clips, audio=get_music_list())
    if os.path.exists("merged.jpg"):
        os.remove("merged.jpg")
    extract_first_image_of_video("merged.mp4", "merged")
    return None


@app.get("/result/video")
def get_result_video() -> FileResponse:
    return FileResponse("merged.mp4")


@app.get("/result/image")
def get_result_image() -> FileResponse:
    return FileResponse("merged.jpg")
