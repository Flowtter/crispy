<script>
    import { API_URL } from "../../variables";

    // These values are bound to properties of the video
    let time = 0;
    let paused = true;
    let duration;

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

<div class="photo">
    <div class="holder">
        <video
            poster={API_URL + "/export/image"}
            src={API_URL + "/export/video"}
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
</div>
<br />

<style>
    .photo {
        width: calc(1920px / 2 - 20px);
        height: calc(1080px / 2);
        background-color: var(--secondary);
        justify-content: center;
        border-radius: 2vh;
        position: relative;
        margin: auto;
        margin-bottom: 10px;
        display: flex;
    }
    video {
        width: 99%;
        height: 96%;
        object-fit: cover;
        display: block;
        border-radius: 2vh;
        margin: auto;
        margin-top: 1%;
    }
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
