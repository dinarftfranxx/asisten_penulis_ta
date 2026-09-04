// Endpoint Lokal (PostgreSQL Laptop)
const BACKEND_URL = "http://127.0.0.1:8000/api/cek-teks/";
// const BACKEND_URL = "https://asistenpenulista-production.up.railway.app/api/cek-teks/"; // Endpoint Railway

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
