/* =========================================================================
   Site-wide behavior: header, mobile nav, drawers, reveal animations,
   accordions, tabs, counters, back-to-top.
   ========================================================================= */
(function () {
  "use strict";

  document.getElementById("year") && (document.getElementById("year").textContent = new Date().getFullYear());

  /* ---------- Header scroll state ---------- */
  const header = document.querySelector(".site-header");
  if (header) {
    const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------- Mobile nav ---------- */
  const navToggle = document.querySelector(".nav-toggle");
  if (navToggle) {
    navToggle.addEventListener("click", () => {
      const open = document.documentElement.classList.toggle("nav-open");
      navToggle.setAttribute("aria-expanded", String(open));
      document.body.style.overflow = open ? "hidden" : "";
    });
    document.querySelectorAll(".mobile-menu a").forEach((a) =>
      a.addEventListener("click", () => {
        document.documentElement.classList.remove("nav-open");
        document.body.style.overflow = "";
      })
    );
  }

  /* ---------- Drawers (bag / wishlist / filters) ---------- */
  let overlay = document.querySelector(".drawer-overlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.className = "drawer-overlay";
    document.body.appendChild(overlay);
  }
  let lastFocused = null;

  function openDrawer(name) {
    const d = document.querySelector(`.drawer[data-drawer="${name}"]`);
    if (!d) return;
    lastFocused = document.activeElement;
    overlay.classList.add("is-open");
    d.classList.add("is-open");
    document.body.style.overflow = "hidden";
    const focusable = d.querySelector("button, a, input");
    if (focusable) focusable.focus({ preventScroll: true });
  }
  function closeDrawers() {
    document.querySelectorAll(".drawer.is-open").forEach((d) => d.classList.remove("is-open"));
    overlay.classList.remove("is-open");
    document.body.style.overflow = "";
    if (lastFocused) lastFocused.focus({ preventScroll: true });
  }
  document.addEventListener("click", (e) => {
    const opener = e.target.closest("[data-drawer-open]");
    if (opener) { e.preventDefault(); openDrawer(opener.getAttribute("data-drawer-open")); }
    if (e.target.closest("[data-drawer-close]") || e.target === overlay) closeDrawers();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") { closeDrawers(); document.documentElement.classList.remove("nav-open"); }
  });

  /* ---------- Reveal on scroll ---------- */
  const revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && revealEls.length) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add("is-visible"));
  }

  /* ---------- Counters ---------- */
  const counters = document.querySelectorAll("[data-count-to]");
  if (counters.length) {
    const format = (v, decimals) => (decimals ? v.toFixed(decimals) : Math.round(v)).toLocaleString("en-US");
    const animateCount = (el) => {
      const target = parseFloat(el.getAttribute("data-count-to"));
      const decimals = parseInt(el.getAttribute("data-decimals") || "0", 10);
      const dur = 1600;
      const start = performance.now();
      function tick(now) {
        const p = Math.min(1, (now - start) / dur);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = format(target * eased, decimals);
        if (p < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    };
    if ("IntersectionObserver" in window) {
      const io2 = new IntersectionObserver(
        (entries) => entries.forEach((e2) => { if (e2.isIntersecting) { animateCount(e2.target); io2.unobserve(e2.target); } }),
        { threshold: 0.4 }
      );
      counters.forEach((c) => io2.observe(c));
    } else {
      counters.forEach(animateCount);
    }
  }

  /* ---------- Accordions ---------- */
  document.addEventListener("click", (e) => {
    const trigger = e.target.closest(".accordion-trigger");
    if (!trigger) return;
    const item = trigger.closest(".accordion-item");
    const panel = item.querySelector(".accordion-panel");
    const isOpen = item.classList.contains("is-open");
    const group = item.closest("[data-accordion-single]");
    if (group) {
      group.querySelectorAll(".accordion-item.is-open").forEach((other) => {
        if (other !== item) {
          other.classList.remove("is-open");
          other.querySelector(".accordion-panel").style.maxHeight = null;
          other.querySelector(".accordion-trigger").setAttribute("aria-expanded", "false");
        }
      });
    }
    item.classList.toggle("is-open", !isOpen);
    trigger.setAttribute("aria-expanded", String(!isOpen));
    panel.style.maxHeight = !isOpen ? panel.scrollHeight + "px" : null;
  });

  /* ---------- Tabs ---------- */
  document.addEventListener("click", (e) => {
    const tabBtn = e.target.closest("[data-tab-trigger]");
    if (!tabBtn) return;
    const wrap = tabBtn.closest("[data-tabs]");
    const key = tabBtn.getAttribute("data-tab-trigger");
    wrap.querySelectorAll("[data-tab-trigger]").forEach((b) => b.classList.toggle("is-active", b === tabBtn));
    wrap.querySelectorAll("[data-tab-panel]").forEach((p) => p.classList.toggle("is-active", p.getAttribute("data-tab-panel") === key));
  });

  /* ---------- Back to top ---------- */
  const backToTop = document.querySelector(".back-to-top");
  if (backToTop) {
    window.addEventListener("scroll", () => backToTop.classList.toggle("show", window.scrollY > 900), { passive: true });
    backToTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  }

  /* ---------- Duplicate marquee content for seamless loop ---------- */
  document.querySelectorAll(".marquee-track[data-duplicate]").forEach((track) => {
    track.innerHTML += track.innerHTML;
  });
})();
