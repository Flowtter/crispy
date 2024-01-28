<div align="center">

# Crispy

Crispy is a machine-learning algorithm to make video-games montages efficiently.
It uses a neural network to detect highlights in the video-game frames.\
[![Tech](https://skillicons.dev/icons?i=python,svelte,ts,css,html,docker,bash,mongo,github)](https://skillicons.dev)

</div>

# Demo

[live demo](https://crispy.gyroskan.com/)\
[youtube demo](https://www.youtube.com/watch?v=svT-Z_MkAfw)

# Supported games

Currently it supports **[Valorant](https://playvalorant.com/)**, **[Overwatch](https://playoverwatch.com/)**, **[CSGO2](https://www.counter-strike.net/cs2)** and **[The Finals](https://www.reachthefinals.com/)**.

# Usage

## Releases

[Releases](https://github.com/Flowtter/crispy/releases) are available for windows and linux.

## Setup

Firstly, you will have to install [ffmpeg](https://ffmpeg.org/about.html) (ffprobe is also required).\
Once unzip, you can run the setup.[sh|bat] file.\
Then you can add your videos in the mp4/mp3 format in the resources folder.

## Configuration

You can configure the algorithm in the settings.json file.\
It's where you'll change the game.\
config example:

```json
{
  "neural-network": {
    "confidence": 0.8
  },
  "clip": {
    "framerate": 8,
    "second-before": 3,
    "second-after": 3,
    "second-between-kills": 5
  },
  "stretch": false,
  "game": "valorant"
}
```

The following settings are adjustable:

- neural-network
  - confidence: The confidence level used by the neural network. Lower values will include more frames, but might include some false positives.
- clip
  - framerate: The framerate of the clip at which the neural network will be applied. Higher values will include more frames, but will take more time to process.
  - second-before: Seconds of gameplay included before the highlight.
  - second-after: Seconds of gameplay included after the highlight.
  - second-between-kills: Transition time between highlights. If the time between two highlights is less than this value, the both highlights will be merged.
- game: Chosen game (either "valorant", "overwatch" or "csgo2")
- stretch: This is an option in case you're playing on a 4:3 resolution but your clips are recorded in 16:9.

### Recommended settings

I recommend you to use the trials and errors method to find the best settings for your videos.\
Here are some settings that I found to work well for me:

#### Valorant

```json
{
  "neural-network": {
    "confidence": 0.8
  },
  "clip": {
    "framerate": 8,
    "second-before": 4,
    "second-after": 0.5,
    "second-between-kills": 3
  },
  "stretch": false,
  "game": "valorant"
}
```

#### Overwatch

```json
{
  "neural-network": {
    "confidence": 0.6
  },
  "clip": {
    "framerate": 8,
    "second-before": 4,
    "second-after": 3,
    "second-between-kills": 5
  },
  "stretch": false,
  "game": "overwatch"
}
```

#### CSGO2

```json
{
  "neural-network": {
    "confidence": 0.7
  },
  "clip": {
    "framerate": 8,
    "second-before": 4,
    "second-after": 1,
    "second-between-kills": 3
  },
  "stretch": false,
  "game": "csgo2"
}
```

#### The Finals

```json
{
  "clip": {
    "framerate": 8,
    "second-before": 6,
    "second-after": 0,
    "second-between-kills": 3
  },
  "stretch": false,
  "game": "thefinals"
}
```

## Run

You can now run the application with the run.[sh|bat] file.

# Frontend explanation

The frontend is a web-application that allows you to add options to the Crispy algorithm.\
It has 5 views:

- Clips
- Segments
- Musics
- Effects
- Result

### Clips

In the clips view, you can see the list of your videos.\
You can rearrange them by dragging and dropping them.\
Select the videos you want to make segments of by selecting "show" for that video \
Select the videos you want in the montage and add customs effects for a single clip.\
Once you've made your selection, you can click on `generate segments` to create the segments.

### Segments

In the segments view, you can see the list of your segments.\
Each segment is a gameplay highlight chosen by the algorithm. \
You can select "hide" on a segment to exclude that segment from the final result.

### Musics

In the music view, you can see the list of your music.\
This is the music that will be played in the final result video. \
You can select "hide" for songs you don't want and you can you can rearrange them by dragging and dropping them.

### Effects

In the effects view, you can see the list of your effects.\
Those effects are applied to the whole video.\
Yet the clips' effects override the global effects.\
The following effects are available to use:

- blur
- hflip
- vflip
- brightness
- saturation
- zoom
- grayscale

### Result

In the result view, you can see the result of your montage.

# Q&A

### **Q:** Why are some games not using the neural network?

**A:** To detect highlights in a video-game, the neural-network searches for things that always happen in a highlight.\
For example, in Overwatch, a kill is symbolized by a red skull. So the neural-network will search for red skulls in the frames.\
Unfortunately, not all games have such things.\
The finals, for example, is a game where you don't have any symbol to represent a kill.\
So for those games, the neural-network is not used. Instead, we're using an OCR to detect the killfeed.\
The OCR is definitely not as efficient as the neural-network, slow, and depends on the quality of the video.\
But it's the best we can do for now.

### **Q:** Why are some games not supported?

**A:** The neural-network has simply not been trained for those games.\
If you want to add support for a game, you can train the neural-network yourself and then make a pull request.\
A tutorial is available [here](https://github.com/Flowtter/crispy/tree/master/crispy-api/dataset).

### **Q:** In CSGO2, I moved the UI, and the kills are not detected anymore. What can I do?

**A:** Unfortunately, there is nothing you can do.\
The neural-network is trained to detect kills in the default UI.\
I'm planning to add support for custom UI in the future, but this is definitely not a priority.

# Contributing

Every contribution is welcome.

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

- `cd crispy-frontend && yarn && yarn dev`
- `cd crispy-backend && pip install -Ir requirements-dev.txt && python -m api`

## Test

- `cd crispy-api && pytest`
