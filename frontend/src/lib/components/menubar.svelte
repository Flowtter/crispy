<script>
    import "../../constants";
    import axios from "axios";
    import { API_URL } from "../../constants";
    import { createEventDispatcher } from "svelte";

    const dispatch = createEventDispatcher();

    export let mode;
    let cuts = false;
    let result = false;

    async function generateCuts() {
        cuts = true;
        let objects = await axios.get(API_URL);

        for (let object of objects.data.objects) {
            if (object.enabled) {
                let cuts = await axios.get(
                    API_URL + "/objects/" + object.name + "/generate-cuts"
                );
                cuts = cuts.data;
                dispatch("cuts", {
                    file: object.name,
                    cuts: cuts,
                });
            }
        }
    }
</script>

<div class="main">
    <div class="menu">
        <button>CLIPS</button>
        <p>|</p>
        <button class={cuts ? "" : "grey"}>CUTS</button>
        <p>|</p>
        <button>MUSIC</button>
        <p>|</p>
        <button>EFFECTS</button>
        <p>|</p>
        <button class={result ? "" : "grey"}>RESULT</button>
    </div>
    {#key mode}
        <div class="end">
            {#if mode === "clips"}
                <button on:click={generateCuts}>GENERATE CUTS</button>
            {/if}
        </div>
    {/key}
</div>

<style>
    .main {
        width: 100%;
        border-radius: 0 0 20px 20px;
        margin-bottom: 20px;
        display: flex;
        background-color: var(--secondary);
    }
    .menu {
        height: 50px;
        width: 60%;
        display: flex;
    }
    .menu > button {
        width: 100%;
    }
    .menu > button:first-child {
        border-radius: 0 0 0 20px;
    }
    .end {
        height: 50px;
        width: 20%;
        display: flex;
        margin-right: 0;
        margin-left: auto;
    }
    .end > button {
        width: 100%;
        border-radius: 0 0 20px 0;
    }

    button {
        text-align: center;
        /* padding: 12px 20px; */
        border: none;
        border-radius: 0px;
        outline: none;
        cursor: pointer;
        border: none;
        color: var(--white-text);
        margin-bottom: 0;
        font-size: large;
        /* width: 2vw !important; */
        font-size: 1.5em;
        background-color: var(--secondary);
    }
    button:hover {
        transition: all 0.2s;
        background-color: var(--primary);
    }
    .grey {
        color: grey;
    }
</style>
