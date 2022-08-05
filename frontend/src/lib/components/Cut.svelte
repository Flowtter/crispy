<script>
    import { API_URL } from "../../constants.js";
    import Video from "./Video.svelte";
    import ChangePage from "./ChangePage.svelte";

    export let cuts;

    let cuts_split = [];

    function split_cuts() {
        // slipt cuts into sub arrays of 5 elements
        for (let i = 0; i < cuts.length; i += 10) {
            cuts_split.push(cuts.slice(i, i + 10));
        }
    }
    split_cuts();
    console.log(cuts_split);

    let currentPage = 0;

    function changePage(event) {
        currentPage = event.detail;
        console.log(event.detail);
        window.scrollTo(0, 0);
    }
</script>

{#key cuts}
    {#if cuts}
        <div class="gallery">
            {#key currentPage}
                {#each cuts_split[currentPage] as vid}
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
                <ChangePage
                    {currentPage}
                    maxi={cuts_split.length}
                    on:change={changePage}
                />
            {/key}
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
