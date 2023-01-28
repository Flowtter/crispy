<style>
	.disabled {
		filter: brightness(35%);
	}
	.audio-container {
		margin: auto;
		width: 90%;
		background-color: var(--secondary);
		border-radius: 20px;
		margin-bottom: 50px;
	}
	audio {
		width: 90%;
		margin: auto;
		display: block;
	}

	p {
		font-size: 1rem;
		font-weight: bold;
		text-align: center;
		margin: auto;
		width: 100%;
		padding-top: 10px;
		padding-bottom: 10px;
		color: var(--white-text);
	}
	.trailing-menu {
		margin-top: 5px;
		height: 50px;
		width: 100%;
		display: flex;
	}

	.only {
		border-radius: 0 0 20px 20px !important;
		width: 100%;
	}

	button {
		text-align: center;
		border: none;
		border-radius: 0px;
		background-color: var(--terciary);
		outline: none;
		cursor: pointer;
		border: none;
		color: var(--white-text);
		margin-bottom: 0;
		font-size: large;
	}
	button:hover {
		transition: all 0.2s;
		background-color: var(--terciary-hover);
	}
</style>

<script>
	import { API_URL, globalError } from "../../constants.js";
	import axios from "axios";
	import { onMount } from "svelte";
	export let name;
	export let id;

	let volume = 0.5;
	let enabled = "enabled";

	function switchStatus() {
		let url = API_URL + `/musics/${id}/switch-status`;
		axios.post(url).catch((error) => {
			globalError(error);
		});
		enabled = !enabled;
	}

	const setIsEnabled = () => {
		let url = API_URL + `/musics/${id}`;
		axios
			.get(url)
			.then((response) => {
				enabled = response.data.enabled;
			})
			.catch((error) => {
				globalError(error);
			});
	};
	onMount(setIsEnabled);
</script>

<div class={enabled ? "" : "disabled"}>
	<div class="audio-container" draggable={false}>
		<p>{name}</p>
		<audio src={API_URL + `/musics/${id}/music`} controls bind:volume>
			<track kind="captions" />
		</audio>
		<div class="trailing-menu">
			<button class="only" on:click={switchStatus}>{enabled ? "HIDE" : "SHOW"}</button>
		</div>
	</div>
</div>
