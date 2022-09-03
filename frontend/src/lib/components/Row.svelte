<script>
    export let activated;
    export let text;
    export let mode = undefined;
    export let firstInput = undefined;
    export let firstPlaceholder = undefined;
    export let secondInput = undefined;
    export let secondPlaceholder = undefined;
</script>

<div class="row">
    <p class="text">{text}</p>
    <input type="checkbox" bind:checked={activated} />
    {#if mode === "one"}
        <input
            type="number"
            bind:value={firstInput}
            placeholder={firstPlaceholder}
        />
    {:else if mode === "two"}
        <input
            type="number"
            bind:value={firstInput}
            placeholder={firstPlaceholder}
        />
        <input
            type="number"
            bind:value={secondInput}
            placeholder={secondPlaceholder}
        />
    {/if}
</div>

<style>
    .text {
        grid-column: span 2;
        text-align: right;
    }
    .row {
        display: grid;
        width: 100%;
        grid-template-columns: repeat(12, 1fr);
        margin-top: -10px;
    }
    input {
        /* center */
        margin: auto;
        height: 20px;
    }
    ::placeholder {
        color: #979797;
        opacity: 1;
    }
    input[type="checkbox"] {
        grid-column: span 2;
        -ms-transform: scale(1.5);
        -webkit-transform: scale(1.5);
        transform: scale(1.5);
        padding: 10px;
        filter: invert(100%) hue-rotate(18deg) brightness(1.7);
        accent-color: #9b59b6;
    }
    input[type="number"] {
        grid-column: span 3;
        width: 80%;
    }
</style>
