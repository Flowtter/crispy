<script>
    import { API_URL, globalError } from "../../constants.js";
    import axios from "axios";
    import { onMount } from "svelte";

    export let src;
    let basename = src.split("/").pop();
    let volume = 0.5;
    let enabled = "enabled";

    function handleSwitch() {
        let url = API_URL + "/musics/" + basename + "/switch";
        axios.get(url);
        enabled = enabled == "disabled" ? "enabled" : "disabled";
    }

    const fetch = () => {
        let url = API_URL + "/musics/" + basename + "/info";
        axios
            .get(url)
            .then((response) => {
                const res = response.data;
                enabled = res ? "enabled" : "disabled";
                // console.log("music", basename, enabled, res);
            })
            .catch((error) => {
                globalError(error);
            });
    };
    onMount(fetch);
</script>

<div class={enabled === "enabled" ? "" : "disabled"}>
    <div class="audio-container" draggable={false}>
        <p>{basename}</p>
        <audio {src} controls bind:volume>
            <track kind="captions" />
        </audio>
        <div class="trailing-menu">
            <button class="only" on:click={handleSwitch}
                >{enabled === "enabled" ? "HIDE" : "SHOW"}</button
            >
        </div>
    </div>
</div>

<style>
    .disabled {
        filter: brightness(35%);
    }
    .audio-container {
        margin: auto;
        width: 90%;
        background-color: var(--secondary);
        border-radius: 20px;
        margin-bottom: 50px;
    }
    audio {
        width: 90%;
        margin: auto;
        display: block;
    }

    p {
        font-size: 1rem;
        font-weight: bold;
        text-align: center;
        margin: auto;
        width: 100%;
        padding-top: 10px;
        padding-bottom: 10px;
        color: var(--white-text);
    }
    .trailing-menu {
        /* background-color: red; */
        margin-top: 5px;
        height: 50px;
        width: 100%;
        display: flex;
    }

    .only {
        border-radius: 0 0 20px 20px !important;
        width: 100%;
    }

    button {
        text-align: center;
        /* padding: 12px 20px; */
        border: none;
        border-radius: 0px;
        background-color: var(--terciary);
        outline: none;
        cursor: pointer;
        border: none;
        color: var(--white-text);
        margin-bottom: 0;
        font-size: large;
        /* width: 2vw !important; */
    }
    button:hover {
        transition: all 0.2s;
        background-color: var(--terciary-hover);
    }
</style>
