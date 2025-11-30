const WARDROBE_KEY = "wardrobe_items_v2";
let lastGeneratedOutfitIds = [];

/* ---------- Helpers ---------- */

function loadWardrobe() {
    try {
        const raw = localStorage.getItem(WARDROBE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch {
        return [];
    }
}

function saveWardrobe(items) {
    try {
        localStorage.setItem(WARDROBE_KEY, JSON.stringify(items));
    } catch (e) {
        alert("Storage full! Please delete some items to add new ones.");
    }
}

async function apiFetch(url, options = {}) {
    const res = await fetch(url, options);
    if (!res.ok) {
        let text;
        try { text = await res.text(); } catch { text = ""; }
        throw new Error(`Request failed: ${res.status} ${text}`);
    }
    try { return await res.json(); } catch { return null; }
}

// === IMAGE COMPRESSION (CRITICAL FOR PERFORMANCE) ===
function resizeImage(file, maxWidth = 600, quality = 0.7) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = (event) => {
            const img = new Image();
            img.src = event.target.result;
            img.onload = () => {
                const canvas = document.createElement("canvas");
                let width = img.width;
                let height = img.height;

                if (width > maxWidth) {
                    height = (height * maxWidth) / width;
                    width = maxWidth;
                }

                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext("2d");
                ctx.drawImage(img, 0, 0, width, height);
                resolve(canvas.toDataURL("image/jpeg", quality));
            };
            img.onerror = (err) => reject(err);
        };
        reader.onerror = (err) => reject(err);
    });
}

/* ---------- Wardrobe Logic ---------- */

function initWardrobePage() {
    const fileInput = document.getElementById("file-input");
    const uploadText = document.getElementById("upload-text");
    const errorEl = document.getElementById("wardrobe-error");
    const emptyEl = document.getElementById("wardrobe-empty");
    const gridEl = document.getElementById("items-grid");

    const initial = loadWardrobe();
    renderWardrobeGrid(initial, gridEl, emptyEl);

    if (!fileInput) return;

    fileInput.addEventListener("change", async () => {
        const file = fileInput.files[0];
        if (!file) return;

        errorEl.classList.add("hidden");
        uploadText.textContent = "Processing...";

        try {
            // Resize before sending to AI or LocalStorage
            const imageDataUrl = await resizeImage(file);

            const meta = await apiFetch("/api/recognize", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({imageDataUrl}),
            });

            const isClothing = meta?.is_clothing;
            const category = meta?.category || "";

            if (!isClothing && category === "not_clothing") {
                errorEl.textContent = "AI didn't detect clothing. Try a clearer photo.";
                errorEl.classList.remove("hidden");
                uploadText.textContent = "Add item";
                fileInput.value = "";
                return;
            }

            const nowIso = new Date().toISOString();
            const item = {
                id: Date.now().toString(),
                imageDataUrl, // Saved compressed
                type: meta?.type || "Item",
                style: meta?.style || "",
                season: meta?.season || "all",
                warmth: meta?.warmth || "",
                colors: meta?.colors || [],
                tags: meta?.tags || [],
                brand: meta?.brand || "",
                usageCount: 0,
                lastUsed: null,
                createdAt: nowIso,
            };

            const updated = [...loadWardrobe(), item];
            saveWardrobe(updated);
            renderWardrobeGrid(updated, gridEl, emptyEl);

        } catch (e) {
            console.error(e);
            errorEl.textContent = "Processing failed. Try again.";
            errorEl.classList.remove("hidden");
        } finally {
            uploadText.textContent = "Add item";
            fileInput.value = "";
        }
    });
}

function renderWardrobeGrid(items, gridEl, emptyEl) {
    gridEl.innerHTML = "";
    if (!items.length) {
        emptyEl.classList.remove("hidden");
        return;
    }
    emptyEl.classList.add("hidden");

    items.forEach((item) => {
        const div = document.createElement("div");
        div.className = "grid-item";
        div.addEventListener("click", () => {
            window.location.href = `/wardrobe/item/${item.id}`;
        });

        const img = document.createElement("img");
        img.src = item.imageDataUrl;
        img.alt = item.type;

        const meta = document.createElement("div");
        meta.className = "grid-item-meta";

        // Show usage stats if worn > 0
        const usageBadge = item.usageCount > 0
            ? `<span style="color:var(--accent); font-weight:bold;">${item.usageCount}× worn</span>`
            : "New";

        meta.innerHTML = `
            <div style="font-weight:600; font-size:13px;">${item.type}</div>
            <div style="font-size:11px; color:#64748b; margin-top:2px;">${usageBadge}</div>
        `;

        div.appendChild(img);
        div.appendChild(meta);
        gridEl.appendChild(div);
    });
}

/* ---------- Item Detail Logic ---------- */
function initWardrobeItemPage() {
    const itemId = document.body.dataset.itemId;
    const errorEl = document.getElementById("item-error");
    const form = document.getElementById("item-form");

    if (!itemId) return;

    let wardrobe = loadWardrobe();
    let item = wardrobe.find((it) => it.id === itemId);

    if (!item) {
        if (errorEl) {
            errorEl.textContent = "Item not found.";
            errorEl.classList.remove("hidden");
        }
        form.classList.add("hidden");
        return;
    }

    // Populate Fields
    const imgEl = document.getElementById("item-image");
    if (imgEl && item.imageDataUrl) {
        imgEl.src = item.imageDataUrl;
        imgEl.style.display = "block";
    }

    ["type", "style", "season", "warmth", "brand"].forEach(field => {
        const el = document.getElementById(`item-${field}`);
        if(el) el.value = item[field] || "";
    });

    const tagsEl = document.getElementById("item-tags");
    if(tagsEl) tagsEl.value = (item.tags || []).join(", ");

    const usageEl = document.getElementById("item-usage");
    if(usageEl) usageEl.textContent = `Worn ${item.usageCount || 0} times. Added on ${new Date(item.createdAt).toLocaleDateString()}.`;

    // Save
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        ["type", "style", "season", "warmth", "brand"].forEach(field => {
             const el = document.getElementById(`item-${field}`);
             if(el) item[field] = el.value;
        });

        if(tagsEl) item.tags = tagsEl.value.split(",").map(s => s.trim()).filter(Boolean);

        wardrobe = loadWardrobe().map(it => it.id === itemId ? item : it);
        saveWardrobe(wardrobe);

        const saveBtn = document.getElementById("item-save");
        const originalText = saveBtn.textContent;
        saveBtn.textContent = "Saved ✔";
        saveBtn.style.background = "#10b981"; // Green
        setTimeout(() => {
            saveBtn.textContent = originalText;
            saveBtn.style.background = "";
        }, 1500);
    });

    // Delete
    const delBtn = document.getElementById("item-delete");
    if(delBtn) {
        delBtn.addEventListener("click", () => {
            if(confirm("Delete this item?")) {
                wardrobe = loadWardrobe().filter(it => it.id !== itemId);
                saveWardrobe(wardrobe);
                window.location.href = "/wardrobe";
            }
        });
    }
}

/* ---------- Home Logic (Smart Assistant) ---------- */

async function loadWeatherForCity(city) {
    if (!city) return null;
    try {
        return await apiFetch(`/api/weather?city=${encodeURIComponent(city)}`);
    } catch (e) {
        console.warn("Weather error", e);
        return null;
    }
}

function initHomePage() {
    // 1. Dynamic Greeting
    const titleEl = document.querySelector(".page-title");
    if (titleEl) {
        const h = new Date().getHours();
        let greeting = "Hello";
        if (h < 12) greeting = "Good morning";
        else if (h < 18) greeting = "Good afternoon";
        else greeting = "Good evening";

        // Keep the name part if it exists
        const namePart = titleEl.textContent.includes(",") ? titleEl.textContent.split(",")[1] : "";
        titleEl.textContent = `${greeting}${namePart}`;
    }

    const cityInput = document.getElementById("city-input");
    const eventInput = document.getElementById("event-input");
    const btn = document.getElementById("outfit-btn");
    const weatherBadge = document.getElementById("weather-badge");
    const tempEl = document.getElementById("weather-temp");
    const iconEl = document.getElementById("weather-icon");
    const resultCard = document.getElementById("outfit-result");
    const itemsEl = document.getElementById("outfit-items");
    const reasonEl = document.getElementById("outfit-reason");
    const hintEl = document.getElementById("home-hint");
    const errorEl = document.getElementById("home-error");
    const wornBtn = document.getElementById("outfit-worn");
    const wornStatusEl = document.getElementById("outfit-worn-status");

    let currentWeatherDataString = "";
    let cachedProfile = null;

    // Load Wardrobe Hint
    const wardrobe = loadWardrobe();
    if(hintEl) {
        hintEl.textContent = wardrobe.length
            ? `${wardrobe.length} items available for AI styling.`
            : "⚠️ Wardrobe is empty. Add items first!";
    }

    async function updateWeatherState() {
        const city = cityInput.value.trim();
        if (!city) {
            tempEl.textContent = "--";
            iconEl.textContent = "No city";
            return;
        }

        weatherBadge.classList.add("loading");
        iconEl.textContent = "Checking...";

        const data = await loadWeatherForCity(city);
        weatherBadge.classList.remove("loading");

        if (data && data.temperature != null) {
            const temp = Math.round(data.temperature);
            const wind = Math.round(data.windspeed || 0);
            tempEl.textContent = `${temp}°C`;
            iconEl.textContent = `Wind ${wind}km/h`;
            currentWeatherDataString = `${temp}°C, wind ${wind}km/h in ${data.city}`;
        } else {
            tempEl.textContent = "?";
            iconEl.textContent = "Not found";
            currentWeatherDataString = "";
        }
    }

    (async () => {
        cachedProfile = await apiFetch("/api/profile");
        if(cityInput && cityInput.value) updateWeatherState();
    })();

    if(cityInput) {
        cityInput.addEventListener("change", updateWeatherState);
        cityInput.addEventListener("keydown", (e) => e.key === "Enter" && cityInput.blur());
    }

    if(btn) {
        btn.addEventListener("click", async () => {
            const currentWardrobe = loadWardrobe();
            if (!currentWardrobe.length) {
                alert("Please add items to your wardrobe first!");
                return;
            }

            if (!currentWeatherDataString) await updateWeatherState();

            errorEl.classList.add("hidden");
            btn.disabled = true;
            btn.innerHTML = `Styling <span class="loading-dots">...</span>`;
            resultCard.classList.add("hidden");

            try {
                const data = await apiFetch("/api/outfit", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        wardrobe: currentWardrobe,
                        weather: currentWeatherDataString,
                        user: {
                            event: eventInput ? eventInput.value : "",
                            style: cachedProfile?.style || "",
                        },
                    }),
                });

                const ids = data?.items || [];
                lastGeneratedOutfitIds = ids;

                const byId = Object.fromEntries(currentWardrobe.map(it => [it.id, it]));
                let selectedItems = ids.map(id => byId[id]).filter(Boolean);

                const orderScore = (item) => {
                    const t = (item.type || "").toLowerCase();
                    const s = (item.subType || "").toLowerCase(); // если есть
                    if (t.includes("hat") || t.includes("cap") || t.includes("beanie")) return 1;
                    if (t.includes("jacket") || t.includes("coat") || t.includes("blazer")) return 2;
                    if (t.includes("shirt") || t.includes("top") || t.includes("hoodie") || t.includes("sweater")) return 3;
                    if (t.includes("pant") || t.includes("jean") || t.includes("trousers") || t.includes("skirt") || t.includes("short")) return 4;
                    if (t.includes("shoe") || t.includes("sneaker") || t.includes("boot")) return 5;
                    return 10;
                };

                selectedItems.sort((a, b) => orderScore(a) - orderScore(b));

                const stackEl = document.getElementById("mannequin-stack");
                const listEl = document.getElementById("outfit-items");

                if (stackEl) stackEl.innerHTML = "";
                listEl.innerHTML = "";

                selectedItems.forEach(item => {
                    if (stackEl) {
                        const div = document.createElement("div");
                        div.className = "mannequin-item";
                        const img = document.createElement("img");
                        img.src = item.imageDataUrl;
                        div.appendChild(img);
                        stackEl.appendChild(div);
                    }

                    const li = document.createElement("li");
                    li.innerHTML = `
                        <span>${item.type}</span>
                        <span style="font-size:12px; color:#94a3b8">${item.brand || 'No brand'}</span>
                    `;
                    listEl.appendChild(li);
                });

                reasonEl.innerHTML = (data.reason || "Here is your look.")
                    .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');

                resultCard.classList.remove("hidden");

                setTimeout(() => {
                    resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
                }, 100);

            } catch (e) {
                console.error(e);
                errorEl.textContent = "AI is thinking too hard. Try again.";
                errorEl.classList.remove("hidden");
            } finally {
                btn.disabled = false;
                btn.textContent = "✨ Generate Look";
            }
        });
    }

    if (wornBtn) {
        wornBtn.addEventListener("click", () => {
            const currentWardrobe = loadWardrobe();
            let updated = false;
            const nowIso = new Date().toISOString();

            currentWardrobe.forEach((item) => {
                if (lastGeneratedOutfitIds.includes(item.id)) {
                    item.usageCount = (item.usageCount || 0) + 1;
                    item.lastUsed = nowIso;
                    updated = true;
                }
            });

            if (updated) {
                saveWardrobe(currentWardrobe);
                wornStatusEl.textContent = "Great choice! Usage stats updated.";
                wornBtn.disabled = true;
                wornBtn.textContent = "Marked as Worn ✔";
                wornBtn.style.background = "#10b981";
                wornBtn.style.borderColor = "#10b981";
                wornBtn.style.color = "white";
            }
        });
    }
}


/* ---------- Chat Logic (Multi-chat) ---------- */
/* ---------- Chat Logic (Multi-chat + History) ---------- */

function initChatPage() {
    const listEl = document.getElementById("chat-list");
    const windowEl = document.getElementById("chat-window");
    const input = document.getElementById("chat-input");
    const sendBtn = document.getElementById("chat-send");
    const newBtn = document.getElementById("new-chat-btn");

    let currentChatId = null;

    if (!windowEl) return;

    // --- 1. Load List ---
    async function loadList() {
        try {
            const chats = await apiFetch("/api/chats");
            listEl.innerHTML = "";

            chats.forEach(chat => {
                const div = document.createElement("div");
                div.className = `chat-list-item ${chat.id === currentChatId ? 'active' : ''}`;
                div.innerHTML = `
                    <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                        ${chat.title}
                    </span>
                    <span class="chat-delete" title="Delete">&times;</span>
                `;

                // Click chat -> Load it
                div.onclick = (e) => {
                    // Prevent triggering if clicked on delete
                    if(e.target.classList.contains("chat-delete")) return;
                    loadChat(chat.id);
                };

                // Click delete
                div.querySelector(".chat-delete").onclick = async (e) => {
                    e.stopPropagation();
                    if(confirm("Delete chat?")) {
                        await apiFetch(`/api/chats/${chat.id}`, {method:"DELETE"});
                        if(currentChatId === chat.id) {
                            currentChatId = null;
                            windowEl.innerHTML = '<div class="chat-intro"><p>Chat deleted.</p></div>';
                            input.disabled = true;
                        }
                        loadList();
                    }
                };

                listEl.appendChild(div);
            });

            // If no chat selected but chats exist, select the first one (most recent)
            if (!currentChatId && chats.length > 0) {
               // loadChat(chats[0].id); // Uncomment if you want auto-select
            }
        } catch(e) { console.error(e); }
    }

    // --- 2. Load Specific Chat ---
    async function loadChat(id) {
        currentChatId = id;
        input.disabled = true;
        windowEl.innerHTML = ""; // Clear screen

        // Refresh list to show active state
        const items = listEl.querySelectorAll(".chat-list-item");
        // We'll just reload list to be simple or toggle classes manually
        loadList();

        try {
            const chatData = await apiFetch(`/api/chats/${id}`);

            // Render history
            if (chatData.messages && chatData.messages.length) {
                chatData.messages.forEach(msg => {
                   addBubble(msg.content, msg.role === "user" ? "user" : "ai");
                });
            } else {
                windowEl.innerHTML = '<div class="chat-intro"><p>New chat started. Say hello!</p></div>';
            }

            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
        } catch(e) { console.error(e); }
    }

    // --- 3. Create New ---
    async function createNew() {
        try {
            const res = await apiFetch("/api/chats", {method:"POST"});
            if (res.id) loadChat(res.id);
        } catch(e) { console.error(e); }
    }

    // --- 4. Send Message ---
    function addBubble(text, who) {
        // Remove placeholder if exists
        const ph = document.getElementById("chat-placeholder");
        if(ph) ph.remove();
        const intro = document.querySelector(".chat-intro");
        if(intro) intro.remove();

        const div = document.createElement("div");
        div.className = "bubble " + who;
        div.innerHTML = text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
        windowEl.appendChild(div);
        windowEl.scrollTop = windowEl.scrollHeight;
    }

    async function send() {
        const text = input.value.trim();
        if(!text) return;

        if(!currentChatId) await createNew(); // Safety fallback

        input.value = "";
        addBubble(text, "user");

        // Typing anim
        const typing = document.createElement("div");
        typing.className = "bubble ai typing-bubble";
        typing.textContent = "•••";
        windowEl.appendChild(typing);
        windowEl.scrollTop = windowEl.scrollHeight;

        try {
            const res = await apiFetch(`/api/chats/${currentChatId}/message`, {
                method: "POST",
                headers: {"Content-Type":"application/json"},
                body: JSON.stringify({message: text})
            });

            typing.remove();
            if(res.reply) {
                addBubble(res.reply, "ai");
                // Refresh list titles
                loadList();
            }
        } catch(e) {
            typing.remove();
            addBubble("Error sending message", "ai");
        }
    }

    newBtn.addEventListener("click", createNew);
    sendBtn.addEventListener("click", send);
    input.addEventListener("keydown", e => { if(e.key==="Enter") send(); });

    // Init
    loadList();
}


/* ---------- Profile Pages (Basic) ---------- */
function initProfileBasic() {
    const form = document.getElementById("profile-basic-form");
    if(!form) return;
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const btn = document.getElementById("basic-save");
        const status = document.getElementById("basic-status");

        btn.textContent = "Saving...";
        btn.disabled = true;

        const payload = {
            name: document.getElementById("basic-name").value,
            email: document.getElementById("basic-email").value,
            city: document.getElementById("basic-city").value,
            about: document.getElementById("basic-about").value,
        };

        try {
            await apiFetch("/api/profile", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(payload)
            });
            window.location.href = "/profile";
        } catch(e) {
            status.textContent = "Error saving profile.";
            btn.disabled = false;
        }
    });
}

/* ---------- Profile Params (Enhanced) ---------- */
function initProfileParams() {
    const form = document.getElementById("profile-params-form");
    if(!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const btn = document.getElementById("params-save");
        btn.textContent = "Saving...";
        btn.disabled = true;

        // Собираем данные из новых полей
        const payload = {
            gender: document.getElementById("params-gender").value,
            height: document.getElementById("params-height").value,
            weight: document.getElementById("params-weight").value,
            body_type: document.getElementById("params-body").value,
            skin_tone: document.getElementById("params-skin").value,
            style: document.getElementById("params-style").value,
        };

        try {
            await apiFetch("/api/profile", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(payload)
            });
            window.location.href = "/profile";
        } catch(e) {
            console.error(e);
            btn.textContent = "Error";
            btn.disabled = false;
        }
    });
}

/* ---------- Init ---------- */
document.addEventListener("DOMContentLoaded", () => {
    const page = document.body.dataset.page;
    if (page === "home") initHomePage();
    if (page === "wardrobe") initWardrobePage();
    if (page === "wardrobe-item") initWardrobeItemPage();
    if (page === "chat") initChatPage();
    if (page === "profile-basic") initProfileBasic();
    if (page === "profile-params") initProfileParams();
});