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
`;
document.head.appendChild(styleSheet);

// 2. BIKIN KOTAK UI MELAYANG
const uiContainer = document.createElement('div');
uiContainer.id = 'asisten-penulis-ui';
document.body.appendChild(uiContainer);

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
        item.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="font-size: 10px; font-weight: 800; color: #ff4757; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">${error.jenis_error}</div>
                <button class="btn-abaikan" data-key="${key.replace(/"/g, '&quot;')}">&times;</button>
            </div>
            <strong style="color: #d63031; font-size: 15px; text-decoration: line-through; text-decoration-color: rgba(214, 48, 49, 0.5);">${error.teks_bermasalah}</strong><br>
            <div style="font-size: 13px; color: var(--ap-desc); margin-top: 6px; line-height: 1.5; font-weight: 500;">${error.keterangan}</div>
        `;
        uiContainer.appendChild(item);
    });

    // Pasang event listener untuk tombol abaikan
    const btns = uiContainer.querySelectorAll('.btn-abaikan');
    btns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const key = e.currentTarget.getAttribute('data-key');
            ignoredErrors.add(key);
            tampilkanUI(daftarError); // Re-render UI
        });
    });

    // Munculkan kotaknya!
    uiContainer.style.display = 'block';
}

// 5. NEMBAK API BACKEND
async function cekTypoKeBackend(teks) {
    if (!teks.trim()) {
        uiContainer.style.display = 'none';
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
            tampilkanUI(data.hasil);
        } else {
            uiContainer.style.display = 'none'; // Sembunyikan kalau aman
        }
    } catch (error) {
        console.error("Gagal ke backend:", error);
    }
}

// 6. PASANG TELINGA
document.addEventListener("keyup", debounce((event) => {
    const elemen = event.target;
    if (elemen.tagName === 'INPUT' || elemen.tagName === 'TEXTAREA' || elemen.isContentEditable) {
        let teksKetik = elemen.tagName === 'INPUT' || elemen.tagName === 'TEXTAREA' ? elemen.value : elemen.innerText;
        cekTypoKeBackend(teksKetik);
    }
}, 1000));