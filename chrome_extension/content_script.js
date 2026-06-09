// chrome_extension/content_script.js
console.log("%c🚀 ASISTEN PENULIS SIAP DENGAN UI MELAYANG! 🚀", "color: white; background: blue; font-size: 14px; font-weight: bold; padding: 4px;");

// 1. INJECT CUSTOM CSS UNTUK TEMA UNIVERSAL & SCROLLBAR
const styleSheet = document.createElement("style");
styleSheet.innerText = `
    /* CSS Variables untuk Tema Universal (Frosted Acrylic) */
    #asisten-penulis-ui {
        --ap-bg: rgba(255, 255, 255, 0.92);
        --ap-text: #2d3436;
        --ap-item-bg: rgba(245, 246, 250, 0.9);
        --ap-item-border: rgba(0, 0, 0, 0.04);
        --ap-item-hover: #ffffff;
        --ap-border: rgba(0, 0, 0, 0.08);
        --ap-shadow: 0 16px 40px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0,0,0,0.05);
        --ap-title: #2d3436;
        --ap-desc: #636e72;
        --ap-btn: #b2bec3;
        --ap-scroll-track: rgba(0, 0, 0, 0.04);
        --ap-scroll-thumb: rgba(0, 0, 0, 0.15);
        --ap-scroll-thumb-hover: rgba(0, 0, 0, 0.25);
        
        /* Base Styling */
        position: fixed;
        bottom: 24px;
        right: 24px;
        width: 340px;
        background: var(--ap-bg);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid var(--ap-border);
        border-radius: 16px;
        box-shadow: var(--ap-shadow);
        z-index: 999999;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        padding: 20px;
        display: none;
        max-height: 450px;
        overflow-y: auto;
        color: var(--ap-text);
        animation: slideUpFade 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }

    #asisten-penulis-ui::-webkit-scrollbar { width: 6px; }
    #asisten-penulis-ui::-webkit-scrollbar-track { background: var(--ap-scroll-track); border-radius: 10px; }
    #asisten-penulis-ui::-webkit-scrollbar-thumb { background: var(--ap-scroll-thumb); border-radius: 10px; }
    #asisten-penulis-ui::-webkit-scrollbar-thumb:hover { background: var(--ap-scroll-thumb-hover); }
    
    .asisten-item {
        margin-bottom: 12px; 
        padding: 14px; 
        background: var(--ap-item-bg); 
        border: 1px solid var(--ap-item-border); 
        border-radius: 12px; 
        border-left: 4px solid #ff4757; 
        position: relative;
        transition: transform 0.2s cubic-bezier(0.25, 0.8, 0.25, 1), background 0.2s ease, box-shadow 0.2s ease;
    }
    .asisten-item:hover {
        background: var(--ap-item-hover) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }
    
    .btn-abaikan {
        background: none; 
        border: none; 
        cursor: pointer; 
        color: var(--ap-btn); 
        font-size: 20px; 
        line-height: 1; 
        padding: 0 0 0 10px; 
        margin-top: -4px;
        transition: color 0.2s ease, transform 0.2s ease;
    }
    .btn-abaikan:hover {
        color: #ff4757 !important;
        transform: scale(1.2);
    }
    
    @keyframes slideUpFade {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Highlight Underline System (overlay di atas editor) */
    #ap-highlight-layer {
        position: fixed;
        pointer-events: none;
        z-index: 999998;
        overflow: hidden;
    }

    .ap-underline {
        position: absolute;
        height: 4px;
        background: none;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 6 4' width='6' height='4'%3E%3Cpath d='M0 3 Q 1.5 0, 3 3 T 6 3' stroke='%23ff4757' fill='none' stroke-width='1.2'/%3E%3C/svg%3E");
        background-repeat: repeat-x;
        background-position: bottom;
        opacity: 0.9;
        animation: apUnderlineFadeIn 0.3s ease;
    }

    @keyframes apUnderlineFadeIn {
        from { opacity: 0; transform: scaleX(0.8); }
        to { opacity: 0.85; transform: scaleX(1); }
    }

    /* Tombol Saran Perbaikan (Click-to-Replace) */
    .ap-saran-btn {
        display: inline-block;
        background: rgba(46, 213, 115, 0.1);
        color: #2ed573;
        border: 1px solid rgba(46, 213, 115, 0.3);
        border-radius: 6px;
        padding: 3px 8px;
        margin: 2px 4px 2px 0;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        font-family: inherit;
        transition: all 0.2s ease;
    }
    .ap-saran-btn:hover {
        background: rgba(46, 213, 115, 0.25);
        border-color: rgba(46, 213, 115, 0.5);
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(46, 213, 115, 0.2);
    }
`;
document.head.appendChild(styleSheet);

// 2. BIKIN KOTAK UI MELAYANG
const uiContainer = document.createElement('div');
uiContainer.id = 'asisten-penulis-ui';
document.body.appendChild(uiContainer);

// HIGHLIGHT OVERLAY LAYER (transparan, tidak menghalangi klik)
const highlightLayer = document.createElement('div');
highlightLayer.id = 'ap-highlight-layer';
document.body.appendChild(highlightLayer);

// 3. FUNGSI DEBOUNCE BIAR NGGAK LAG
let timeoutId;
function debounce(func, delay) {
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

// Set untuk menyimpan error yang diabaikan.
const ignoredErrors = new Set();

// Track editor aktif dan error terakhir untuk highlight
let activeEditor = null;
let latestErrors = [];

// 4. FUNGSI UPDATE TAMPILAN KOTAK UI
function tampilkanUI(daftarError) {
    // Filter error yang sudah diabaikan user
    const errorAktif = daftarError.filter(error => {
        const key = (error.teks_bermasalah.toLowerCase() + '|' + (error.konteks || '').toLowerCase()).trim();
        return !ignoredErrors.has(key);
    });

    if (errorAktif.length === 0) {
        uiContainer.style.display = 'none';
        return;
    }

    // Reset isi kotak dengan judul
    uiContainer.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--ap-border); padding-bottom: 12px; margin-bottom: 15px;">
            <h3 style="margin: 0; color: var(--ap-title); font-size: 16px; font-weight: 700; letter-spacing: 0.2px; display: flex; align-items: center; gap: 8px;">
                Asisten Penulis
            </h3>
            <span style="background: rgba(255, 71, 87, 0.1); color: #ff4757; border: 1px solid rgba(255, 71, 87, 0.2); padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700;">
                ${errorAktif.length} Error
            </span>
        </div>
    `;

    // Looping error aktif dan bikin daftarnya
    errorAktif.forEach(error => {
        const item = document.createElement('div');
        item.className = 'asisten-item';
        
        const key = (error.teks_bermasalah.toLowerCase() + '|' + (error.konteks || '').toLowerCase()).trim();
        
        // Buat HTML dengan kelas yang sudah diatur di CSS
        const saranList = parseSaran(error);
        let saranHTML = '';
        if (saranList.length > 0) {
            saranHTML = `<div style="margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; align-items: center;">
                <span style="font-size: 11px; color: var(--ap-desc); font-weight: 600;">Ganti \u2192</span>
                ${saranList.map(s => `<button class="ap-saran-btn" data-kata-lama="${error.teks_bermasalah.replace(/"/g, '&quot;')}" data-kata-baru="${s.replace(/"/g, '&quot;')}">${s}</button>`).join('')}
            </div>`;
        }

        item.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="font-size: 10px; font-weight: 800; color: #ff4757; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">${error.jenis_error}</div>
                <button class="btn-abaikan" data-key="${key.replace(/"/g, '&quot;')}">&times;</button>
            </div>
            <strong style="color: #d63031; font-size: 15px; text-decoration: line-through; text-decoration-color: rgba(214, 48, 49, 0.5);">${error.teks_bermasalah}</strong><br>
            <div style="font-size: 13px; color: var(--ap-desc); margin-top: 6px; line-height: 1.5; font-weight: 500;">${error.keterangan}</div>
            ${saranHTML}
        `;
        uiContainer.appendChild(item);
    });

    // Pasang event listener untuk tombol abaikan
    const btns = uiContainer.querySelectorAll('.btn-abaikan');
    btns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation(); // Cegah auto-hide
            const key = e.currentTarget.getAttribute('data-key');
            ignoredErrors.add(key);
            tampilkanUI(daftarError); // Re-render UI
            gambarUnderline(); // Update underline juga
        });
    });

    // Pasang event listener untuk tombol saran (click-to-replace)
    const saranBtns = uiContainer.querySelectorAll('.ap-saran-btn');
    saranBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation(); // Cegah auto-hide
            const kataLama = e.currentTarget.dataset.kataLama;
            const kataBaru = e.currentTarget.dataset.kataBaru;
            if (gantiKataEditor(kataLama, kataBaru)) {
                // Berhasil diganti! Re-check teks setelah delay singkat
                setTimeout(() => {
                    if (activeEditor) {
                        cekTypoKeBackend(activeEditor.innerText);
                    }
                }, 300);
            }
        });
    });

    // Munculkan kotaknya!
    uiContainer.style.display = 'block';
}

// 5. FUNGSI HIGHLIGHT/UNDERLINE DI EDITOR
function getKataHighlight(error) {
    // Untuk POS Tagging, hanya underline kata pertama (yang bermasalah)
    if (error.jenis_error === 'Tata Bahasa (POS Tagging)') {
        const words = error.teks_bermasalah.trim().split(/\s+/);
        return words[0].replace(/[.,!?;:()\[\]{}"']/g, '');
    }
    return error.teks_bermasalah;
}

function cariPosisiKata(editor, kata) {
    const positions = [];
    const kataLower = kata.toLowerCase();
    const walker = document.createTreeWalker(editor, NodeFilter.SHOW_TEXT);

    while (walker.nextNode()) {
        const textNode = walker.currentNode;
        const text = textNode.textContent.toLowerCase();
        let startIdx = 0;

        while (startIdx < text.length) {
            const idx = text.indexOf(kataLower, startIdx);
            if (idx === -1) break;

            // Cek batas kata (word boundary) agar tidak match di tengah kata lain
            const charSebelum = idx > 0 ? text[idx - 1] : ' ';
            const charSesudah = idx + kataLower.length < text.length ? text[idx + kataLower.length] : ' ';
            const awalKata = /[\s.,!?;:()\[\]{}"'\/-]/.test(charSebelum) || idx === 0;
            const akhirKata = /[\s.,!?;:()\[\]{}"'\/-]/.test(charSesudah) || idx + kataLower.length === text.length;

            if (awalKata && akhirKata) {
                const range = document.createRange();
                range.setStart(textNode, idx);
                range.setEnd(textNode, idx + kataLower.length);

                const rects = range.getClientRects();
                for (const rect of rects) {
                    positions.push({ top: rect.bottom - 2, left: rect.left, width: rect.width });
                }
            }
            startIdx = idx + 1;
        }
    }
    return positions;
}

// Versi khusus untuk POS Tagging: hanya match kata di AWAL kalimat
function cariPosisiAwalKalimat(editor, kata) {
    const positions = [];
    const kataLower = kata.toLowerCase();
    const walker = document.createTreeWalker(editor, NodeFilter.SHOW_TEXT);

    while (walker.nextNode()) {
        const textNode = walker.currentNode;
        const text = textNode.textContent.toLowerCase();
        let startIdx = 0;

        while (startIdx < text.length) {
            const idx = text.indexOf(kataLower, startIdx);
            if (idx === -1) break;

            // Cek word boundary di akhir kata
            const charSesudah = idx + kataLower.length < text.length ? text[idx + kataLower.length] : ' ';
            const akhirKata = /[\s.,!?;:()\[\]{}"'\/-]/.test(charSesudah) || idx + kataLower.length === text.length;

            // Cek apakah di AWAL KALIMAT (bukan di tengah)
            let isAwalKalimat = false;
            if (idx === 0) {
                isAwalKalimat = true; // Awal text node (biasanya awal paragraf di ProseMirror)
            } else {
                // Cek karakter sebelumnya: harus .!? atau newline diikuti spasi
                const textSebelum = text.substring(0, idx).trimEnd();
                if (textSebelum.length > 0 && /[.!?\n]/.test(textSebelum[textSebelum.length - 1])) {
                    isAwalKalimat = true;
                }
            }

            if (isAwalKalimat && akhirKata) {
                const range = document.createRange();
                range.setStart(textNode, idx);
                range.setEnd(textNode, idx + kataLower.length);

                const rects = range.getClientRects();
                for (const rect of rects) {
                    positions.push({ top: rect.bottom - 2, left: rect.left, width: rect.width });
                }
            }
            startIdx = idx + 1;
        }
    }
    return positions;
}

function gambarUnderline() {
    highlightLayer.innerHTML = '';

    if (!activeEditor || !latestErrors || latestErrors.length === 0) {
        highlightLayer.style.display = 'none';
        return;
    }

    const editorRect = activeEditor.getBoundingClientRect();
    highlightLayer.style.top = editorRect.top + 'px';
    highlightLayer.style.left = editorRect.left + 'px';
    highlightLayer.style.width = editorRect.width + 'px';
    highlightLayer.style.height = editorRect.height + 'px';
    highlightLayer.style.display = 'block';

    // Filter error yang sudah diabaikan
    const errorAktif = latestErrors.filter(error => {
        const key = (error.teks_bermasalah.toLowerCase() + '|' + (error.konteks || '').toLowerCase()).trim();
        return !ignoredErrors.has(key);
    });

    errorAktif.forEach(error => {
        const kata = getKataHighlight(error);
        // POS Tagging: hanya highlight kata di awal kalimat
        const positions = error.jenis_error === 'Tata Bahasa (POS Tagging)'
            ? cariPosisiAwalKalimat(activeEditor, kata)
            : cariPosisiKata(activeEditor, kata);

        positions.forEach(pos => {
            const el = document.createElement('div');
            el.className = 'ap-underline';
            el.style.top = (pos.top - editorRect.top) + 'px';
            el.style.left = (pos.left - editorRect.left) + 'px';
            el.style.width = pos.width + 'px';
            highlightLayer.appendChild(el);
        });
    });
}

// 5b. FUNGSI CLICK-TO-REPLACE
function parseSaran(error) {
    // Extract kata saran dari keterangan error
    if (error.jenis_error === 'Typo (Levenshtein)') {
        // Format: "Mungkin maksudmu: imkan, makan"
        const parts = error.keterangan.split(':');
        if (parts.length >= 2) {
            return parts.slice(1).join(':').split(',').map(s => s.trim()).filter(s => s.length > 0);
        }
    } else if (error.jenis_error === 'Bentuk Tidak Baku') {
        // Format: "Bentuk baku: apotek"
        const parts = error.keterangan.split(':');
        if (parts.length >= 2) {
            return [parts.slice(1).join(':').trim()];
        }
    }
    // N-Gram dan POS Tagging tidak punya saran pengganti
    return [];
}

function gantiKataEditor(kataLama, kataBaru) {
    if (!activeEditor) return false;

    const kataLamaLower = kataLama.toLowerCase();
    const walker = document.createTreeWalker(activeEditor, NodeFilter.SHOW_TEXT);

    while (walker.nextNode()) {
        const textNode = walker.currentNode;
        const text = textNode.textContent.toLowerCase();
        const idx = text.indexOf(kataLamaLower);

        if (idx !== -1) {
            // Cek word boundary
            const charSebelum = idx > 0 ? text[idx - 1] : ' ';
            const charSesudah = idx + kataLamaLower.length < text.length ? text[idx + kataLamaLower.length] : ' ';
            const awalKata = /[\s.,!?;:()\[\]{}"'\/-]/.test(charSebelum) || idx === 0;
            const akhirKata = /[\s.,!?;:()\[\]{}"'\/-]/.test(charSesudah) || idx + kataLamaLower.length === text.length;

            if (awalKata && akhirKata) {
                // Pertahankan huruf kapital di awal jika kata aslinya kapital
                let replacement = kataBaru;
                const hurufAsli = textNode.textContent[idx];
                if (hurufAsli === hurufAsli.toUpperCase() && hurufAsli !== hurufAsli.toLowerCase()) {
                    replacement = kataBaru.charAt(0).toUpperCase() + kataBaru.slice(1);
                }

                // Buat Range dan select kata yang mau diganti
                const range = document.createRange();
                range.setStart(textNode, idx);
                range.setEnd(textNode, idx + kataLamaLower.length);

                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);

                // Ganti pakai execCommand agar kompatibel dengan ProseMirror
                document.execCommand('insertText', false, replacement);
                return true;
            }
        }
    }
    return false;
}

// 6. NEMBAK API BACKEND
async function cekTypoKeBackend(teks) {
    if (!teks.trim()) {
        uiContainer.style.display = 'none';
        latestErrors = [];
        gambarUnderline();
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/api/cek-teks/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ teks: teks })
        });

        const data = await response.json();
        
        if (data.hasil && data.hasil.length > 0) {
            latestErrors = data.hasil;
            tampilkanUI(data.hasil);
            gambarUnderline();
        } else {
            latestErrors = [];
            uiContainer.style.display = 'none';
            gambarUnderline();
        }
    } catch (error) {
        console.error("Gagal ke backend:", error);
    }
}

// 7. PASANG TELINGA
document.addEventListener("keyup", debounce((event) => {
    const elemen = event.target;
    if (elemen.tagName === 'INPUT' || elemen.tagName === 'TEXTAREA' || elemen.isContentEditable) {
        // Track editor aktif untuk highlight (hanya contentEditable)
        if (elemen.isContentEditable) {
            activeEditor = elemen.closest('[contenteditable="true"]') || elemen;
        } else {
            activeEditor = null; // INPUT/TEXTAREA tidak support overlay highlight
        }
        let teksKetik = elemen.tagName === 'INPUT' || elemen.tagName === 'TEXTAREA' ? elemen.value : elemen.innerText;
        cekTypoKeBackend(teksKetik);
    }
}, 1000));

// 7b. RE-CHECK SAAT KLIK BALIK KE EDITOR
document.addEventListener("focusin", (event) => {
    const elemen = event.target;
    if (elemen.isContentEditable) {
        const editor = elemen.closest('[contenteditable="true"]') || elemen;
        activeEditor = editor;
        const teks = editor.innerText;
        if (teks.trim()) {
            cekTypoKeBackend(teks);
        }
    }
});

// 8. REPOSISI HIGHLIGHT SAAT SCROLL/RESIZE
let highlightRenderTimeout;
function renderUlangHighlight() {
    clearTimeout(highlightRenderTimeout);
    highlightRenderTimeout = setTimeout(gambarUnderline, 50);
}

window.addEventListener('scroll', renderUlangHighlight, true);
window.addEventListener('resize', renderUlangHighlight);

// 9. AUTO-HIDE SAAT KELUAR DARI EDITOR
function sembunyikanSemua() {
    activeEditor = null;
    latestErrors = [];
    uiContainer.style.display = 'none';
    highlightLayer.innerHTML = '';
    highlightLayer.style.display = 'none';
}

// A. Klik di luar editor & panel → sembunyikan
document.addEventListener('click', (e) => {
    if (uiContainer.contains(e.target)) return;  // Klik di panel
    if (highlightLayer.contains(e.target)) return;
    if (e.target.isContentEditable) return;  // Klik di editor
    if (e.target.closest('[contenteditable="true"]')) return;  // Klik di dalam editor
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    sembunyikanSemua();
});

// B. Editor dihapus dari DOM (SPA navigation) → sembunyikan
const domObserver = new MutationObserver(() => {
    if (activeEditor && !document.contains(activeEditor)) {
        sembunyikanSemua();
    }
});
domObserver.observe(document.body, { childList: true, subtree: true });