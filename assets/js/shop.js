/* =========================================================================
   Shop page: client-side filter / search / sort over server-rendered cards.
   Cards already exist in the DOM (SEO-friendly) — this only shows/hides
   and reorders them, and keeps state in the URL query string.
   ========================================================================= */
(function () {
  "use strict";
  const grid = document.querySelector("[data-product-grid]");
  if (!grid) return;

  const cards = Array.from(grid.querySelectorAll(".card"));
  const checkboxes = Array.from(document.querySelectorAll("[data-filter]"));
  const searchInput = document.querySelector("[data-shop-search]");
  const sortSelect = document.querySelector("[data-shop-sort]");
  const resultCount = document.querySelector("[data-result-count]");
  const activeFiltersWrap = document.querySelector("[data-active-filters]");
  const clearAllBtn = document.querySelector("[data-clear-filters]");
  const emptyState = document.querySelector("[data-empty-state]");

  function currentChecked() {
    return checkboxes.filter((cb) => cb.checked);
  }

  function syncURL() {
    const params = new URLSearchParams();
    currentChecked().forEach((cb) => params.append(cb.name, cb.value));
    if (searchInput && searchInput.value.trim()) params.set("q", searchInput.value.trim());
    if (sortSelect && sortSelect.value !== "featured") params.set("sort", sortSelect.value);
    const qs = params.toString();
    history.replaceState(null, "", qs ? `?${qs}` : location.pathname);
  }

  function applyFromURL() {
    const params = new URLSearchParams(location.search);
    checkboxes.forEach((cb) => {
      if (params.getAll(cb.name).includes(cb.value)) cb.checked = true;
    });
    const q = params.get("q");
    if (q && searchInput) searchInput.value = q;
    const sort = params.get("sort");
    if (sort && sortSelect) sortSelect.value = sort;
  }

  function chip(label, onRemove) {
    const el = document.createElement("span");
    el.className = "chip";
    el.innerHTML = `${label} <button type="button" aria-label="Remove filter ${label}"><svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M1 1l10 10M11 1 1 11"/></svg></button>`;
    el.querySelector("button").addEventListener("click", onRemove);
    return el;
  }

  function renderChips() {
    if (!activeFiltersWrap) return;
    activeFiltersWrap.innerHTML = "";
    const checked = currentChecked();
    checked.forEach((cb) => {
      const label = cb.closest(".check").querySelector("span:not(.n)")?.textContent.trim() || cb.value;
      activeFiltersWrap.appendChild(chip(label, () => { cb.checked = false; update(); }));
    });
    activeFiltersWrap.parentElement.style.display = checked.length ? "flex" : "none";
    if (clearAllBtn) clearAllBtn.style.display = checked.length ? "inline" : "none";
  }

  function matches(card) {
    const checked = currentChecked();
    const byGroup = {};
    checked.forEach((cb) => {
      byGroup[cb.name] = byGroup[cb.name] || [];
      byGroup[cb.name].push(cb.value);
    });
    for (const group in byGroup) {
      const cardVal = card.getAttribute(`data-${group}`);
      if (!byGroup[group].includes(cardVal)) return false;
    }
    if (searchInput && searchInput.value.trim()) {
      const q = searchInput.value.trim().toLowerCase();
      const name = card.getAttribute("data-name") || "";
      if (!name.includes(q)) return false;
    }
    return true;
  }

  function sortCards(list) {
    const mode = sortSelect ? sortSelect.value : "featured";
    const arr = list.slice();
    if (mode === "price-asc") arr.sort((a, b) => +a.getAttribute("data-price") - +b.getAttribute("data-price"));
    else if (mode === "price-desc") arr.sort((a, b) => +b.getAttribute("data-price") - +a.getAttribute("data-price"));
    else if (mode === "newest") arr.sort((a, b) => +b.getAttribute("data-new") - +a.getAttribute("data-new"));
    else arr.sort((a, b) => +b.getAttribute("data-featured") - +a.getAttribute("data-featured"));
    return arr;
  }

  function update() {
    const visible = cards.filter(matches);
    const sorted = sortCards(visible);
    cards.forEach((c) => { c.style.display = "none"; });
    sorted.forEach((c, i) => {
      c.style.display = "";
      c.style.order = i;
    });
    if (resultCount) resultCount.textContent = `${visible.length} piece${visible.length === 1 ? "" : "s"}`;
    if (emptyState) emptyState.style.display = visible.length ? "none" : "block";
    renderChips();
    syncURL();
  }

  checkboxes.forEach((cb) => cb.addEventListener("change", update));
  if (searchInput) {
    let t;
    searchInput.addEventListener("input", () => { clearTimeout(t); t = setTimeout(update, 180); });
  }
  if (sortSelect) sortSelect.addEventListener("change", update);
  if (clearAllBtn) clearAllBtn.addEventListener("click", () => { checkboxes.forEach((cb) => (cb.checked = false)); update(); });

  grid.style.display = "grid";
  applyFromURL();
  update();
})();
