/* Unsplash URL helper — consistent, right-sized image requests. */
(function (global) {
  function img(id, w, q) {
    if (!id) return "";
    if (id.startsWith("http")) return id;
    return `https://images.unsplash.com/photo-${id}?auto=format&fit=crop&w=${w || 1200}&q=${q || 78}`;
  }
  global.SSV_img = img;
})(window);
