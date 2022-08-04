# Usage
## Releases
[Releases](https://github.com/Flowtter/crispy/releases) are available for windows and linux.\

## Setup
Firstly, you will have to install [ffmpeg](https://ffmpeg.org/about.html) (ffprobe is also required).
Once unzip, you can run the setup.[sh|bat] file.\
Then you can add your videos in the mp4/mp3 format in the resources folder.

## Run
You can now run the application with the run.[sh|bat] file.

# Demo
[live demo](https://crispy.gyroskan.com/)
# Dev
## Setup pre-commit
First install `pre-commit` by running:
```sh
pip install pre-commit
```
Then to install the git hook run:
```sh
pre-commit install -t pre-commit -t commit-msg
```

Now `pre-commit` will run on every `git commit`.


## Start
- `cd frontend && npm install && npm run dev`
- `pip install -r backend/requirements.txt && python backend/src/app.py`
