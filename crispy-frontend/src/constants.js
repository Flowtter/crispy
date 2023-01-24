import { toast } from "@zerodevx/svelte-toast";

const API_URL = "http://127.0.0.1:7821";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function globalError(e, args) {
	return toast.push({
		msg: e,
		duration: 10000,
		theme: {
			"--toastBackground": "#FF5252",
			"--toastBarBackground": "#A53030",
		},
		...args,
	});
}

function globalWarning(e, args) {
	return toast.push({
		msg: e,
		duration: 6000,
		theme: {
			"--toastBackground": "#bec01a",
			"--toastBarBackground": "#a1a322",
		},
		...args,
	});
}

function globalInfo(e, args) {
	return toast.push({
		msg: e,
		duration: 15000,
		theme: {
			"--toastBackground": "#4299E1",
			"--toastBarBackground": "#2B6CB0",
		},
		...args,
	});
}

function globalSuccess(e, args) {
	return toast.push({
		msg: e,
		duration: 5000,
		theme: {
			"--toastBackground": "#009432",
			"--toastBarBackground": "#A3CB38",
		},
		...args,
	});
}

export { API_URL, globalError, globalWarning, globalInfo, globalSuccess, sleep };
