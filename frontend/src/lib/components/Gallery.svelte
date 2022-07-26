<script>
    import axios from "axios";
    import { onMount } from "svelte";
    import { flip } from "svelte/animate";

    import { API_URL, globalError, globalWarning } from "../../constants.js";
    import Video from "./Video.svelte";

    export const fetch = () => {
        axios
            .get(API_URL)
            .then((response) => {
                const res = response.data;
                list = [];

                if (res.objects.length >= 15) {
                    globalWarning(
                        "You have more than 70 clips. Some browser won't accept it."
                    );
                }
                for (let i = 0; i < res.objects.length; i++) {
                    var name = res.objects[i].name;
                    var fullname = name;
                    if (name.length > 20) {
                        name =
                            name.substring(0, 10) +
                            "..." +
                            name.substring(name.length - 10);
                    }
                    list.push({
                        name: name,
                        fullname: fullname,
                        id: i,
                    });
                }
            })
            .catch((error) => {
                globalError(error);
            });
    };
    onMount(fetch);

    let list;
    let hovering = false;

    const drop = (event, target) => {
        event.dataTransfer.dropEffect = "move";
        const start = parseInt(event.dataTransfer.getData("text/plain"));
        const newTracklist = list;

        if (start < target) {
            newTracklist.splice(target + 1, 0, newTracklist[start]);
            newTracklist.splice(start, 1);
        } else {
            newTracklist.splice(target, 0, newTracklist[start]);
            newTracklist.splice(start + 1, 1);
        }

        list = newTracklist;
        hovering = null;

        var tmp = [];
        for (let i = 0; i < list.length; i++) {
            tmp.push({ name: list[i].fullname });
        }

        axios
            .post(API_URL + "/reorder", JSON.stringify(tmp), {
                headers: { "Content-Type": "application/json" },
            })
            .catch((error) => {
                globalError(error);
            });
    };

    const dragstart = (event, i) => {
        event.dataTransfer.effectAllowed = "move";
        event.dataTransfer.dropEffect = "move";
        const start = i;
        event.dataTransfer.setData("text/plain", start);
    };
</script>

{#if list}
    <div class="gallery">
        {#each list as n, index (n.id)}
            <div
                class="list-item"
                animate:flip={{ duration: 400 }}
                draggable={true}
                on:dragstart={(event) => dragstart(event, index)}
                on:drop|preventDefault={(event) => drop(event, index)}
                ondragover="return false"
                on:dragenter={() => (hovering = index)}
                class:is-active={hovering === index}
            >
                <Video
                    filename={n.fullname}
                    shortname={n.name}
                    videoUrl={API_URL + "/objects/" + n.fullname + "/video"}
                />
            </div>
        {/each}
    </div>
{/if}

<style>
    .gallery {
        justify-content: center;
        border-radius: 4px;

        flex-wrap: wrap;
        justify-content: center;
        display: flex;
        text-align: center;
        width: 95%;
        /* align the div */
        margin: auto;
    }

    .list-item {
        padding: 0.5em 1em;
    }

    .list-item.is-active {
        background-color: var(--secondary);
        border-radius: 4px;
        /* color: #fff; */
    }
</style>
