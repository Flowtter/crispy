<script>
	import "./constants";
	import Cut from "./lib/components/cut.svelte";
	import Gallery from "./lib/components/gallery.svelte";
	import Menubar from "./lib/components/menubar.svelte";
	import Video from "./lib/components/video.svelte";

	let cuts = {};

	function addCut(event) {
		console.log(cuts);
		cuts[event.detail.file] = event.detail.cuts;
		console.log("add cut:", cuts);
	}
</script>

<main>
	<div class="main-container">
		<!-- <Video filename={"0"} shortname={"0"} /> -->
		<Menubar mode="clips" on:cuts={addCut} />
		<div class="content">
			<!-- <Gallery /> -->
			<Cut {cuts} />
		</div>
	</div>
</main>

<style>
	main {
		background-color: var(--primary);
		color: var(--white-text);
	}
	.main-container {
		max-width: 1600px;
		margin: 0 auto;
	}
	.content {
		background-color: var(--secondary);
		border-radius: 20px 20px 0 0;
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
</style>
