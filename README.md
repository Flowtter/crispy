# Crispy
Crispy is a machine-learning algorithm to make video-games montages efficiently.\
It uses a neural network to detect highlights in the video-game frames.\
Currently it supports **[Valorant](https://playvalorant.com/)**.
# Usage
## Releases
[Releases](https://github.com/Flowtter/crispy/releases) are available for windows and linux.\

## Setup
Firstly, you will have to install [ffmpeg](https://ffmpeg.org/about.html) (ffprobe is also required).
Once unzip, you can run the setup.[sh|bat] file.\
Then you can add your videos in the mp4/mp3 format in the resources folder.

## Run
You can now run the application with the run.[sh|bat] file.

## Frontend explanation
The frontend is a web-application that allows you to add options to the Crispy algorithm.\
It has 5 pages:
- clips
- cuts
- music
- effects
- result

### Clips
In the clips page, you can see the list of your videos.\
You can rearrange them by dragging and dropping them.\
Select the video you don't want in the montage and add customs effects for a single clip.\
Once you've made your selection, you can click on `generate cuts` to create the cuts.

### Cuts
In the cuts page, you can see the list of your cuts.\
You can hide the one you don't want

### Music
In the music page, you can see the list of your music.\
You can hide the one you don't want and you can you can rearrange them by dragging and dropping them.\

### Effects
In the effects page, you can see the list of your effects.\
Those effects are applied to the whole video.\
Yet the clips' effects override the global effects.

### Result
In the result page, you can see the result of your montage.

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
