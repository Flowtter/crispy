<script>
    import AudioPlayer from "./Audio.svelte";
    import { API_URL, globalError } from "../../constants.js";

    //
    import axios from "axios";
    import { onMount } from "svelte";

    export const fetch = () => {
        axios
            .get(API_URL + "/")
            .then((response) => {
                const res = response.data;
                list = [];
                for (let i = 0; i < res.musics.length; i++) {
                    var name = res.musics[i].name;
                    list.push({
                        name: name,
                        id: i,
                    });
                }
                console.log(list);
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
            tmp.push({ name: list[i].name });
        }

        axios.post(API_URL + "/musics/reorder", JSON.stringify(tmp), {
            headers: { "Content-Type": "application/json" },
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
    <div>
        {#each list as n, index (n.id)}
            <div
                class="list-item"
                draggable={true}
                on:dragstart={(event) => dragstart(event, index)}
                on:drop|preventDefault={(event) => drop(event, index)}
                ondragover="return false"
                on:dragenter={() => (hovering = index)}
                class:is-active={hovering === index}
            >
                <AudioPlayer src={API_URL + "/musics/" + n.name} />
                <!-- <div>{n.name}</div> -->
            </div>
        {/each}
    </div>
{/if}
