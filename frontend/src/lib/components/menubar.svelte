<script>
    import "../../constants";
    import axios from "axios";
    import { API_URL } from "../../constants";
    import { createEventDispatcher } from "svelte";
    import { toast } from "@zerodevx/svelte-toast";

    const dispatch = createEventDispatcher();

    export let mode;
    let cuts = false;
    let cutsDone = false;
    let result = false;

    let greenOptions = {
        "--toastBackground": "#2ecc71",
        "--toastBarBackground": "#27ae60",
    };
    let redOptions = {
        "--toastBackground": "#F56565",
        "--toastBarBackground": "#C53030",
    };
    let generating = false;

    async function lock() {
        let gen = await axios.get(API_URL + "/generating");
        console.log("generating rn", gen.data, generating);
        gen = gen.data || generating;
        if (gen) {
            console.log("pushing already");
            toast.push("Already generating", {
                duration: 3000,
                theme: redOptions,
            });
        }
        console.log("so gen is", gen);
        return gen;
    }

    async function generateCuts() {
        toast.pop(0);
        if (await lock()) return;
        generating = true;
        cutsDone = false;
        cuts = true;
        dispatch("clear", {});
        let objects = await axios.get(API_URL);
        toast.push("Generating cuts! Check the cut menu to see them", {
            duration: 5000,
        });
        for (let object of objects.data.objects) {
            let first = true;
            if (object.enabled) {
                if (first) first = false;
                else await new Promise((resolve) => setTimeout(resolve, 1500));

                const id = toast.push(
                    'Generating cut for "<strong>' + object.name + '</strong>"',
                    {
                        dismissable: false,
                        initial: 0,
                        next: 0,
                    }
                );
                let cuts = await axios.get(
                    API_URL + "/objects/" + object.name + "/generate-cuts"
                );
                cuts = cuts.data;
                dispatch("cuts", {
                    file: object.name,
                    cuts: cuts,
                });
                // allow the backend to send the videos to the browser
                // before rendering the next video
                toast.pop(id);
                toast.push(
                    'Cuts for "<strong>' + object.name + '</strong>" generated',
                    {
                        theme: greenOptions,
                    }
                );
            }
        }
        toast.push(
            "All cuts generated! You can now generate the montage in the cut menu > Generate result",
            {
                duration: 15000,
                theme: {
                    "--toastBackground": "#4299E1",
                    "--toastBarBackground": "#2B6CB0",
                },
            }
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

        let objects = await axios.get(API_URL);
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
                await axios.get(API_URL + "/generate-result/" + object.name);
            }
            console.log(i, length);
        }

        toast.set(id, {
            msg: "Generating final montage",
            next: length - 1 / length,
        });
        await axios.get(API_URL + "/generate-result");

        toast.pop(id);
        toast.push("Result generated!", {
            theme: greenOptions,
        });
        result = true;
        generating = false;
    }

    function changeMenu(newMode) {
        console.log("changeMenu", newMode, cuts, result);
        if (newMode === mode) {
            return;
        }
        if (newMode === "cuts" && !cuts) {
            return;
        }
        if (newMode === "result" && !result) {
            return;
        }

        mode = newMode;
        dispatch("mode", newMode);
    }
</script>

<div class="main">
    <div class="menu">
        <button
            class={mode === "clips" ? "selected" : ""}
            on:click={() => changeMenu("clips")}>CLIPS</button
        >
        <p>|</p>
        <button
            class={(mode === "cuts" ? "selected" : "") +
                " " +
                (cuts ? "" : "grey")}
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
        background-color: var(--terciary-hover);
    }
    .grey {
        color: #8c8c8c;
    }
    .selected {
        background-color: var(--primary);
    }
</style>
