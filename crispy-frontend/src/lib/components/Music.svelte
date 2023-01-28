<script>
	import AudioPlayer from "./Audio.svelte";
	import { API_URL, globalError } from "../../constants.js";
	import axios from "axios";
	import { onMount } from "svelte";

	let list;
	export const getMusics = () => {
		axios
			.get(API_URL + "/musics")
			.then((response) => {
				const res = response.data;
				list = [];
				for (let i = 0; i < res.length; i++) {
					var name = res[i].name;
					list.push({
						name: name,
						id: res[i]._id,
					});
				}
			})
			.catch((error) => {
				globalError(error);
			});
	};
	onMount(getMusics);

	let hovering = false;
	const drop = (event, target) => {
		event.dataTransfer.dropEffect = "move";
		const start = parseInt(event.dataTransfer.getData("text/plain"));
		if (start === target) {
			return;
		}

		const newTracklist = list;

		if (start < target) {
			newTracklist.splice(target + 1, 0, newTracklist[start]);
			newTracklist.splice(start, 1);
		} else {
			newTracklist.splice(target, 0, newTracklist[start]);
			newTracklist.splice(start + 1, 1);
		}

		list = newTracklist;
		hovering = null;
		axios
			.post(
				API_URL + "/musics/reorder",
				JSON.stringify({
					music_id: list[start].id,
					other_music_id: list[target].id,
				}),
				{
					headers: {
						"Content-Type": "application/json",
					},
				}
			)
			.catch((error) => {
				globalError(error);
			});
	};

	const dragstart = (event, i) => {
		event.dataTransfer.effectAllowed = "move";
		event.dataTransfer.dropEffect = "move";
		const start = i;
		event.dataTransfer.setData("text/plain", start);
	};
</script>

{#if list}
	<div>
		{#each list as n, index (n.id)}
			<div
				class="list-item"
				draggable={true}
				on:dragstart={(event) => dragstart(event, index)}
				on:drop|preventDefault={(event) => drop(event, index)}
				ondragover="return false"
				on:dragenter={() => (hovering = index)}
				class:is-active={hovering === index}
			>
				<AudioPlayer name={n.name} id={n.id} />
			</div>
		{/each}
	</div>
{/if}
