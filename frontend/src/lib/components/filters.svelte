<script>
    import { toast } from "@zerodevx/svelte-toast";
    import axios from "axios";
    import { onMount } from "svelte";
    import { API_URL } from "../../constants";
    import Filter from "./filter.svelte";

    import { createEventDispatcher } from "svelte";
    const dispatch = createEventDispatcher();

    export let toastId;
    export let name;

    export let filterRoute;

    async function saved() {
        function error(filter) {
            toast.push({
                msg: "Please fill all fields in " + filter,
                theme: {
                    "--toastBackground": "#FF5252",
                    "--toastBarBackground": "#C53030",
                },
            });
        }
        for (let filter in filters) {
            if (filters[filter].box) {
                if (
                    filter === "scale" &&
                    (filters[filter].h === null ||
                        filters[filter].w === null ||
                        filters[filter].h === "" ||
                        filters[filter].w === "")
                ) {
                    error(filter);
                    return;
                }
                if (
                    filters[filter].value === null ||
                    filters[filter].value === ""
                ) {
                    error(filter);
                    return;
                }
            }
        }
        toast.pop(toastId);
        toast.push({
            msg: "Saved!",
            duration: 2500,
            theme: {
                "--toastBackground": "#2ecc71",
                "--toastBarBackground": "#27ae60",
            },
        });
        dispatch("save", {});
        await saveFilters();
    }

    async function readFilters() {
        console.log(API_URL + "/" + filterRoute + "/read");
        let read = await axios.get(API_URL + "/" + filterRoute + "/read");
        filters = read.data;
    }
    async function saveFilters() {
        let j = JSON.stringify(filters);
        await axios.post(API_URL + "/" + filterRoute + "/save", j, {
            headers: { "Content-Type": "application/json" },
        });
    }
    onMount(readFilters);
    let filters = undefined;
</script>

{#if filters}
    <div>
        <p>{name}</p>
        <Filter
            bind:activated={filters["blur"].box}
            text="blur"
            mode="one"
            firstPlaceholder="value"
            bind:firstInput={filters["blur"].value}
        />
        <Filter
            bind:activated={filters["scale"].box}
            text="scale"
            mode="two"
            firstPlaceholder="width"
            secondPlaceholder="height"
            bind:firstInput={filters["scale"].w}
            bind:secondInput={filters["scale"].h}
        />

        <Filter bind:activated={filters["hflip"].box} text="hflip" />
        <Filter bind:activated={filters["vflip"].box} text="vflip" />

        <Filter
            bind:activated={filters["brightness"].box}
            text="brightness"
            mode="one"
            firstPlaceholder="value"
            bind:firstInput={filters["brightness"].value}
        />
        <Filter
            bind:activated={filters["saturation"].box}
            text="saturation"
            mode="one"
            firstPlaceholder="value"
            bind:firstInput={filters["saturation"].value}
        />
        <Filter
            bind:activated={filters["zoom"].box}
            text="zoom"
            mode="one"
            firstPlaceholder="value"
            bind:firstInput={filters["zoom"].value}
        />
        <Filter bind:activated={filters["grayscale"].box} text="grayscale" />

        <!-- <Filter bind:activated={activated[0]} text="saturation" mode="one" /> -->
        <button on:click={saved}>Save</button>
    </div>
{/if}

<style>
    button {
        /* FIXME: bad usage of negatove margin */
        margin-top: -40px;
        float: right;
        text-align: center;
        padding: 12px 20px;
        border: none;
        border-radius: 0px;
        background-color: var(--terciary);
        outline: none;
        cursor: pointer;
        border: none;
        color: var(--white-text);
        margin-bottom: 0;
        font-size: large;
        font-size: 1.25em;
        border-radius: 5px;
    }
    button:hover {
        transition: all 0.2s;
        background-color: var(--terciary-hover);
    }
    p {
        text-align: center;
        margin: 0px;
    }
</style>
