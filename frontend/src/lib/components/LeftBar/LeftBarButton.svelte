<script>
    import axios from "axios";
    import { createEventDispatcher } from "svelte";
    import { API_URL } from "../../../variables";

    const dispatch = createEventDispatcher();

    export let type;
    let letter = type == "reload" ? "R" : "S";
    function handleClick() {
        axios.get(API_URL + "/" + type).then((response) => {
            if (type == "reload") {
                dispatch("message", response.data);
            } else {
                dispatch("send");
            }
        });
    }
</script>

<button class={type} on:click={handleClick}>{letter}</button>

<style>
    button {
        cursor: pointer;
        margin: 0;
        width: 40px;
        height: 40px;
        border: none;
        outline: none;
        border-radius: 0px;
        color: var(--white-text);
    }
    .reload {
        background-color: var(--exit);
    }
    .reload:hover {
        background-color: var(--exit-hover);
    }
    .reload:active {
        background-color: var(--exit-selected);
    }
    .send {
        background-color: var(--terciary);
        border-radius: 0 0 15px 0;
    }
    .send:hover {
        background-color: var(--terciary-hover);
    }
    .send:active {
        background-color: var(--terciary-variant);
    }
</style>
