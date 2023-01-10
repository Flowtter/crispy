<script>
    import { API_URL } from "../../constants";

    ///////////
    // found on https://svelte.dev/repl/7bf3c9308bc941a682ac92b9bec0a653?version=3.23.2
    ///////////

    let time = 0;
    let duration;
    let paused = true;

    let lastMouseDown;

    function handleMousedown(e) {
        lastMouseDown = new Date();
    }

    function handleMouseup(e) {
        if (new Date() - lastMouseDown < 300) {
            if (paused) e.target.play();
            else e.target.pause();
        }
    }
    let t = Date.now();
</script>

<div class="object">
    <div class="title">merged.mp4</div>
    <video
        poster={API_URL + "/results/image?t=" + t}
        src={API_URL + "/results/video?t=" + t}
        on:mousedown={handleMousedown}
        on:mouseup={handleMouseup}
        bind:currentTime={time}
        bind:duration
        bind:paused
    >
        <track kind="captions" />
    </video>
    <br />

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
    <br />
</div>

<style>
    .title {
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem;
        text-align: center;
        font-weight: bold;
    }

    .object {
        background-color: var(--terciary);
        justify-content: center;
        border-radius: 20px;
        position: relative;
        margin-left: 10vh;
        margin-right: 10vh;
    }
    video {
        width: 98%;
        height: 94%;
        object-fit: cover;
        display: block;
        border-radius: 20px;
        margin: auto;
    }

    .loader {
        position: absolute;
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
