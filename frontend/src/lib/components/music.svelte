<script>
    import AudioPlayer from "./audio.svelte";

    let audioTracks = [
        "https://sveltejs.github.io/assets/music/strauss.mp3",
        "https://sveltejs.github.io/assets/music/holst.mp3",
        "https://sveltejs.github.io/assets/music/satie.mp3",
    ];
</script>

<div>
    Musics:
    {#each audioTracks as src}
        <AudioPlayer {src} />
    {/each}
</div>
