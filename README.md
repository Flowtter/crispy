<div align="center">

# Crispy

**Crispy** is a machine learning platform designed to efficiently create video game montages. It utilizes neural networks to detect highlights within video game footage.

[![Tech Stack](https://skillicons.dev/icons?i=python,svelte,ts,css,html,docker,bash,mongo,github)](https://skillicons.dev)

</div>

# Demo

- [Live Demo](https://crispy.gyroskan.com/)
- [YouTube Demo](https://www.youtube.com/watch?v=svT-Z_MkAfw)

# Supported Games

Crispy currently supports the following games:

- **[Valorant](https://playvalorant.com/)**
- **[League of Legends](https://www.leagueoflegends.com/)**
- **[Overwatch 2](https://playoverwatch.com/)**
- **[CSGO 2](https://www.counter-strike.net/cs2)**
- **[The Finals](https://www.reachthefinals.com/)**

# Usage

## Installation

Download the latest release for your operating system from the [Releases page](https://github.com/Flowtter/crispy/releases). Releases are available for Windows and Linux.

## Setup

1. **Install Dependencies**

   - Install [FFmpeg](https://ffmpeg.org/about.html). Ensure that both `ffmpeg` and `ffprobe` are installed and added to your system's PATH.

2. **Run the Setup**

   - Unzip the downloaded release.
   - Run the appropriate setup script:
     - For Windows: `setup.bat`
     - For Linux: `setup.sh`

3. **Add your Videos and Musics**

   - Place your video files (`.mp4` format) and audio files (`.mp3` format) into the `resources` folder.

### Python version

Currently, Crispy supports Python 3.8, 3.9, and 3.10.

## Configuration

Customize the application by editing the `settings.json` file. This is where you can adjust algorithm settings and select the game you are processing.

### Configuration Example

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

### Available Settings

- **neural-network**
  - **confidence**: The confidence threshold used by the neural network. Lower values may include more frames but might introduce false positives.
- **clip**
  - **framerate**: The framerate at which the neural network processes the clips. Higher values include more frames but increase processing time.
  - **second-before**: Number of seconds to include before the highlight.
  - **second-after**: Number of seconds to include after the highlight.
  - **second-between-kills**: Maximum time between kills to be considered part of the same highlight. If the time between two highlights is less than this value, they will be merged.
- **stretch**: Set to `true` if you're playing on a 4:3 resolution but your clips are recorded in 16:9.
- **game**: The game you are processing. Options are `"valorant"`, `"overwatch"`, `"csgo2"`, `"the-finals"`, `"league-of-legends"`.

### Recommended Settings

It's recommended to experiment with the settings to achieve the best results for your videos. Below are some configurations that have worked well:

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

#### Overwatch 2

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

#### CSGO 2

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

Since **The Finals** does not use the neural network, the settings differ slightly. The application uses image recognition and Optical Character Recognition (OCR) to detect kills. Due to the computational demands of OCR, processing can be slow.

**Recommendation:** Use a framerate of 4 to balance speed and accuracy. Increasing the framerate may improve results but will significantly increase processing time (a maximum of 8 is suggested).

```json
{
  "clip": {
    "framerate": 4,
    "second-before": 6,
    "second-after": 0,
    "second-between-kills": 6
  },
  "stretch": false,
  "game": "the-finals"
}
```

#### League of Legends

For **League of Legends**, image recognition is used to detect kills. A lower framerate is sufficient because kill indicators remain on the screen for an extended period.

```json
{
  "clip": {
    "framerate": 4,
    "second-before": 8,
    "second-after": 0,
    "second-between-kills": 10
  },
  "stretch": false,
  "game": "league-of-legends"
}
```

## Running the Application

After configuration, run the application using the appropriate script:

- For Windows: `run.bat`
- For Linux: `run.sh`

# Frontend Overview

The frontend is a web application that allows you to interact with the Crispy algorithm and customize your video montages. It consists of five main sections:

1. **Clips**
2. **Segments**
3. **Music**
4. **Effects**
5. **Result**

## Clips

In the **Clips** section, you can:

- **View and manage your video clips**: See a list of your uploaded videos.
- **Rearrange clips**: Drag and drop to reorder your clips.
- **Select clips for segmentation**: Use the "Show" toggle to select which videos to process.
- **Add custom effects**: Apply effects to individual clips.
- **Generate segments**: After making your selections, click on **Generate Segments** to create highlights.

## Segments

In the **Segments** section, you can:

- **View generated segments**: See the list of highlights extracted by the algorithm.
- **Include or exclude segments**: Use the "Hide" toggle to exclude segments from the final montage.

## Music

In the **Music** section, you can:

- **Manage your music tracks**: View the list of music files added to the `resources` folder.
- **Select music for the montage**: Use the "Hide" toggle to exclude tracks.
- **Rearrange music**: Drag and drop to set the order of music tracks in your montage.

## Effects

In the **Effects** section, you can:

- **Apply global effects**: Add effects that will be applied to the entire video.
- **Override with clip effects**: Note that effects applied to individual clips will override these global effects.
- **Available effects**:
  - Blur
  - Horizontal Flip (`hflip`)
  - Vertical Flip (`vflip`)
  - Brightness
  - Saturation
  - Zoom
  - Grayscale

## Result

In the **Result** section, you can:

- **Preview your montage**: See the final assembled video with all clips, music, and effects applied.

# Q&A

#### Q: I get an Axios error when I load the web page.

**A:** This error likely occurs because the backend is not running. Please ensure that the backend is operational. Look for the following messages in your console:

```bash
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Adding X highlights, this may take a while.
WARNING:  Wait for `Application startup complete.` to use Crispy.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:7821 (Press CTRL+C to quit)
```

If you don't see the `Application startup complete` message, the backend is still initializing or there is an error. Wait until it completes or check for errors. If issues persist, refer to [existing issues](https://github.com/Flowtter/crispy/issues?q=is%3Aissue+error), or open a new issue if necessary.

### Q: How can I change the game ?

**A:** To change the game setting in Crispy, follow these steps:

1. **Stop the application.**
2. **Delete the `.data` folder and the `session` folder** in the Crispy directory.
3. **Edit `settings.json`** to specify the new game under the `"game"` key.
4. **Add and remove any necessary files in the resources folder** (e.g., new game dataset).
5. **Restart the application.**

These steps will reset the game configuration, and the new game will be applied upon starting Crispy.

#### Q: Why are some games not using the neural network?

**A:** The neural network is designed to detect consistent visual cues that signify highlights, such as specific icons or symbols that appear during kills. Some games do not have these consistent indicators. For those games, we use alternative methods like image recognition or Optical Character Recognition (OCR). While these methods can be slower and less accurate, they are the best available options for games without consistent visual cues.

#### Q: Why are some games not supported?

**A:** The neural network requires training specific to each game. If a game is not supported, it means the neural network has not been trained for it yet. You can contribute by training the neural network for the game and submitting a pull request. A tutorial is available [here](https://github.com/Flowtter/crispy/tree/master/crispy-api/dataset).

#### Q: In CSGO 2, I moved the UI, and the kills are not detected anymore. What can I do?

**A:** Currently, the neural network is trained to detect kills based on the default UI layout. Custom UI configurations are not supported at this time. Support for custom UIs may be added in future updates.

#### Q: Why is the algorithm so slow on The Finals?

**A:** The algorithm is slow because it relies on OCR to detect the kill feed, which is computationally intensive. To improve processing time, use a lower framerate (e.g., 4 frames per second). Increasing the framerate will significantly increase processing time without substantial improvement in results.

# Contributing

We welcome contributions from the community!

## Setting Up Pre-Commit Hooks

To maintain code quality, we use `pre-commit` hooks. Follow these steps to set them up:

1. **Install Pre-Commit**

   ```sh
   pip install pre-commit
   ```

2. **Install Git Hooks**

   ```sh
   pre-commit install -t pre-commit -t commit-msg
   ```

   This will set up `pre-commit` to run automatically on every `git commit`.

## Development Setup

To get started with development:

1. **Frontend**

   ```sh
   cd crispy-frontend
   yarn
   yarn dev
   ```

2. **Backend**

   ```sh
   cd crispy-backend
   pip install -Ir requirements-dev.txt
   python -m api
   ```

## Running Tests

To run the test suite:

```sh
cd crispy-api
pytest
```
