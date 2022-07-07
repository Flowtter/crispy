import os
import json
import argparse

from PIL import Image, ImageOps
import ffmpeg

DATASET_PATH = os.path.join("backend", "dataset")
VALUES_PATH = os.path.join(DATASET_PATH, "values.json")
VIDEOS_PATH = os.path.join("backend", "resources", "video")
DOT_PATH = os.path.join("backend", "assets", "dot.png")

INDEX = 0


def to_csv(folder: str, file: str, values: dict, save: bool = False) -> None:
    """Convert the images to a csv file"""
    global INDEX

    if not file in values:
        print("Warning:", file, "not in values, using []")
        d = []
    else:
        d = values[file]

    dict_values = []

    for inclusive_range in d:
        if inclusive_range == []:
            continue

        for i in range(inclusive_range[0], inclusive_range[1] + 1):
            dict_values.append(i)

    path = os.path.join(folder, file)

    csv = []
    images = os.listdir(path)
    images = [i for i in images if not os.path.isdir(os.path.join(path, i))]
    images.sort()

    file_clean = file
    file_clean = file_clean.replace("_", "-")
    file_clean = file_clean.replace(" ", "-")

    for i, image in enumerate(images):
        im = ImageOps.grayscale(Image.open(os.path.join(path, image)))
        pixel_values = list(im.getdata())

        pixel_values.insert(0, int(i in dict_values))
        csv.append(pixel_values)
        im.save(
            os.path.join(DATASET_PATH, "result",
                         str(INDEX) + "_" + file_clean + "_" + str(i) +
                         ".bmp"))
        INDEX += 1
        if save:
            if not os.path.exists(os.path.join(path, "grey")):
                os.makedirs(os.path.join(path, "grey"))
            if not os.path.exists(os.path.join(path, "v_grey")):
                os.makedirs(os.path.join(path, "v_grey"))
            im.save(os.path.join(path, "grey", image))
            im3 = Image.new("RGB", (112, 112))
            for x in range(112):
                for y in range(112):
                    v = int(pixel_values[x * 112 + y])
                    im3.putpixel((y, x), (v, v, v))

            res = Image.new("RGB", (336, 112))
            res.paste(Image.open(os.path.join(path, image)), (0, 0))
            res.paste(im, (112, 0))
            res.paste(im3, (224, 0))
            res.save(os.path.join(path, "v_grey", image))

    with open(os.path.join(folder, file + ".csv"), "w") as f:
        for row in csv:
            f.write(",".join([str(x) for x in row]) + "\n")


def extract_images(video_path: str, save_path: str) -> None:
    """Extract the images from the video"""
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    (
        ffmpeg
        .input(video_path)
        .filter('fps', fps='1/0.25')
        .crop(x=900, y=804, width=120, height=60)
        .overlay(ffmpeg.input(DOT_PATH))
        .output(os.path.join(save_path, "%3d.bmp"), start_number=0)
        .overwrite_output()
        .run(quiet=True)
    ) # yapf: disable


def concat_csv(folder: str) -> None:
    """Merge all the csv files into one"""
    result = []
    files = os.listdir(folder)
    files.sort()
    for file in files:
        if file.split(".")[-1] == "csv":
            if file == "result.csv":
                continue
            with open(os.path.join(folder, file), "r") as f:
                lines = f.readlines()
                result.extend(lines)

    with open(os.path.join(folder, "result.csv"), "w") as f:
        f.writelines(result)


def main(ext: bool, csv: bool) -> None:
    if not os.path.exists(DATASET_PATH):
        os.makedirs(DATASET_PATH)

    with open(VALUES_PATH, "r") as f:
        values = json.load(f)

    videos = os.listdir(VIDEOS_PATH)
    videos.sort()
    print(videos)

    if not os.path.exists(os.path.join(DATASET_PATH, "result")):
        os.makedirs(os.path.join(DATASET_PATH, "result"))

    for video in videos:
        print("Doing:", video)
        video_no_ext = video.split(".")[0]
        if ext:
            extract_images(os.path.join(VIDEOS_PATH, video),
                           os.path.join(DATASET_PATH, video_no_ext))

        if csv:
            to_csv(DATASET_PATH, video_no_ext, values)
    if csv:
        concat_csv(DATASET_PATH)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract", action="store_true")
    parser.add_argument("--to-csv", action="store_true")

    args = parser.parse_args()

    main(args.extract, args.to_csv)
