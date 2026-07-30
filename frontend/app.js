// Dynamic API Base URL resolution:
// - Uses window.API_CONFIG.backendUrl if specified.
// - If running on separate local dev frontend port 8080 or file:// protocol, targets http://127.0.0.1:8000.
// - For all single-server deployments (Render, DuckDNS, custom domain, port 8000, etc.), uses relative path "".
const API_BASE = (function() {
    if (window.API_CONFIG && window.API_CONFIG.backendUrl) {
        return window.API_CONFIG.backendUrl;
    }
    if (window.location.port === "8080" || window.location.protocol === "file:") {
        return "http://127.0.0.1:8000";
    }
    return "";
})();

let trainPairs = [];

// Toast Notification Logic
function showToast(message) {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    // Tailwind classes for stylish dark toast with slide-in animation
    toast.className = "bg-slate-800 text-white px-6 py-3 rounded shadow-lg transform translate-x-[120%] transition-transform duration-300 flex items-center gap-3 border-l-4 border-blue-500";
    toast.innerHTML = `<i class="fa-solid fa-bell text-blue-400"></i> <span class="font-medium tracking-wide">${message}</span>`;

    container.appendChild(toast);

    // Trigger slide in
    setTimeout(() => {
        toast.classList.remove("translate-x-[120%]");
    }, 10);

    // Remove after 4s
    setTimeout(() => {
        toast.classList.add("translate-x-[120%]");
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Show developer branding on load
document.addEventListener("DOMContentLoaded", () => {
    showToast("Developed by Suhail 🚀");
    fetchStats();
});

// ── Stats Dashboard ──────────────────────────────────────────────────────────
async function fetchStats() {
    try {
        const res  = await fetch(`${API_BASE}/get-stats`);
        if (!res.ok) return;
        const data = await res.json();

        const trains  = data.total_trains        || 0;
        const minutes = data.total_time_saved_minutes || 0;
        const docs    = data.total_generated     || 0;

        document.getElementById("stat-generated").textContent = docs;

        const hrs = (minutes / 60);
        document.getElementById("stat-time").textContent =
            hrs < 1 ? `${minutes} min` : `${hrs.toFixed(1)} hrs`;
    } catch (_) {
        // Stats panel failure is non-critical — silently ignore
    }
}

// DOM Elements
const upTrainInput = document.getElementById("upTrain");
const downTrainInput = document.getElementById("downTrain");
const scheduleTypeInput = document.getElementById("scheduleType");
const addPairBtn = document.getElementById("addPairBtn");
const pdfFileInput = document.getElementById("pdfFile");
const uploadContent = document.getElementById("uploadContent");
const uploadLoading = document.getElementById("uploadLoading");
const pairsTableBody = document.getElementById("pairsTableBody");
const pairCount = document.getElementById("pairCount");
const generateBtn = document.getElementById("generateBtn");
const generateIcon = document.getElementById("generateIcon");
const generateText = document.getElementById("generateText");

// Schedule Type change handler for dynamic inputs (TOD date inputs & Sections input)
if (scheduleTypeInput) {
    scheduleTypeInput.addEventListener("change", () => {
        const todContainer = document.getElementById("todDateContainer");
        const sectionsContainer = document.getElementById("sectionsContainer");
        
        if (todContainer) {
            const isTod = scheduleTypeInput.value === "tod" || scheduleTypeInput.value === "tod_wcb";
            todContainer.classList.toggle("hidden", !isTod);
        }
        if (sectionsContainer) {
            sectionsContainer.classList.toggle("hidden", scheduleTypeInput.value !== "sections");
        }
    });
}

// Initialize and Render Table
function renderTable() {
    pairsTableBody.innerHTML = "";

    if (trainPairs.length === 0) {
        pairsTableBody.innerHTML = `
            <tr>
                <td colspan="4" class="py-8 text-center text-gray-400">No pairs added yet.</td>
            </tr>
        `;
        generateBtn.disabled = true;
        pairCount.textContent = "0 Pairs";
        return;
    }

    trainPairs.forEach((pair, index) => {
        const up = pair.up || "-";
        const down = pair.down || "-";
        let typeLabel = '<span class="bg-emerald-100 text-emerald-800 text-xs font-semibold px-2.5 py-0.5 rounded">ETE</span>';
        if (pair.schedule_type === "sections") {
            let secInfo = "";
            if (pair.up_sections || pair.dn_sections) {
                secInfo = `<span class="text-[10px] text-blue-700 block font-normal mt-0.5">EXCL: ${pair.up_sections || '-'} / ${pair.dn_sections || '-'}</span>`;
            }
            typeLabel = `<span class="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded">Sections</span>${secInfo}`;
        } else if (pair.schedule_type === "wcb") {
            typeLabel = '<span class="bg-purple-100 text-purple-800 text-xs font-semibold px-2.5 py-0.5 rounded">WCB</span>';
        } else if (pair.schedule_type === "tod") {
            let uptoInfo = "";
            if (pair.up_upto || pair.dn_upto) {
                uptoInfo = `<span class="text-[10px] text-amber-700 block font-normal mt-0.5">UPTO: ${pair.up_upto || '-'} / ${pair.dn_upto || '-'}</span>`;
            }
            typeLabel = `<span class="bg-amber-100 text-amber-800 text-xs font-semibold px-2.5 py-0.5 rounded">TOD</span>${uptoInfo}`;
        } else if (pair.schedule_type === "tod_wcb") {
            let uptoInfo = "";
            if (pair.up_upto || pair.dn_upto) {
                uptoInfo = `<span class="text-[10px] text-pink-700 block font-normal mt-0.5">UPTO: ${pair.up_upto || '-'} / ${pair.dn_upto || '-'}</span>`;
            }
            typeLabel = `<span class="bg-pink-100 text-pink-800 text-xs font-semibold px-2.5 py-0.5 rounded">TOD+WCB</span>${uptoInfo}`;
        }

        const tr = document.createElement("tr");
        tr.className = "hover:bg-gray-50 transition-colors";
        tr.innerHTML = `
            <td class="py-3 px-4 text-gray-500">${index + 1}</td>
            <td class="py-3 px-4 font-medium text-gray-800">${up} ${typeLabel}</td>
            <td class="py-3 px-4 font-medium text-gray-800">${down}</td>
            <td class="py-3 px-4 text-right">
                <button onclick="removePair(${index})" class="text-red-500 hover:text-red-700 transition-colors" title="Remove Pair">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </td>
        `;
        pairsTableBody.appendChild(tr);
    });

    generateBtn.disabled = false;
    pairCount.textContent = `${trainPairs.length} Pair${trainPairs.length > 1 ? 's' : ''}`;
}

window.removePair = function (index) {
    trainPairs.splice(index, 1);
    renderTable();
};

// Smart Train Number Parsing
upTrainInput.addEventListener("blur", () => {
    const val = upTrainInput.value.trim();
    if (!val) return;
    
    // Auto-split formats like 12601-02 or 12409/10
    const match = val.match(/^(\d{5})[-/](\d{2,5})$/);
    if (match) {
        const up = match[1];
        const suffix = match[2];
        const down = suffix.length === 5 ? suffix : up.substring(0, 5 - suffix.length) + suffix;
        
        upTrainInput.value = up;
        downTrainInput.value = down;
    }
});

// Add Manual Pair
addPairBtn.addEventListener("click", () => {
    const up = upTrainInput.value.trim();
    let down = downTrainInput.value.trim();
    const type = scheduleTypeInput ? scheduleTypeInput.value : "normal";

    if (!up || !down) {
        alert("Both UP and DOWN Train numbers are required!");
        return;
    }

    if (down && down.length === 2 && up.length === 5) {
        down = up.substring(0, 3) + down;
    }

    const isTod = type === "tod" || type === "tod_wcb";
    const upUpto = (isTod && document.getElementById("upUptoDate")) ? document.getElementById("upUptoDate").value.trim() : "";
    const dnUpto = (isTod && document.getElementById("dnUptoDate")) ? document.getElementById("dnUptoDate").value.trim() : "";

    const upSections = (type === "sections" && document.getElementById("upSectionsInput")) ? document.getElementById("upSectionsInput").value.trim() : "";
    const dnSections = (type === "sections" && document.getElementById("dnSectionsInput")) ? document.getElementById("dnSectionsInput").value.trim() : "";

    const newPair = {
        up: up,
        down: down,
        schedule_type: type,
        up_upto: upUpto,
        dn_upto: dnUpto,
        up_sections: upSections,
        dn_sections: dnSections
    };
    trainPairs.push(newPair);

    upTrainInput.value = "";
    downTrainInput.value = "";
    if (document.getElementById("upUptoDate")) document.getElementById("upUptoDate").value = "";
    if (document.getElementById("dnUptoDate")) document.getElementById("dnUptoDate").value = "";
    if (document.getElementById("upSectionsInput")) document.getElementById("upSectionsInput").value = "";
    if (document.getElementById("dnSectionsInput")) document.getElementById("dnSectionsInput").value = "";
    renderTable();
});

// PDF Upload Handling
pdfFileInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.type !== "application/pdf") {
        alert("Please upload a valid PDF file.");
        pdfFileInput.value = "";
        return;
    }

    await handlePDFUpload(file);
    pdfFileInput.value = ""; // Reset for re-uploading same file if needed
});

async function handlePDFUpload(file) {
    uploadContent.classList.add("hidden");
    uploadLoading.classList.remove("hidden");

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`${API_BASE}/extract-trains`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || "Failed to extract trains");
        }

        const data = await response.json();

        if (data.extracted_pairs && data.extracted_pairs.length > 0) {
            const formattedPairs = data.extracted_pairs.map(p => ({
                up: p[0],
                down: p.length > 1 ? p[1] : "",
                schedule_type: "normal"
            }));
            trainPairs = [...trainPairs, ...formattedPairs];
            renderTable();
            showToast(`Extracted ${data.extracted_pairs.length} train pairs successfully!`);
        } else {
            alert("No 5-digit train numbers found in the PDF.");
        }
    } catch (error) {
        alert(`Error extracting PDF: ${error.message}`);
    } finally {
        uploadContent.classList.remove("hidden");
        uploadLoading.classList.add("hidden");
    }
}

function scrollToConsoleBottom() {
    const consoleEl = document.getElementById("liveConsole");
    if (consoleEl) {
        consoleEl.scrollTop = consoleEl.scrollHeight;
        requestAnimationFrame(() => {
            consoleEl.scrollTop = consoleEl.scrollHeight;
        });
    }
}

// Live Console Stream Helper
function addConsoleLog(text, type = "info") {
    const consoleEl = document.getElementById("liveConsole");
    if (!consoleEl) return;

    const div = document.createElement("div");
    if (type === "pair") {
        div.className = "text-sky-300 font-bold mt-1";
    } else if (type === "url") {
        div.className = "text-amber-300 font-mono text-[10px]";
    } else if (type === "success") {
        div.className = "text-emerald-400 font-medium";
    } else if (type === "http") {
        div.className = "text-blue-400 font-semibold mt-1";
    } else if (type === "warn") {
        div.className = "text-red-400 font-semibold";
    } else {
        div.className = "text-slate-300";
    }

    div.textContent = text;
    consoleEl.appendChild(div);
    scrollToConsoleBottom();
}

// ── Password Protection Logic ────────────────────────────────────────────────
const passwordModal = document.getElementById("passwordModal");
const modalBox = document.getElementById("modalBox");
const authPasswordInput = document.getElementById("authPasswordInput");
const passwordError = document.getElementById("passwordError");
const passwordForm = document.getElementById("passwordForm");
const cancelAuthBtn = document.getElementById("cancelAuthBtn");
const togglePasswordBtn = document.getElementById("togglePasswordBtn");
const togglePasswordIcon = document.getElementById("togglePasswordIcon");

function openPasswordModal() {
    if (!passwordModal) return;
    authPasswordInput.value = "";
    if (passwordError) passwordError.classList.add("hidden");
    passwordModal.classList.remove("hidden");
    setTimeout(() => {
        passwordModal.classList.remove("opacity-0");
        if (modalBox) {
            modalBox.classList.remove("scale-95");
            modalBox.classList.add("scale-100");
        }
        authPasswordInput.focus();
    }, 10);
}

function closePasswordModal() {
    if (!passwordModal) return;
    passwordModal.classList.add("opacity-0");
    if (modalBox) {
        modalBox.classList.remove("scale-100");
        modalBox.classList.add("scale-95");
    }
    setTimeout(() => {
        passwordModal.classList.add("hidden");
    }, 300);
}

if (togglePasswordBtn) {
    togglePasswordBtn.addEventListener("click", () => {
        const isPassword = authPasswordInput.type === "password";
        authPasswordInput.type = isPassword ? "text" : "password";
        togglePasswordIcon.className = isPassword ? "fa-solid fa-eye-slash" : "fa-solid fa-eye";
    });
}

if (cancelAuthBtn) {
    cancelAuthBtn.addEventListener("click", closePasswordModal);
}

// Cryptographic SHA-256 hash helper (One-Way Encryption)
async function getSha256Hash(text) {
    const encoder = new TextEncoder();
    const data = encoder.encode(text);
    const hashBuffer = await crypto.subtle.digest("SHA-256", data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

// Encrypted Password SHA-256 Hash (Never reveals plain text in Inspect Element!)
const AUTH_KEY_HASH = "4f7482b7436a52f3b1c18c4b187d0df4a3ca4d6253703ae323a06566eef6f2de";

if (passwordForm) {
    passwordForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const entered = authPasswordInput.value.trim();
        if (!entered) {
            if (passwordError) passwordError.classList.remove("hidden");
            authPasswordInput.focus();
            return;
        }

        const enteredHash = await getSha256Hash(entered);
        if (enteredHash !== AUTH_KEY_HASH) {
            if (passwordError) passwordError.classList.remove("hidden");
            if (modalBox) {
                modalBox.classList.add("border-red-500");
                setTimeout(() => modalBox.classList.remove("border-red-500"), 1000);
            }
            authPasswordInput.select();
            return; // STRICTLY STOP HERE IF HASH DOES NOT MATCH
        }

        if (passwordError) passwordError.classList.add("hidden");
        closePasswordModal();
        startScheduleGenerationStream(entered);
    });
}

// ── Anti-Inspect Security Shield (Blocks F12, Ctrl+Shift+I, Right-Click) ─────
document.addEventListener("contextmenu", (e) => e.preventDefault());
document.addEventListener("keydown", (e) => {
    if (
        e.key === "F12" ||
        (e.ctrlKey && e.shiftKey && (e.key === "I" || e.key === "i" || e.key === "J" || e.key === "j" || e.key === "C" || e.key === "c")) ||
        (e.ctrlKey && (e.key === "U" || e.key === "u" || e.key === "S" || e.key === "s"))
    ) {
        e.preventDefault();
        return false;
    }
});

// Generate Button Click -> Prompt Password Modal
generateBtn.addEventListener("click", () => {
    if (trainPairs.length === 0) return;
    openPasswordModal();
});

// Real-Time Schedule Generation Stream
async function startScheduleGenerationStream(userPassword = "") {
    // Loading State
    generateBtn.disabled = true;
    generateIcon.className = "fa-solid fa-circle-notch fa-spin mr-2";
    generateText.textContent = "Processing...";

    const statusEl = document.getElementById("terminal-status");
    if (statusEl) statusEl.textContent = "BUSY • FETCHING";

    const consoleEl = document.getElementById("liveConsole");
    if (consoleEl) consoleEl.innerHTML = ""; // reset log window

    try {
        const payload = {
            pairs: trainPairs,
            auth_password: userPassword
        };

        const response = await fetch(`${API_BASE}/generate-schedule-stream`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (response.status === 401) {
            addConsoleLog("[SECURITY ERROR] 🔒 Incorrect Access Key! Access Denied.", "warn");
            showToast("❌ Incorrect Security Access Key! Access Denied.");
            openPasswordModal();
            if (passwordError) passwordError.classList.remove("hidden");
            return;
        }

        if (!response.ok) {
            addConsoleLog(`[ERROR] Server error: ${response.statusText}`, "warn");
            throw new Error("Failed to connect to schedule generation stream.");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";
        let finalFilename = null;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const chunks = buffer.split("\n\n");
            buffer = chunks.pop(); // keep last incomplete line in buffer

            for (const chunk of chunks) {
                const trimmed = chunk.trim();
                if (trimmed.startsWith("data: ")) {
                    try {
                        const data = JSON.parse(trimmed.slice(6));

                        if (data.error) {
                            addConsoleLog(`[ERROR] ${data.error}`, "warn");
                            showToast(`Error: ${data.error}`);
                            return;
                        }

                        if (data.text) {
                            addConsoleLog(data.text, data.type || "info");
                        }

                        if (data.done && data.filename) {
                            finalFilename = data.filename;
                        }
                    } catch (e) {
                        console.error("Error parsing stream chunk:", e);
                    }
                }
            }
        }

        if (finalFilename) {
            // Automatically trigger file download
            const downloadUrl = `${API_BASE}/download-file/${finalFilename}`;
            const a = document.createElement("a");
            a.href = downloadUrl;
            a.download = "IRCTC_Live_Schedules.docx";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            showToast("Schedule Generated Successfully! ✅");
            fetchStats();
        }

    } catch (error) {
        alert(`Error generating document: ${error.message}`);
    } finally {
        generateBtn.disabled = false;
        generateIcon.className = "fa-solid fa-file-word mr-2";
        generateText.textContent = "Generate Word Document";
        if (statusEl) statusEl.textContent = "STREAM READY";
        scrollToConsoleBottom();
    }
}
