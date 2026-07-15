/* =========================================================================
   Newsletter + Contact form validation.
   No backend yet — these validate client-side and show a success state.
   Wire to a real endpoint (Formspree / Netlify Forms / API route) later.
   ========================================================================= */
(function () {
  "use strict";
  const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  /* ---------- Newsletter ---------- */
  document.querySelectorAll("[data-newsletter-form]").forEach((form) => {
    const input = form.querySelector('input[type="email"]');
    const success = form.parentElement.querySelector(".newsletter-success");
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (!input.value.trim() || !emailRe.test(input.value.trim())) {
        input.focus();
        input.style.borderColor = "#b3603a";
        return;
      }
      form.style.display = "none";
      if (success) success.classList.add("show");
    });
    input && input.addEventListener("input", () => (input.style.borderColor = ""));
  });

  /* ---------- Contact ---------- */
  const contactForm = document.querySelector("[data-contact-form]");
  if (contactForm) {
    const params = new URLSearchParams(location.search);
    if (params.get("ref") === "bag" && window.SSV_cart) {
      const bag = window.SSV_cart.getBag();
      const dataEl = document.getElementById("ssv-data");
      if (bag.length && dataEl) {
        try {
          const map = JSON.parse(dataEl.textContent);
          const lines = bag.map((i) => {
            const p = map[i.id];
            return p ? `• ${p.name} (Size ${i.size}, ${"$" + p.price})` : null;
          }).filter(Boolean);
          const msg = contactForm.querySelector('[name="message"]');
          const subjectSel = contactForm.querySelector('[name="subject"]');
          if (msg && lines.length) {
            msg.value = `Hi — I'd like to reserve the following pieces:\n\n${lines.join("\n")}\n\nPlease let me know how to complete the hold.`;
          }
          if (subjectSel) subjectSel.value = "reserve";
        } catch (err) { /* ignore malformed data */ }
      }
    }

    contactForm.addEventListener("submit", (e) => {
      e.preventDefault();
      let valid = true;
      contactForm.querySelectorAll("[required]").forEach((field) => {
        const wrap = field.closest(".field");
        let ok = field.value.trim().length > 0;
        if (field.type === "email") ok = ok && emailRe.test(field.value.trim());
        wrap.classList.toggle("has-error", !ok);
        if (!ok) valid = false;
      });
      if (!valid) {
        const firstError = contactForm.querySelector(".has-error input, .has-error textarea, .has-error select");
        if (firstError) firstError.focus();
        return;
      }
      contactForm.style.display = "none";
      const success = document.querySelector("[data-contact-success]");
      if (success) success.classList.add("show");
    });

    contactForm.querySelectorAll("input, textarea, select").forEach((field) => {
      field.addEventListener("input", () => field.closest(".field").classList.remove("has-error"));
    });
  }
})();
