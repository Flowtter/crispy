<script>
    import { createEventDispatcher } from "svelte";
    const dispatch = createEventDispatcher();

    export let maxi;
    export let currentPage;

    function change(next) {
        if (next) {
            if (currentPage == maxi - 1) return;
            currentPage++;
        } else {
            if (currentPage == 0) return;
            currentPage--;
        }
        dispatch("change", currentPage);
    }
</script>

<div class="end-menu">
    <button on:click={() => change(false)}>&lt</button>
    <p>{currentPage}/{maxi - 1}</p>
    <button on:click={() => change(true)}>&gt</button>
</div>

<style>
    .end-menu {
        display: table;
        width: 20vw;
        /* align center */
        margin: auto;
    }
    .end-menu > button {
        width: 40px;
        display: table-cell;
    }
    .end-menu > p {
        display: table-cell;
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
        background-color: var(--terciary-hover);
    }
</style>
