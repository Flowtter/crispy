import { toast } from "@zerodevx/svelte-toast";

const API_URL = "http://127.0.0.1:1337"



function globalError(e) {
    toast.push({
        msg: e,
        duration: 10000,
        theme: {
            "--toastBackground": "#FF5252",
            "--toastBarBackground": "#C53030",
        },
    });
}

function globalWarning(e) {
    toast.push({
        msg: e,
        duration: 6000,
        theme: {
            "--toastBackground": "#bec01a",
            "--toastBarBackground": "#a1a322",

        },
    });

}

function globalInfo(e) {
    toast.push({
        msg: e,
        duration: 15000,
        theme: {

            "--toastBackground": "#4299E1",
            "--toastBarBackground": "#2B6CB0",

        },
    });
}

export { API_URL, globalError, globalWarning, globalInfo }
