/* =========================================================================
   Bag (reserve) + Wishlist — localStorage-backed. No checkout: the Bag is a
   "reserve to enquire" list that hands off to the Contact page.
   ========================================================================= */
(function () {
  "use strict";

  const BAG_KEY = "ssv_bag_v1";
  const WISH_KEY = "ssv_wishlist_v1";

  function readMap() {
    const el = document.getElementById("ssv-data");
    if (!el) return {};
    try { return JSON.parse(el.textContent); } catch (e) { return {}; }
  }
  const PRODUCTS = readMap();

  function safeParse(key) {
    try {
      const v = JSON.parse(localStorage.getItem(key));
      return Array.isArray(v) ? v : [];
    } catch (e) { return []; }
  }
  function getBag() { return safeParse(BAG_KEY); }
  function saveBag(items) { localStorage.setItem(BAG_KEY, JSON.stringify(items)); render(); }
  function getWishlist() { return safeParse(WISH_KEY); }
  function saveWishlist(items) { localStorage.setItem(WISH_KEY, JSON.stringify(items)); render(); }

  function addToBag(id, size) {
    const items = getBag();
    const existing = items.find((i) => i.id === id);
    if (existing) {
      // Every piece is one-of-one — you can't buy two of the same garment
      showToast("This one-of-one piece is already in your bag");
      return;
    }
    items.push({ id, size: size || "One Size", qty: 1 });
    saveBag(items);
    showToast("Added to your bag");
    pulseIcon("bag");
  }
  function removeFromBag(index) {
    const items = getBag();
    items.splice(index, 1);
    saveBag(items);
  }
  function isWished(id) { return getWishlist().includes(id); }
  function toggleWishlist(id) {
    let items = getWishlist();
    if (items.includes(id)) {
      items = items.filter((x) => x !== id);
    } else {
      items.push(id);
      showToast("Saved to your wishlist");
      pulseIcon("wishlist");
    }
    saveWishlist(items);
  }

  function pulseIcon(which) {
    const el = document.querySelector(`[data-drawer-open="${which}"] svg`);
    if (!el) return;
    el.animate(
      [{ transform: "scale(1)" }, { transform: "scale(1.35)" }, { transform: "scale(1)" }],
      { duration: 420, easing: "cubic-bezier(.19,1,.22,1)" }
    );
  }

  let toastTimer;
  function showToast(msg) {
    let toast = document.querySelector(".toast");
    if (!toast) {
      toast = document.createElement("div");
      toast.className = "toast";
      toast.setAttribute("role", "status");
      toast.setAttribute("aria-live", "polite");
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), 2600);
  }

  function money(n) { return "$" + Number(n).toFixed(0); }

  function itemRow(entry, index, kind) {
    const p = PRODUCTS[entry.id || entry];
    if (!p) return "";
    const id = entry.id || entry;
    const size = entry.size ? `<span>Size ${entry.size}</span>` : "";
    return `
      <div class="drawer-item" data-row="${index}">
        <a href="${p.href}"><img class="drawer-item__img" src="${p.img}" alt="" loading="lazy" width="76" height="96"></a>
        <div>
          <a href="${p.href}"><div class="drawer-item__name">${p.name}</div></a>
          <div class="drawer-item__meta">${size}${entry.size ? " · " : ""}${p.era || ""}</div>
          <button class="drawer-item__remove" type="button" data-remove="${kind}" data-index="${index}">Remove</button>
        </div>
        <div class="drawer-item__actions">
          <div class="drawer-item__price">${money(p.price)}</div>
        </div>
      </div>`;
  }

  function render() {
    const bag = getBag();
    const wish = getWishlist();

    document.querySelectorAll('[data-count="bag"]').forEach((el) => {
      const n = bag.reduce((s, i) => s + i.qty, 0);
      el.textContent = n;
      el.classList.toggle("show", n > 0);
    });
    document.querySelectorAll('[data-count="wishlist"]').forEach((el) => {
      el.textContent = wish.length;
      el.classList.toggle("show", wish.length > 0);
    });

    const bagBody = document.querySelector('[data-drawer-body="bag"]');
    if (bagBody) {
      if (!bag.length) {
        bagBody.innerHTML = `<div class="drawer__empty"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M6 8h12l-1 12H7L6 8Z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg><p>Your bag is empty.<br>Start saving pieces you love.</p></div>`;
      } else {
        bagBody.innerHTML = bag.map((e, i) => itemRow(e, i, "bag")).join("");
      }
      const total = bag.reduce((s, e) => s + ((PRODUCTS[e.id] && PRODUCTS[e.id].price) || 0) * e.qty, 0);
      const totalEl = document.querySelector('[data-bag-total]');
      if (totalEl) totalEl.textContent = money(total);
      const foot = document.querySelector('[data-drawer-foot="bag"]');
      if (foot) foot.style.display = bag.length ? "block" : "none";
    }

    const wishBody = document.querySelector('[data-drawer-body="wishlist"]');
    if (wishBody) {
      if (!wish.length) {
        wishBody.innerHTML = `<div class="drawer__empty"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M12 21s-7.5-4.6-10-9.3C.5 8 2 4 6 4c2.2 0 3.7 1.2 6 3.6C14.3 5.2 15.8 4 18 4c4 0 5.5 4 4 7.7C19.5 16.4 12 21 12 21Z"/></svg><p>No saved pieces yet.<br>Tap the heart on anything you love.</p></div>`;
      } else {
        wishBody.innerHTML = wish.map((id, i) => itemRow(id, i, "wishlist")).join("");
      }
    }

    document.querySelectorAll("[data-wish-id]").forEach((btn) => {
      btn.classList.toggle("is-active", isWished(btn.getAttribute("data-wish-id")));
    });
  }

  document.addEventListener("click", (e) => {
    const addBtn = e.target.closest("[data-add-to-bag]");
    if (addBtn) {
      e.preventDefault();
      const id = addBtn.getAttribute("data-add-to-bag");
      const sizeSel = document.querySelector(".size-select .is-active");
      const size = addBtn.getAttribute("data-size") || (sizeSel && sizeSel.textContent.trim());
      addToBag(id, size);
    }
    const wishBtn = e.target.closest("[data-wish-id]");
    if (wishBtn) {
      e.preventDefault();
      toggleWishlist(wishBtn.getAttribute("data-wish-id"));
    }
    const removeBtn = e.target.closest("[data-remove]");
    if (removeBtn) {
      e.preventDefault();
      const kind = removeBtn.getAttribute("data-remove");
      const index = Number(removeBtn.getAttribute("data-index"));
      if (kind === "bag") removeFromBag(index);
      else {
        const w = getWishlist();
        w.splice(index, 1);
        saveWishlist(w);
      }
    }
  });

  window.SSV_cart = { addToBag, toggleWishlist, isWished, getBag, getWishlist, render };
  render();
})();
