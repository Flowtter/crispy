<script>
    import { tweened } from "svelte/motion";
    import { cubicOut } from "svelte/easing";
    import { createEventDispatcher } from "svelte";
    import axios from "axios";
    import { API_URL } from "../../variables";
    import { onMount } from "svelte";

    const progress = tweened(0, {
        duration: 3000,
        easing: cubicOut,
    });

    let text;
    let finished = false;

    const dispatch = createEventDispatcher();

    function update() {
        if (!interval) {
            interval = setInterval(update, 1000);
        }
        axios.get(API_URL + "/status").then((response) => {
            progress.set(response.data.count / response.data.max);
            text = response.data.job;
            if (text === "Uploading video") {
                finished = true;
                dispatch("video");
                clearInterval(interval);
            }
        });
    }
    let interval;
    onMount(update);
</script>

{#if !finished}
    <div class="container">
        <br />
        <div class="outer">
            <div class="inner" style="width: {$progress * 100}%" />
        </div>
        <p>{text}</p>
    </div>
{/if}

<style>
    .inner,
    .outer {
        height: 20px;
        border-radius: 10px;
    }
    .outer {
        width: 80%;
        margin: auto;
        /* background-color: transparent; */
        border: 1px solid var(--terciary-variant);
    }
    .inner {
        height: 101%;
        background-color: var(--terciary);
    }
    .container {
        width: 90vw;
        margin: auto;
        background-color: var(--secondary);
        border-radius: 25px;
    }
    p {
        margin-top: 0.2em;
        text-align: center;
        padding-bottom: 10px;
    }
</style>
