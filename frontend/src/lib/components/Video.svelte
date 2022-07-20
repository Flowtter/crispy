<script>
    import axios from "axios";
    import { onMount } from "svelte";
    import { API_URL } from "../../constants";

    export let filename;
    export let shortname;

    const fetch = () => {
        axios
            .get(API_URL + "/objects/" + filename + "/info")
            .then((response) => {
                const res = response.data;
                enabled = res.enabled ? "enabled" : "disabled";
            });
    };
    onMount(fetch);

    let enabled;

    function handleSwitch() {
        axios.get(API_URL + "/objects/" + filename + "/switch");
        enabled = enabled == "disabled" ? "enabled" : "disabled";
    }

    ///////////
    // https://svelte.dev/repl/7bf3c9308bc941a682ac92b9bec0a653?version=3.23.2
    ///////////

    // These values are bound to properties of the video
    let time = 0;
    let duration;
    let paused = true;

    // Used to track time of last mouse down event
    let lastMouseDown;

    // we can't rely on the built-in click event, because it fires
    // after a drag — we have to listen for clicks ourselves
    function handleMousedown(e) {
        lastMouseDown = new Date();
    }

    function handleMouseup(e) {
        if (new Date() - lastMouseDown < 300) {
            if (paused) e.target.play();
            else e.target.pause();
        }
    }
</script>

<div class="object">
    <div class="title">
        {shortname}.mp4
    </div>
    <div class={enabled}>
        <video
            poster={API_URL + "/objects/" + filename + "/image"}
            src={API_URL + "/objects/" + filename + "/video"}
            on:mousedown={handleMousedown}
            on:mouseup={handleMouseup}
            bind:currentTime={time}
            bind:duration
            bind:paused
        >
            <track kind="captions" />
        </video>

        {#if !duration}
            <div class="loader">
                <div class="lds-roller">
                    <div />
                    <div />
                    <div />
                    <div />
                    <div />
                    <div />
                    <div />
                    <div />
                </div>
            </div>
        {/if}
    </div>
    <div class="trailing-menu">
        <button>FILTER</button>
        <p>|</p>
        <button>TRANSITION</button>
        <p>|</p>
        <button on:click={handleSwitch}>HIDE</button>
    </div>
</div>

<style>
    .title {
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem;
        text-align: center;
        font-weight: bold;
    }

    .disabled {
        filter: brightness(40%);
    }
    .object {
        width: calc(1600px / 4 - 80px);
        background-color: var(--terciary);
        /* display: flex; */
        justify-content: center;
        border-radius: 20px;
        position: relative;
        margin: 1vh;
    }
    video {
        width: 94%;
        height: 90%;
        object-fit: cover;
        display: block;
        border-radius: 20px;
        margin: auto;
    }
    .trailing-menu {
        /* background-color: red; */

        height: 100%;
        width: 100%;
        display: flex;
    }
    .trailing-menu > button {
        width: 100%;
    }
    .trailing-menu > button:first-child {
        border-radius: 0 0 0 20px;
    }
    .trailing-menu > button:last-child {
        border-radius: 0 0 20px 0;
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
        background-color: var(--terciary-variant);
    }

    /*  */
    .loader {
        position: absolute;
        /* center */
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    .lds-roller {
        display: inline-block;
        position: relative;
        width: 80px;
        height: 80px;
    }
    .lds-roller div {
        animation: lds-roller 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
        transform-origin: 40px 40px;
    }
    .lds-roller div:after {
        content: " ";
        display: block;
        position: absolute;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--terciary);
        margin: -4px 0 0 -4px;
    }
    .lds-roller div:nth-child(1) {
        animation-delay: -0.036s;
    }
    .lds-roller div:nth-child(1):after {
        top: 63px;
        left: 63px;
    }
    .lds-roller div:nth-child(2) {
        animation-delay: -0.072s;
    }
    .lds-roller div:nth-child(2):after {
        top: 68px;
        left: 56px;
    }
    .lds-roller div:nth-child(3) {
        animation-delay: -0.108s;
    }
    .lds-roller div:nth-child(3):after {
        top: 71px;
        left: 48px;
    }
    .lds-roller div:nth-child(4) {
        animation-delay: -0.144s;
    }
    .lds-roller div:nth-child(4):after {
        top: 72px;
        left: 40px;
    }
    .lds-roller div:nth-child(5) {
        animation-delay: -0.18s;
    }
    .lds-roller div:nth-child(5):after {
        top: 71px;
        left: 32px;
    }
    .lds-roller div:nth-child(6) {
        animation-delay: -0.216s;
    }
    .lds-roller div:nth-child(6):after {
        top: 68px;
        left: 24px;
    }
    .lds-roller div:nth-child(7) {
        animation-delay: -0.252s;
    }
    .lds-roller div:nth-child(7):after {
        top: 63px;
        left: 17px;
    }
    .lds-roller div:nth-child(8) {
        animation-delay: -0.288s;
    }
    .lds-roller div:nth-child(8):after {
        top: 56px;
        left: 12px;
    }
    @keyframes lds-roller {
        0% {
            transform: rotate(0deg);
        }
        100% {
            transform: rotate(360deg);
        }
    }
</style>
