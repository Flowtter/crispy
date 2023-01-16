<script>
    import "../../constants";
    import axios from "axios";
    import { API_URL, globalInfo, globalError } from "../../constants";
    import { createEventDispatcher } from "svelte";
    import { toast } from "@zerodevx/svelte-toast";

    const dispatch = createEventDispatcher();

    export let mode;
    let cutsDone = false;
    let result = false;

    let greenOptions = {
        "--toastBackground": "#009432",
        "--toastBarBackground": "#A3CB38",
    };

    let generating = false;

    async function lock() {
        if (generating) {
            globalError("Already generating.");
        }
        return generating;
    }

    async function generateCuts() {
        toast.pop(0);
        if (await lock()) return;
        generating = true;
        cutsDone = false;
        result = false;
        dispatch("clear", {});
        let objects = await axios.get(API_URL + "/").catch((error) => {
            globalError(error);
            generating = false;
            return;
        });
        await axios.get(API_URL + "/results/clear").catch((error) => {
            globalError(error);
            generating = false;
            return;
        });
        toast.push("Generating cuts! Check the cut menu to see them", {
            duration: 5000,
        });
        for (let object of objects.data.objects) {
            if (object.enabled) {
                const id = toast.push(
                    'Generating cut for "<strong>' + object.name + '</strong>"',
                    {
                        dismissable: false,
                        initial: 0,
                        next: 0,
                    }
                );
                let cuts = await axios
                    .get(API_URL + "/results/" + object.name + "/generate-cuts")
                    .catch((error) => {
                        generating = false;
                        globalError(error);
                        return;
                    });
                cuts = cuts.data;
                dispatch("cuts", {
                    file: object.name,
                    cuts: cuts,
                });
                toast.pop(id);
                toast.push(
                    'Cuts for "<strong>' + object.name + '</strong>" generated',
                    {
                        theme: greenOptions,
                    }
                );
            }
        }
        globalInfo(
            "All cuts generated! You can now generate the montage in the cut menu > Generate result"
        );
        cutsDone = true;
        generating = false;
    }

    async function generateResult() {
        toast.pop(0);
        if (await lock()) return;
        if (!cutsDone) return;
        generating = true;
        result = false;
        toast.push("Generating result! This may take a while...", {
            duration: 10000,
        });
        const id = toast.push("Loading, please wait...", {
            duration: 300,
            initial: 0,
            next: 0,
            dismissable: false,
        });

        let objects = await axios.get(API_URL + "/").catch((error) => {
            generating = false;
            globalError(error);
            return;
        });

        objects = objects.data.objects.filter((object) => object.enabled);

        let length = objects.length + 1;
        for (var i = 0; i < length - 1; i++) {
            let object = objects[i];
            if (object.enabled) {
                toast.set(id, {
                    msg:
                        'Generating final clip for "<strong>' +
                        object.name +
                        '</strong>"',
                    next: i / length,
                });
                await axios
                    .get(API_URL + "/results/generate-result/" + object.name)
                    .catch((error) => {
                        generating = false;
                        globalError(error);
                        return;
                    });
            }
        }

        toast.set(id, {
            msg: "Generating final montage",
            next: length - 1 / length,
        });
        await axios.get(API_URL + "/results/generate-result").catch((error) => {
            generating = false;
            globalError(error);
            return;
        });

        toast.pop(id);
        toast.push("Result generated!", {
            theme: greenOptions,
        });
        result = true;
        generating = false;
    }

    function changeMenu(newMode) {
        if (generating) {
            globalError("Wait for the end of the generation.");
            return;
        }

        if (newMode === mode) {
            return;
        }
        if (newMode === "cuts" && !cutsDone) {
            return;
        }
        if (newMode === "result" && !result) {
            return;
        }

        mode = newMode;
        dispatch("mode", newMode);
    }
</script>

<div class={"main" + (generating ? " menu-gen" : "")}>
    <div class="menu">
        <button
            class={mode === "clips" ? "selected" : ""}
            on:click={() => changeMenu("clips")}>CLIPS</button
        >
        <p>|</p>
        <button
            class={(mode === "cuts" ? "selected" : "") +
                " " +
                (cutsDone ? "" : "grey")}
            on:click={() => changeMenu("cuts")}>CUTS</button
        >
        <p>|</p>
        <button
            class={mode === "music" ? "selected" : ""}
            on:click={() => changeMenu("music")}>MUSIC</button
        >
        <p>|</p>
        <button
            class={mode === "effects" ? "selected" : ""}
            on:click={() => changeMenu("effects")}>EFFECTS</button
        >
        <p>|</p>
        <button
            class={(mode === "result" ? "selected" : "") +
                " " +
                (result ? "" : "grey")}
            on:click={() => changeMenu("result")}>RESULT</button
        >
    </div>
    {#key mode}
        <div class="end">
            {#if mode === "clips"}
                <button on:click={generateCuts}>GENERATE CUTS</button>
            {:else if mode === "cuts"}
                <button class={cutsDone ? "" : "grey"} on:click={generateResult}
                    >GENERATE RESULT</button
                >
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
    .menu-gen {
        filter: brightness(0.6);
    }
    .end {
        height: 50px;
        width: 30%;
        display: flex;
        margin-right: 0;
        margin-left: auto;
    }
    .end > button {
        width: 100%;
        border-radius: 0 0 20px 0;
        animation-name: cycle-color;
        animation-duration: 2s;
        animation-iteration-count: infinite;
        animation-direction: alternate;
    }

    button {
        text-align: center;
        border: none;
        border-radius: 0px;
        outline: none;
        cursor: pointer;
        border: none;
        color: var(--white-text);
        margin-bottom: 0;
        font-size: large;
        font-size: 1.5em;
        background-color: var(--secondary);
    }
    button:hover {
        transition: all 0.2s;
        background-color: var(--terciary-hover);
    }
    .grey {
        color: #8c8c8c;
    }
    .selected {
        background-color: var(--primary);
    }
    @media (max-width: 700px) {
        .main {
            flex-direction: column;
            border-radius: 0% !important;
        }
        .menu {
            width: 100%;
            height: 30px;
        }
        .end {
            width: 100%;
            margin-top: 10px;
        }
        button {
            font-size: smaller;
            border-radius: 0% !important;
        }
        p {
            display: none;
        }
    }
    @media (max-width: 500px) {
        button {
            font-size: small;
        }
    }

    @keyframes cycle-color {
        50% {
            color: var(--white-text);
        }

        100% {
            color: #ffc312;
        }
    }
</style>