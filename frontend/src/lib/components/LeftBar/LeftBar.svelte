<script>
    import LeftBarButton from "./LeftBarButton.svelte";
</script>

<div class="bar">
    <LeftBarButton type="reload" on:message />
    <LeftBarButton type="send" on:send />
</div>

<style>
    .bar {
        display: flex;
        position: fixed;
        flex-direction: column;
        justify-content: flex-end;
        align-items: center;
        top: 0;
        left: 0;
    }
</style>
