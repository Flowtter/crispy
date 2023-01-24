<style>
	.component {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		width: 90%;
		height: 100%;
		background-color: #323c53;
		margin: 0 auto;
		border-radius: 20px;
	}
</style>

<script>
	import Filters from "./Filters.svelte";
</script>

<div class="component">
	<br />
	<Filters name="filters" filterRoute="filters" />
</div>
