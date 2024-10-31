<style>
	:root {
		--toastContainerTop: 60px;
	}
	main {
		background-color: var(--background);
		color: var(--white-text);
	}
	.main-container {
		max-width: 1600px;
		margin: 0 auto;
	}
	.content {
		background-color: var(--content);
		border-radius: 20px 20px 0 0;
		min-height: calc(100vh - 70px);
	}
	:global(body) {
		margin: 0;
		padding: 0;
	}
	* {
		--background: #131d35;

		--content: #242d44;

		--primary: #2e364a;
		--secondary: #404b62;

		--terciary: #404b62;
		--terciary-hover: #2e364a;

		--white-text: #f0f0f0;
	}
	.top {
		--toastContainerTop: 0.5rem;
		--toastContainerRight: 0.5rem;
		--toastContainerBottom: auto;
		--toastContainerLeft: 0.5rem;
		--toastWidth: 100%;
		--toastMinHeight: 2rem;
		--toastPadding: 0 0.5rem;
		font-size: 0.9em;
	}
	@media (min-width: 40rem) {
		.top {
			--toastContainerRight: auto;
			--toastContainerLeft: calc(50vw - 20rem);
			--toastWidth: 40rem;
		}
	}

	@media (max-width: 1000px) {
		.top {
			--toastWidth: 90vw;
			--toastContainerLeft: 3vw;
		}
	}

	@media (max-width: 900px) {
		.content {
			border-radius: 0% !important;
		}
		.right {
			--toastContainerTop: 150px;
			--toastWidth: 90vw;
			--toastContainerRight: 5vw;

			--toastContainerTop: auto;
			--toastContainerBottom: 30px;

			font-size: 0.7em;
		}
	}
</style>

<script>
	import "./constants";
	import Loader from "./lib/components/Loader.svelte";
	import Segments from "./lib/components/Segments.svelte";
	import Gallery from "./lib/components/Gallery.svelte";
	import Menubar from "./lib/components/Menubar.svelte";
	import Result from "./lib/components/Result.svelte";
	import Effects from "./lib/components/Effects.svelte";
	import Musics from "./lib/components/Musics.svelte";

	import { SvelteToast, toast } from "@zerodevx/svelte-toast";
	import axios from "axios";
	import { onMount } from "svelte";
	import { globalInfo, globalError, API_URL } from "./constants";

	let mode = "clips";
	let generating = false;
	let healthy = false;
	let healthCheckIndex = 0;

	onMount(() => {
		if (!healthy) {
			const interval = setInterval(checkHealth, 5000);
			checkHealth();
			return () => clearInterval(interval);
		}
	});

	async function checkHealth() {
		if (healthy) {
			return;
		}
		try {
			const response = await axios.get(API_URL + "/health");
			if (response.status === 200) {
				healthy = true;
				if (healthCheckIndex > 0) {
					toast.pop(0);
				}
				globalInfo("Activate the videos you want in your montage, then generate segments!");
			}
		} catch (error) {
			healthy = false;
			if (healthCheckIndex % 12 === 1) {
				globalError("Can't connect to the server. Please check it is running and ready.", { duration: 10000 });
			}
		}

		healthCheckIndex++;
	}

	function changeMode(event) {
		mode = event.detail;
	}
	function changeGenerating(event) {
		generating = event.detail;
	}

	toast.push("Thanks for using Crispy!", { duration: 2500 });
</script>

<main>
		<div class="top">
			<SvelteToast options={{ initial: 0, intro: { y: -64 } }} target="new" />
		</div>
		<div class="right">
			<SvelteToast />
		</div>
		<div class="main-container">
			<Menubar {healthy} {mode} {generating} on:changeMode={changeMode} on:changeGenerating={changeGenerating} />
			{#if healthy}
				<div class="content">
					<br />
					{#key mode}
						{#if mode === "clips"}
							<Gallery />
						{:else if mode === "segments"}
							<Segments {generating} />
						{:else if mode === "result"}
							<Result />
						{:else if mode === "musics"}
							<Musics />
						{:else if mode === "effects"}
							<Effects />
						{/if}
					{/key}
				</div>
			{:else}
				<Loader {healthy} />
			{/if}
		</div>
</main>
