<style>
	p {
		padding-top: 10px;
	}
	.gallery {
		justify-content: center;
		border-radius: 4px;

		justify-content: center;
		text-align: center;
		width: 95%;
		margin: auto;
	}
	.group {
		display: flex;
		flex-wrap: wrap;
		margin-bottom: 20px;
		justify-content: center;
	}
	.content {
		background-color: var(--background);
		border-radius: 10px;
		width: auto;
	}
</style>

<script>
	import { API_URL, sleep, globalSuccess } from "../../constants.js";
	import Video from "./Video.svelte";
	import ChangePage from "./ChangePage.svelte";
	import axios from "axios";

	export let generating;

	let allBlocks = [];
	let currentPage = 0;
	let blocksInPage = [];
	// FIXME: blockCount should not be needed
	// but svelte crashes if we're checking the length of blocksInPage
	// https://github.com/sveltejs/svelte/issues/5789
	let blockCount = 0;

	const setPagination = () => {
		blockCount = 0;
		blocksInPage = [];

		allBlocks.sort((a, b) => {
			return a.highlight.index - b.highlight.index;
		});

		for (let i = 0; i < allBlocks.length; i += 10) {
			blocksInPage.push(allBlocks.slice(i, i + 10));
			blockCount++;
		}
	};

	const addSegmentToBlock = async (highlight) => {
		const segments = await axios.get(API_URL + `/highlights/${highlight._id}/segments`);
		allBlocks.push({
			highlight: highlight,
			segments: segments.data,
		});
	};

	const mainLoop = async () => {
		const renderedHighlights = [];
		while (true) {
			let highlights = await axios.get(API_URL + "/highlights/segments/generate/status");
			let newHighlights = false;
			const promises = [];
			for (let i = 0; i < highlights.data.length; i++) {
				const highlight = highlights.data[i];
				if (highlight.status == "completed" && !renderedHighlights.includes(highlight._id)) {
					newHighlights = true;
					renderedHighlights.push(highlight._id);
					promises.push(addSegmentToBlock(highlight));
					if (generating) {
						// short delay to make sure the toast is rendered
						await sleep(100);
						globalSuccess(`Segments for <strong>${highlight.name}</strong> generated!`);
					}
				}
			}
			await Promise.all(promises);

			if (newHighlights) setPagination();

			if (highlights.data.every((highlight) => highlight.status == "completed")) {
				break;
			}
			await sleep(5000);
		}
	};
	mainLoop();

	function changePage(event) {
		currentPage = event.detail;
		window.scrollTo(0, 0);
	}
</script>

<main>
	{#key blockCount}
		{#if blockCount}
			<div class="gallery">
				{#key currentPage}
					{#each blocksInPage[currentPage] as blocks}
						<div class="content">
							<p>{blocks.highlight.name}.mp4</p>
							<div class="group">
								{#if blocks.segments.length == 0}
									<p style="color: var(--text);">No segments</p>
								{:else}
									{#each Object.entries(blocks.segments) as [index]}
										<Video
											shortname={blocks.segments[index].name}
											id={blocks.segments[index]._id}
											videoUrl={API_URL + `/segments/${blocks.segments[index]._id}/video`}
											posterUrl={API_URL + `/highlights/${blocks.highlight._id}/thumbnail`}
											editable={false}
											isSegment={true}
										/>
									{/each}
								{/if}
							</div>
						</div>
					{/each}
					<ChangePage {currentPage} maxi={blocksInPage.length} on:change={changePage} />
				{/key}
			</div>
			<br />
		{/if}
	{/key}
</main>
