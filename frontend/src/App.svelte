<script>
	import FinalVideo from "./lib/components/FinalVideo.svelte";
	import Gallery from "./lib/components/Gallery.svelte";
	import LeftBar from "./lib/components/LeftBar/LeftBar.svelte";
	import Log from "./lib/components/Log.svelte";
	import Video from "./lib/components/Video.svelte";

	var display = "hide";
	var init = "init";
	setTimeout(() => {
		display = "";
		init = "hide";
	}, 500);

	function handleReload(event) {
		location.reload();
	}

	let log;

	function startLogging() {
		log = true;
	}

	let video;
	function startVideo() {
		video = true;
	}
</script>

<main class={display}>
	{#if !log}
		<LeftBar on:message={handleReload} on:send={startLogging} />
	{/if}
	<Gallery />
	{#if log}
		<Log on:video={startVideo} />
	{/if}
	{#if video}
		<FinalVideo />
	{/if}
</main>
<div class={init} />

<style>
	main {
		background-color: var(--primary);
		color: var(--white-text);
		min-width: 100%;
		min-height: 100%;
	}
	:global(body) {
		margin: 0;
		padding: 0;
	}
	* {
		--primary: #141b23;
		--secondary: #1b222f;
		--terciary: #f5a52a;
		--terciary-variant: #c57f15;
		--terciary-hover: #d48c1f;

		--exit: #e74c3c;
		--exit-hover: #dd4332;
		--exit-selected: #c0392b;

		--white-text: #f0f0f0;
	}
	.hide {
		display: none;
	}
	.init {
		height: 100vh;
		width: 100vw;
		background-color: var(--primary);
	}
</style>
