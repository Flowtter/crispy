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
	.menu-generating {
		filter: brightness(0.6);
	}
	.end {
		height: 50px;
		width: 30%;
		display: flex;
		margin-right: 0;
		margin-left: auto;
	}
	.end > button {
		width: 100%;
		border-radius: 0 0 20px 0;
		animation-name: cycle-color;
		animation-duration: 2s;
		animation-iteration-count: infinite;
		animation-direction: alternate;
	}

	button {
		text-align: center;
		border: none;
		border-radius: 0px;
		outline: none;
		cursor: pointer;
		border: none;
		color: var(--white-text);
		margin-bottom: 0;
		font-size: large;
		font-size: 1.5em;
		background-color: var(--secondary);
	}
	button:hover {
		transition: all 0.2s;
		background-color: var(--terciary-hover);
	}
	.selected {
		background-color: var(--primary);
	}
	@media (max-width: 700px) {
		.main {
			flex-direction: column;
			border-radius: 0% !important;
		}
		.menu {
			width: 100%;
			height: 30px;
		}
		.end {
			width: 100%;
			margin-top: 10px;
		}
		button {
			font-size: smaller;
			border-radius: 0% !important;
		}
		p {
			display: none;
		}
	}
	@media (max-width: 500px) {
		button {
			font-size: small;
		}
	}

	@keyframes cycle-color {
		50% {
			color: var(--white-text);
		}

		100% {
			color: #ffc312;
		}
	}
</style>

<script>
	import "../../constants";
	import axios from "axios";
	import { API_URL, globalInfo, globalError, globalSuccess, sleep } from "../../constants";
	import { createEventDispatcher } from "svelte";
	import { toast } from "@zerodevx/svelte-toast";

	const dispatch = createEventDispatcher();

	export let mode;
	export let generating;

	const waitForJobs = async (url, id, msg) => {
		let count = -1;
		while (true) {
			let request = await axios.get(url);
			if (request.status != 200) {
				globalError("Error while waiting for the jobs to finish");
				return;
			}
			const jobs = request.data;
			if (Array.isArray(jobs)) {
				if (jobs.every((highlight) => highlight.status == "completed")) {
					break;
				}
			} else {
				if (jobs.status == "completed") {
					break;
				}
			}
			if (id) {
				// count how many times "completed" is in the status
				const completed = jobs.filter((highlight) => highlight.status == "completed").length;
				if (count != completed) {
					toast.set(id, {
						msg: msg,
						next: completed / jobs.length,
					});
					count = completed;
				}
			}

			await sleep(1500);
		}
	};

	async function generateSegments() {
		if (generating) {
			globalError("Already generating.");
			return;
		}
		new Promise(function (resolve, reject) {
			toast.pop(0);

			dispatch("changeGenerating", true);

			let id = globalInfo("Generating Segments!", {
				next: 0,
				initial: 0,
				dismissable: false,
			});

			axios.post(API_URL + "/highlights/segments/generate").catch((error) => {
				toast.pop(0);
				globalError(error);
				dispatch("changeGenerating", false);
				return;
			});

			waitForJobs(API_URL + "/highlights/segments/generate/status", id, "Generating Segments!").then(() => {
				toast.pop(0);
				globalSuccess("Segments generated!");
				globalInfo("You can now generate the result.");
				dispatch("changeGenerating", false);
				resolve();
			});
		});

		dispatch("changeMode", "segments");
	}

	async function generateResult() {
		if (generating) {
			globalError("Already generating.");
			return;
		}
		toast.pop(0);

		dispatch("changeGenerating", true);

		let toastId = globalInfo("Generating Results!", {
			initial: 0,
			next: 0,
			dismissable: false,
		});

		let request = await axios.post(API_URL + "/results/generate/highlights");

		if (request.status !== 200) {
			toast.pop(0);
			globalError("Error while generating result.");
			dispatch("changeGenerating", false);
			return;
		}
		await waitForJobs(API_URL + "/results/generate/highlights/status", toastId, "Generating Results!");
		toast.pop(0);
		globalSuccess("All results generated! Generating final video...");
		globalInfo("Generating Final video! This may take a while...", {
			initial: 0,
			dismissable: false,
		});

		request = await axios.post(API_URL + "/results/generate/video");

		if (request.status !== 200) {
			toast.pop(0);
			globalError("Error while generating result.");
			dispatch("changeGenerating", false);
			return;
		}

		let id = request.data._id;

		await waitForJobs(API_URL + `/results/job/${id}`);
		toast.pop(0);
		globalSuccess("Result generated!");

		dispatch("changeGenerating", false);
		dispatch("changeMode", "result");
	}

	function changeMenu(newMode) {
		if (generating) {
			globalError("Wait for current job to finish.");
			return;
		}

		if (newMode === mode) return;
		mode = newMode;
		dispatch("changeMode", newMode);
	}
</script>

<div class={"main" + (generating ? " menu-generating" : "")}>
	<div class="menu">
		<button class={mode === "clips" ? "selected" : ""} on:click={() => changeMenu("clips")}>CLIPS</button>
		<p>|</p>
		<button class={mode === "segments" ? "selected" : ""} on:click={() => changeMenu("segments")}>SEGMENTS</button>
		<p>|</p>
		<button class={mode === "musics" ? "selected" : ""} on:click={() => changeMenu("musics")}>MUSICS</button>
		<p>|</p>
		<button class={mode === "effects" ? "selected" : ""} on:click={() => changeMenu("effects")}>EFFECTS</button>
		<p>|</p>
		<button class={mode === "result" ? "selected" : ""} on:click={() => changeMenu("result")}>RESULT</button>
	</div>
	{#key mode}
		<div class="end">
			{#if mode === "clips"}
				<button on:click={generateSegments}>GENERATE SEGMENTS</button>
			{:else if mode === "segments"}
				<button on:click={generateResult}>GENERATE RESULT</button>
			{/if}
		</div>
	{/key}
</div>
