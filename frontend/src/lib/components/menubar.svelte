<script>
    export let endUrl;
</script>

<div class="main">
    <div class="menu">
        <button>CLIPS</button>
        <p>|</p>
        <button>CUTS</button>
        <p>|</p>
        <button>MUSIC</button>
        <p>|</p>
        <button>EFFECTS</button>
        <p>|</p>
        <button>RESULT</button>
    </div>
    {#key endUrl}
        {#if endUrl}
            <div class="end">
                <button>end</button>
            </div>
        {/if}
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
        background-color: var(--primary);
    }
</style>
