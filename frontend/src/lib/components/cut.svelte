<script>
    import { API_URL } from "../../constants.js";
    import Video from "./video.svelte";

    export let cuts;
    console.log(cuts);
</script>

{#if cuts}
    <div class="gallery">
        {#each Object.entries(cuts) as [filename, cuts]}
            <div class="group">
                {#each cuts as cut}
                    <Video
                        {filename}
                        shortname={filename + "-" + cut}
                        videoUrl={API_URL + "/objects/" + filename + "/" + cut}
                        editable={false}
                    />
                {/each}
            </div>
        {/each}
    </div>
{/if}

<style>
    .gallery {
        justify-content: center;
        border-radius: 4px;

        justify-content: center;
        text-align: center;
        width: 95%;
        margin: auto;
    }
    .group {
        background-color: red;
        width: 100%;

        display: flex;
        flex-wrap: wrap;
        margin-bottom: 100px;
    }
</style>
