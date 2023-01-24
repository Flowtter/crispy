<style>
	.gallery {
		justify-content: center;
		border-radius: 4px;

		flex-wrap: wrap;
		justify-content: center;
		display: flex;
		text-align: center;
		width: 95%;
		margin: auto;
	}

	.list-item {
		padding: 0.5em 1em;
	}

	.list-item.is-active {
		background-color: var(--secondary);
		border-radius: 4px;
	}
</style>

<script>
	import axios from "axios";
	import { onMount } from "svelte";
	import { flip } from "svelte/animate";

	import { API_URL, globalError, globalWarning } from "../../constants.js";
	import Video from "./Video.svelte";

	let list;
	export const fetch = () => {
		axios
			.get(API_URL + "/highlights")
			.then((response) => {
				const res = response.data;

				if (res.length >= 70) {
					globalWarning("You have more than 70 clips. Some browser won't accept it.");
				}

				list = [];
				for (let i = 0; i < res.length; i++) {
					var name = res[i].name;
					if (name.length > 20) {
						name = name.substring(0, 10) + "..." + name.substring(name.length - 10);
					}
					list.push({
						name: name,
						fullname: res[i].name,
						id: res[i]._id,
					});
				}
			})
			.catch((error) => {
				globalError(error);
			});
	};
	onMount(fetch);

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
		hovering = false;

		axios
			.post(
				API_URL + "/highlights/reorder",
				JSON.stringify({
					highlight_id: list[start].id,
					other_highlight_id: list[target].id,
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
	<div class="gallery">
		{#each list as n, index (n.id)}
			<div
				class="list-item"
				animate:flip={{ duration: 400 }}
				draggable={true}
				ondragover="return false"
				on:dragstart={(event) => dragstart(event, index)}
				on:drop|preventDefault={(event) => drop(event, index)}
				on:dragenter={() => (hovering = index)}
				class:is-active={hovering === index}
			>
				<Video
					id={n.id}
					shortname={n.name}
					videoUrl={API_URL + `/highlights/${n.id}/snippet`}
					posterUrl={API_URL + `/highlights/${n.id}/thumbnail`}
				/>
			</div>
		{/each}
	</div>
{/if}
