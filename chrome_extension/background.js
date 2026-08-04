// Background service worker - tidak terpengaruh CSP halaman
// Semua request ke backend dilakukan di sini

const BACKEND_URL = "https://asistenpenulista-production.up.railway.app/api/cek-teks/";

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "cek-teks") {
        fetch(BACKEND_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ teks: request.teks })
        })
        .then(response => response.json())
        .then(data => sendResponse({ success: true, data: data }))
        .catch(error => sendResponse({ success: false, error: error.message }));

        return true; // Penting: biarkan channel terbuka untuk async response
    }
});
