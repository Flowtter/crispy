<script>
    import { API_URL } from "../../constants.js";
    import Video from "./video.svelte";

    export let cuts;
</script>

{#key cuts}
    {#if cuts}
        <div class="gallery">
            {#each cuts as vid}
                <div class="content">
                    <p>{vid.file}.mp4</p>
                    <div class="group">
                        {#each Object.entries(vid.cut) as [index]}
                            <Video
                                filename={vid.file}
                                shortname={vid.cut[index][0]}
                                videoUrl={API_URL +
                                    "/objects/" +
                                    vid.file +
                                    "/" +
                                    vid.cut[index][0]}
                                editable={false}
                                cuts={vid.cut[index][0]}
                            />
                        {/each}
                    </div>
                </div>
            {/each}
        </div>
        <br />
    {/if}
{/key}

<style>
    p {
        padding-top: 10px;
    }
    .gallery {
        justify-content: center;
        border-radius: 4px;

        justify-content: center;
        text-align: center;
        width: 95%;
        margin: auto;
    }
    .group {
        display: flex;
        flex-wrap: wrap;
        margin-bottom: 20px;
        /* center */
        justify-content: center;
    }
    .content {
        background-color: var(--background);
        border-radius: 10px;
        width: auto;
    }
</style>
