(() => {
  const root = document.querySelector("[data-bot-root]");
  if (!root) return;

  const STORAGE_KEY = "knockoffBotPosition";
  const trigger = root.querySelector("[data-bot-trigger]");
  const panel = root.querySelector("[data-bot-panel]");
  const closeButton = root.querySelector("[data-bot-close]");
  const form = root.querySelector("[data-bot-form]");
  const input = root.querySelector("[data-bot-input]");
  const messages = root.querySelector("[data-bot-messages]");
  const statusNode = root.querySelector("[data-bot-status]");
  const isLocalHost = ["127.0.0.1", "localhost"].includes(window.location.hostname);
  const apiURL = isLocalHost && root.dataset.localApiUrl ? root.dataset.localApiUrl : root.dataset.apiUrl;

  if (!trigger || !panel || !closeButton || !form || !input || !messages || !statusNode || !apiURL) return;
  trigger.draggable = false;

  let dragging = false;
  let moved = false;
  let startPoint = null;
  let startPosition = null;
  let suppressClick = false;

  const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

  const readPoint = (event) => {
    if (event.touches && event.touches[0]) {
      return { x: event.touches[0].clientX, y: event.touches[0].clientY };
    }
    if (event.changedTouches && event.changedTouches[0]) {
      return { x: event.changedTouches[0].clientX, y: event.changedTouches[0].clientY };
    }
    return { x: event.clientX, y: event.clientY };
  };

  const applyPosition = (left, top, persist = false) => {
    const maxLeft = window.innerWidth - root.offsetWidth - 8;
    const maxTop = window.innerHeight - root.offsetHeight - 8;
    const nextLeft = clamp(left, 8, maxLeft);
    const nextTop = clamp(top, 8, maxTop);

    root.style.left = `${nextLeft}px`;
    root.style.top = `${nextTop}px`;
    root.style.right = "auto";
    root.style.bottom = "auto";

    if (persist) {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ left: nextLeft, top: nextTop }));
    }
  };

  const restorePosition = () => {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      root.style.left = "auto";
      root.style.top = "auto";
      root.style.right = "1rem";
      root.style.bottom = "1rem";
      return;
    }

    try {
      const saved = JSON.parse(raw);
      if (typeof saved.left === "number" && typeof saved.top === "number") {
        applyPosition(saved.left, saved.top);
      }
    } catch (_) {
      window.localStorage.removeItem(STORAGE_KEY);
      root.style.left = "auto";
      root.style.top = "auto";
      root.style.right = "1rem";
      root.style.bottom = "1rem";
    }
  };

  const openPanel = () => {
    const rect = root.getBoundingClientRect();
    if (rect.left < window.innerWidth / 2) {
      panel.style.left = "0";
      panel.style.right = "auto";
    } else {
      panel.style.right = "0";
      panel.style.left = "auto";
    }
    panel.hidden = false;
    root.classList.add("is-open");
  };

  const closePanel = () => {
    panel.hidden = true;
    root.classList.remove("is-open");
  };

  const togglePanel = () => {
    if (panel.hidden) openPanel();
    else closePanel();
  };

  const setStatus = (text, isError = false) => {
    statusNode.textContent = text;
    statusNode.dataset.state = isError ? "error" : "ok";
  };

  const addMessage = (role, body, citations = []) => {
    const article = document.createElement("article");
    article.className = `knockoff-bot-message knockoff-bot-message--${role.toLowerCase()}`;

    const header = document.createElement("header");
    header.textContent = role;
    article.appendChild(header);

    const bodyNode = document.createElement("div");
    bodyNode.className = "knockoff-bot-message-body";
    bodyNode.textContent = body;
    article.appendChild(bodyNode);

    if (citations.length) {
      const list = document.createElement("ul");
      list.className = "knockoff-bot-citations";
      citations.forEach((citation) => {
        const item = document.createElement("li");
        item.textContent = `${citation.title} - ${citation.snippet}`;
        list.appendChild(item);
      });
      article.appendChild(list);
    }

    messages.appendChild(article);
    messages.scrollTop = messages.scrollHeight;
  };

  const request = async (path, options = {}) => {
    const response = await fetch(`${apiURL}${path}`, options);
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.detail || `Request failed: ${response.status}`);
    }
    return payload;
  };

  const checkHealth = async () => {
    try {
      await request("/health");
      setStatus(root.dataset.statusReady || "Ready for questions");
    } catch (_) {
      setStatus(root.dataset.statusOffline || "Bot backend is unavailable.", true);
    }
  };

  const onDragMove = (event) => {
    if (!dragging || !startPoint || !startPosition) return;

    const point = readPoint(event);
    const dx = point.x - startPoint.x;
    const dy = point.y - startPoint.y;

    if (!moved && Math.hypot(dx, dy) > 6) {
      moved = true;
    }
    if (!moved) return;

    event.preventDefault();
    applyPosition(startPosition.left + dx, startPosition.top + dy);
  };

  const finishDrag = () => {
    if (!dragging) return;

    window.removeEventListener("mousemove", onDragMove);
    window.removeEventListener("mouseup", finishDrag);
    window.removeEventListener("touchmove", onDragMove);
    window.removeEventListener("touchend", finishDrag);
    window.removeEventListener("touchcancel", finishDrag);

    root.classList.remove("is-dragging");
    if (moved) {
      const rect = root.getBoundingClientRect();
      applyPosition(rect.left, rect.top, true);
      suppressClick = true;
    }

    dragging = false;
    startPoint = null;
    startPosition = null;
  };

  const startDrag = (event, kind) => {
    if (kind === "mouse" && event.button !== 0) return;

    const rect = root.getBoundingClientRect();
    const point = readPoint(event);

    dragging = true;
    moved = false;
    suppressClick = false;
    startPoint = { x: point.x, y: point.y };
    startPosition = { left: rect.left, top: rect.top };
    root.classList.add("is-dragging");

    root.style.left = `${rect.left}px`;
    root.style.top = `${rect.top}px`;
    root.style.right = "auto";
    root.style.bottom = "auto";

    if (kind === "mouse") {
      window.addEventListener("mousemove", onDragMove);
      window.addEventListener("mouseup", finishDrag);
    } else {
      window.addEventListener("touchmove", onDragMove, { passive: false });
      window.addEventListener("touchend", finishDrag);
      window.addEventListener("touchcancel", finishDrag);
    }
  };

  trigger.addEventListener("mousedown", (event) => startDrag(event, "mouse"));
  trigger.addEventListener("touchstart", (event) => startDrag(event, "touch"), { passive: false });

  trigger.addEventListener("click", (event) => {
    if (suppressClick || moved) {
      event.preventDefault();
      suppressClick = false;
      moved = false;
      return;
    }
    togglePanel();
  });

  closeButton.addEventListener("click", closePanel);

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closePanel();
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const question = input.value.trim();
    if (!question) return;

    addMessage(root.dataset.roleUser || "You", question);
    input.value = "";
    setStatus(root.dataset.statusLoading || "Thinking...");

    try {
      const payload = await request("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, top_k: 4, use_llm: true }),
      });
      addMessage(root.dataset.roleBot || "Bot", payload.answer, payload.citations || []);
      if (payload.warning) {
        addMessage(root.dataset.roleSystem || "System", payload.warning);
      }
      setStatus(root.dataset.statusReady || "Ready for questions");
    } catch (error) {
      addMessage(root.dataset.roleSystem || "System", error.message);
      setStatus(root.dataset.statusOffline || "Bot backend is unavailable.", true);
    }
  });

  window.addEventListener("resize", () => {
    const rect = root.getBoundingClientRect();
    applyPosition(rect.left, rect.top, true);
  });

  restorePosition();
  checkHealth();
})();
