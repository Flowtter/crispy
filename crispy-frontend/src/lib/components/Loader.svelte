<script>
	export let isHealthy = false;
</script>

<style>
	.spinner {
		border: 4px solid var(--secondary);
		border-top: 4px solid var(--white-text);
		border-radius: 50%;
		width: 40px;
		height: 40px;
		animation: spin 1s linear infinite;
		margin: auto;
	}

	@keyframes spin {
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
	}
	.loader {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 100vh;
	}
</style>

{#if !isHealthy}
	<div class = "loader">
		<div class="spinner"></div>
	</div>
{/if}
