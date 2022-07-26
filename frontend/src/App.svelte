<script>
	import "./constants";
	import Cut from "./lib/components/cut.svelte";
	import Gallery from "./lib/components/gallery.svelte";
	import Menubar from "./lib/components/menubar.svelte";
	import Result from "./lib/components/result.svelte";
	import Effects from "./lib/components/effects.svelte";

	import { SvelteToast, toast } from "@zerodevx/svelte-toast";
	import Music from "./lib/components/music.svelte";
	import { globalInfo } from "./constants";

	let cuts = [];
	let last_cut = null;

	let mode = "clips";

	function addCut(event) {
		let file = event.detail.file;
		let cut = event.detail.cuts;
		last_cut = cut;
		for (let i = 0; i < cuts.length; i++) {
			let f = cuts[i].file;
			if (f === file) {
				cuts[i] = { file, cut };
				return;
			}
		}
		cuts.push({ file, cut });
	}

	function changeMode(event) {
		mode = event.detail;
	}

	function clearCuts(event) {
		cuts = [];
	}
	toast.push("Thanks for using Crispy!", {
		duration: 5000,
	});
	globalInfo(
		"Activate the videos you want in your montage, then generate cuts!"
	);
</script>

<!-- <Demo /> -->
<div class="top">
	<SvelteToast options={{ initial: 0, intro: { y: -64 } }} target="new" />
</div>

<main>
	<SvelteToast />
	<div class="main-container">
		<Menubar
			{mode}
			on:cuts={addCut}
			on:mode={changeMode}
			on:clear={clearCuts}
		/>
		<div class="content">
			<br />
			{#key mode}
				{#if mode === "clips"}
					<Gallery />
				{:else if mode === "cuts"}
					{#key last_cut}
						<Cut {cuts} />
					{/key}
				{:else if mode === "result"}
					<Result />
				{:else if mode === "music"}
					<Music />
				{:else if mode === "effects"}
					<Effects />
				{/if}
			{/key}
		</div>
	</div>
</main>

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
</style>
