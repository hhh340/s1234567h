/* Product detail page: gallery + size select interactions. */
(function () {
  "use strict";
  const mainImg = document.querySelector("[data-gallery-main]");
  document.querySelectorAll("[data-gallery-thumb]").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-gallery-thumb]").forEach((b) => b.classList.remove("is-active"));
      btn.classList.add("is-active");
      if (mainImg) mainImg.src = btn.getAttribute("data-gallery-thumb");
    });
  });

  const sizeWrap = document.querySelector(".size-select");
  if (sizeWrap) {
    sizeWrap.addEventListener("click", (e) => {
      const btn = e.target.closest("button");
      if (!btn) return;
      sizeWrap.querySelectorAll("button").forEach((b) => b.classList.remove("is-active"));
      btn.classList.add("is-active");
    });
  }
})();
