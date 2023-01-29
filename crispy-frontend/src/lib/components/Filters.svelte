<style>
	div {
		background-color: transparent;
	}
	button {
		margin-top: -60px;
		margin-bottom: 20px;
		float: right;
		text-align: center;
		padding: 12px 20px;
		border: none;
		border-radius: 0px;
		background-color: var(--terciary);
		outline: none;
		cursor: pointer;
		border: none;
		color: var(--white-text);
		font-size: large;
		font-size: 1.25em;
		border-radius: 5px;
	}
	button:hover {
		transition: all 0.2s;
		background-color: var(--terciary-hover);
	}
	p {
		text-align: center;
		margin: 0px;
	}
</style>

<script>
	import axios from "axios";
	import { onMount } from "svelte";
	import { API_URL, globalError, globalSuccess } from "../../constants";
	import Filter from "./RowFilter.svelte";

	import { toast } from "@zerodevx/svelte-toast";

	export let toastId;
	export let name;
	export let filterRoute;

	let defaultFilters = {
		blur: {
			box: false,
			value: null,
		},
		hflip: {
			box: false,
		},
		vflip: {
			box: false,
		},
		saturation: {
			box: false,
			value: null,
		},
		brightness: {
			box: false,
			value: null,
		},
		zoom: {
			box: false,
			value: null,
		},
		grayscale: {
			box: false,
		},
	};

	let filters = undefined;
	async function saveFilters() {
		let json = JSON.stringify(filters);
		await axios
			.post(API_URL + filterRoute, json, {
				headers: { "Content-Type": "application/json" },
			})
			.catch((error) => {
				globalError(error);
			});
	}

	async function verifyFilterValues() {
		for (let filter in filters) {
			if (filters[filter].box) {
				if (filters[filter].value === null || filters[filter].value === "") {
					globalError("Value cannot be empty!");
					return;
				}
			}
		}
		toast.pop(toastId);
		globalSuccess("Filters saved!");
		await saveFilters();
	}

	async function readFilters() {
		let read = await axios.get(API_URL + filterRoute).catch((error) => {
			globalError(error);
		});
		let tmpFilter = read.data.filters || {};
		for (let filter in tmpFilter) {
			if (typeof tmpFilter[filter] === "boolean") {
				tmpFilter[filter] = {
					box: tmpFilter[filter],
				};
			} else if (!tmpFilter[filter]) {
				tmpFilter[filter] = {
					box: false,
					value: null,
				};
			} else {
				tmpFilter[filter] = {
					box: true,
					value: tmpFilter[filter],
				};
			}
		}
		for (let filter in defaultFilters) {
			if (!(filter in tmpFilter)) {
				tmpFilter[filter] = defaultFilters[filter];
			}
		}
		filters = tmpFilter;
	}
	onMount(readFilters);
</script>

{#if filters}
	<div>
		<p>{name}</p>
		<Filter
			bind:activated={filters["blur"].box}
			text="blur"
			mode="one"
			firstPlaceholder="10"
			bind:firstInput={filters["blur"].value}
		/>

		<Filter bind:activated={filters["hflip"].box} text="hflip" />
		<Filter bind:activated={filters["vflip"].box} text="vflip" />

		<Filter
			bind:activated={filters["brightness"].box}
			text="brightness"
			mode="one"
			firstPlaceholder="0.5"
			bind:firstInput={filters["brightness"].value}
		/>
		<Filter
			bind:activated={filters["saturation"].box}
			text="saturation"
			mode="one"
			firstPlaceholder="1.2"
			bind:firstInput={filters["saturation"].value}
		/>
		<Filter
			bind:activated={filters["zoom"].box}
			text="zoom"
			mode="one"
			firstPlaceholder="1.5"
			bind:firstInput={filters["zoom"].value}
		/>
		<Filter bind:activated={filters["grayscale"].box} text="grayscale" />

		<button on:click={verifyFilterValues}>Save</button>
	</div>
{/if}
