/* =========================================================================
   Checkout — realistic front-end flow, no backend.
   Card details live only in the form; they are never persisted anywhere.
   ========================================================================= */
(function () {
  "use strict";

  const BAG_KEY = "ssv_bag_v1";
  const ORDERS_KEY = "ssv_orders_v1";
  const FREE_SHIP_THRESHOLD = 200;

  const dataEl = document.getElementById("ssv-data");
  const PRODUCTS = dataEl ? JSON.parse(dataEl.textContent) : {};

  const form = document.querySelector("[data-checkout-form]");
  const layout = document.querySelector("[data-checkout-layout]");
  const emptyState = document.querySelector("[data-checkout-empty]");
  const successPanel = document.querySelector("[data-order-success]");
  if (!form) return;

  function getBag() {
    try {
      const v = JSON.parse(localStorage.getItem(BAG_KEY));
      return Array.isArray(v) ? v : [];
    } catch (e) { return []; }
  }
  const money = (n) => "$" + Number(n).toFixed(2);

  /* ---------- Totals ---------- */
  function shippingCost(method, subtotal) {
    if (method === "pickup") return 0;
    if (method === "express") return 18;
    return subtotal >= FREE_SHIP_THRESHOLD ? 0 : 8; // standard
  }

  function currentMethod() {
    const checked = form.querySelector('input[name="delivery"]:checked');
    return checked ? checked.value : "standard";
  }

  function computeTotals() {
    const bag = getBag();
    const subtotal = bag.reduce((s, e) => s + ((PRODUCTS[e.id] && PRODUCTS[e.id].price) || 0) * e.qty, 0);
    const ship = shippingCost(currentMethod(), subtotal);
    return { subtotal, ship, tax: 0, total: subtotal + ship };
  }

  /* ---------- Order summary ---------- */
  function renderSummary() {
    const bag = getBag();
    const itemsWrap = document.querySelector("[data-summary-items]");
    if (!itemsWrap) return;

    if (!bag.length && !successPanel.classList.contains("show")) {
      layout.style.display = "none";
      emptyState.style.display = "block";
      return;
    }
    layout.style.display = "";
    emptyState.style.display = "none";

    itemsWrap.innerHTML = bag.map((e) => {
      const p = PRODUCTS[e.id];
      if (!p) return "";
      return `<div class="summary-item">
        <img src="${p.img}" alt="" width="56" height="70" loading="lazy">
        <div>
          <div class="summary-item__name">${p.name}</div>
          <div class="summary-item__meta">Size ${e.size} · ${p.era} · One of one</div>
        </div>
        <div class="summary-item__price">${money(p.price)}</div>
      </div>`;
    }).join("");

    const t = computeTotals();
    document.querySelector("[data-sum-subtotal]").textContent = money(t.subtotal);
    document.querySelector("[data-sum-shipping]").textContent = t.ship === 0 ? "Free" : money(t.ship);
    document.querySelector("[data-sum-total]").textContent = money(t.total);
    const payBtn = form.querySelector("[data-pay-btn]");
    if (payBtn && !payBtn.disabled) payBtn.querySelector("span").textContent = `Pay ${money(t.total)}`;

    // Standard shipping row shows the free-threshold state
    const stdPrice = form.querySelector('[data-ship-price="standard"]');
    if (stdPrice) stdPrice.textContent = t.subtotal >= FREE_SHIP_THRESHOLD ? "Free" : "$8.00";
  }

  /* ---------- Delivery method selection ---------- */
  form.querySelectorAll('input[name="delivery"]').forEach((radio) => {
    radio.addEventListener("change", () => {
      form.querySelectorAll(".radio-card").forEach((c) => c.classList.remove("is-selected"));
      radio.closest(".radio-card").classList.add("is-selected");
      const shipFields = document.querySelector("[data-shipping-fields]");
      if (shipFields) shipFields.style.display = radio.value === "pickup" ? "none" : "";
      const payStep = form.querySelector("[data-pay-step]");
      if (payStep) payStep.textContent = radio.value === "pickup" ? "3" : "4";
      renderSummary();
    });
  });

  /* ---------- Card input formatting ---------- */
  const cardInput = form.querySelector('[name="card-number"]');
  const brandEl = form.querySelector("[data-card-brand]");
  function detectBrand(digits) {
    if (/^4/.test(digits)) return "Visa";
    if (/^5[1-5]/.test(digits) || /^2[2-7]/.test(digits)) return "Mastercard";
    if (/^3[47]/.test(digits)) return "Amex";
    if (/^6/.test(digits)) return "Discover";
    return "";
  }
  if (cardInput) {
    cardInput.addEventListener("input", () => {
      let digits = cardInput.value.replace(/\D/g, "").slice(0, 16);
      const brand = detectBrand(digits);
      if (brand === "Amex") digits = digits.slice(0, 15);
      const groups = brand === "Amex" ? [4, 6, 5] : [4, 4, 4, 4];
      let out = [], i = 0;
      for (const g of groups) {
        if (i >= digits.length) break;
        out.push(digits.slice(i, i + g));
        i += g;
      }
      cardInput.value = out.join(" ");
      if (brandEl) brandEl.textContent = brand;
    });
  }

  const expiryInput = form.querySelector('[name="card-expiry"]');
  if (expiryInput) {
    expiryInput.addEventListener("input", () => {
      let v = expiryInput.value.replace(/\D/g, "").slice(0, 4);
      if (v.length >= 3) v = v.slice(0, 2) + "/" + v.slice(2);
      else if (v.length === 2 && !expiryInput.value.endsWith("/")) v = v + "/";
      expiryInput.value = v;
    });
  }

  const cvvInput = form.querySelector('[name="card-cvv"]');
  if (cvvInput) {
    cvvInput.addEventListener("input", () => {
      cvvInput.value = cvvInput.value.replace(/\D/g, "").slice(0, 4);
    });
  }

  const zipInput = form.querySelector('[name="zip"]');
  if (zipInput) {
    zipInput.addEventListener("input", () => {
      zipInput.value = zipInput.value.replace(/[^\dA-Za-z -]/g, "").slice(0, 10);
    });
  }

  /* ---------- Validation ---------- */
  const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  function fieldOk(field) {
    const v = field.value.trim();
    if (!v) return false;
    switch (field.name) {
      case "email": return emailRe.test(v);
      case "card-number": {
        const d = v.replace(/\D/g, "");
        return d.length === 15 || d.length === 16;
      }
      case "card-expiry": {
        const m = v.match(/^(\d{2})\/(\d{2})$/);
        if (!m) return false;
        const month = +m[1], year = 2000 + +m[2];
        if (month < 1 || month > 12) return false;
        const now = new Date();
        return year > now.getFullYear() || (year === now.getFullYear() && month >= now.getMonth() + 1);
      }
      case "card-cvv": return /^\d{3,4}$/.test(v);
      case "zip": return v.length >= 3;
      default: return true;
    }
  }

  function validate() {
    let firstBad = null;
    const pickup = currentMethod() === "pickup";
    form.querySelectorAll("[required]").forEach((field) => {
      // Skip hidden shipping-address fields when picking up
      if (pickup && field.closest("[data-shipping-fields]")) {
        field.closest(".field").classList.remove("has-error");
        return;
      }
      const ok = fieldOk(field);
      field.closest(".field").classList.toggle("has-error", !ok);
      if (!ok && !firstBad) firstBad = field;
    });
    return firstBad;
  }

  form.querySelectorAll("input, select").forEach((f) => {
    f.addEventListener("input", () => {
      const wrap = f.closest(".field");
      if (wrap) wrap.classList.remove("has-error");
    });
  });

  /* ---------- Place order ---------- */
  function orderNumber() {
    const d = new Date();
    const ymd = String(d.getFullYear()).slice(2) + String(d.getMonth() + 1).padStart(2, "0") + String(d.getDate()).padStart(2, "0");
    return `SSV-${ymd}-${String(Math.floor(1000 + Math.random() * 9000))}`;
  }

  function deliveryEstimate(method) {
    if (method === "pickup") return "Ready for pickup within 2 hours";
    const days = method === "express" ? 2 : 5;
    const d = new Date();
    let added = 0;
    while (added < days) {
      d.setDate(d.getDate() + 1);
      if (d.getDay() !== 0 && d.getDay() !== 6) added++;
    }
    return "Estimated delivery by " + d.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" });
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const bad = validate();
    if (bad) {
      bad.focus();
      bad.scrollIntoView({ block: "center", behavior: "smooth" });
      return;
    }

    const payBtn = form.querySelector("[data-pay-btn]");
    const t = computeTotals();
    payBtn.disabled = true;
    payBtn.innerHTML = '<span class="spinner" aria-hidden="true"></span><span>Processing payment…</span>';

    setTimeout(() => {
      const bag = getBag();
      const method = currentMethod();
      const email = form.querySelector('[name="email"]').value.trim();
      const firstName = form.querySelector('[name="first-name"]').value.trim();
      const cardDigits = (cardInput ? cardInput.value.replace(/\D/g, "") : "");
      const order = {
        number: orderNumber(),
        placedAt: new Date().toISOString(),
        items: bag,
        totals: t,
        delivery: method,
        // Only non-sensitive payment metadata is kept — never the card itself
        payment: { brand: detectBrand(cardDigits) || "Card", last4: cardDigits.slice(-4) },
      };
      try {
        const prev = JSON.parse(localStorage.getItem(ORDERS_KEY)) || [];
        prev.push(order);
        localStorage.setItem(ORDERS_KEY, JSON.stringify(prev));
      } catch (err) { /* non-critical */ }

      // Build confirmation
      document.querySelector("[data-conf-name]").textContent = firstName ? `Thank you, ${firstName}.` : "Thank you.";
      document.querySelector("[data-conf-number]").textContent = order.number;
      document.querySelector("[data-conf-email]").textContent = email;
      document.querySelector("[data-conf-delivery]").textContent = deliveryEstimate(method);
      document.querySelector("[data-conf-items]").innerHTML = bag.map((en) => {
        const p = PRODUCTS[en.id];
        return p ? `<div class="summary-item">
            <img src="${p.img}" alt="" width="56" height="70">
            <div><div class="summary-item__name">${p.name}</div>
            <div class="summary-item__meta">Size ${en.size} · ${p.era}</div></div>
            <div class="summary-item__price">${money(p.price)}</div>
          </div>` : "";
      }).join("");
      document.querySelector("[data-conf-subtotal]").textContent = money(t.subtotal);
      document.querySelector("[data-conf-shipping]").textContent = t.ship === 0 ? "Free" : money(t.ship);
      document.querySelector("[data-conf-total]").textContent = money(t.total);
      document.querySelector("[data-conf-payment]").textContent =
        order.payment.brand + (order.payment.last4 ? " ending in " + order.payment.last4 : "");

      // Clear the bag and swap views
      localStorage.removeItem(BAG_KEY);
      if (window.SSV_cart) window.SSV_cart.render();
      layout.style.display = "none";
      emptyState.style.display = "none";
      successPanel.classList.add("show");
      successPanel.style.display = "block";
      window.scrollTo({ top: 0, behavior: "smooth" });
    }, 1600 + Math.random() * 700);
  });

  /* Keep summary in sync if the bag drawer changes it */
  if (window.SSV_cart) {
    const orig = window.SSV_cart.render;
    window.SSV_cart.render = function () { orig(); renderSummary(); };
  }

  // Default select the standard option visually
  const std = form.querySelector('input[name="delivery"][value="standard"]');
  if (std) std.closest(".radio-card").classList.add("is-selected");

  renderSummary();
})();
