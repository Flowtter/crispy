<script>
    import Filters from "./filters.svelte";
</script>

<div class="component">
    <br />
    <Filters name="filters" filterRoute="filters" />
</div>

<style>
    .component {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 90%;
        height: 100%;
        background-color: var(--primary);
        /* align to center */
        margin: 0 auto;
        border-radius: 20px;
    }
</style>
