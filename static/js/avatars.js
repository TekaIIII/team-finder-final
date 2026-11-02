// Если файл недоступен, под картинкой остаётся буква имени.
document.addEventListener("error", event => {
  if (event.target.matches?.(".buk-ava-img")) {
    event.target.hidden = true;
  }
}, true);
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".buk-ava-img[src]").forEach(img => {
    if (img.complete && img.naturalWidth === 0) img.hidden = true;
  });
  const input = document.getElementById("id_avatar");
  const img = document.querySelector(".avatar-preview .buk-ava-img");
  const button = document.getElementById("vybrat-avatar");
  if (!input || !img || !button) return;
  const clearCheckbox = document.getElementById("avatar-clear_id");
  const name = document.getElementById("id_name");
  const initial = document.querySelector(".avatar-preview .buk-ava-letter");
  const caption = document.getElementById("avatar-note");
  const originalUrl = img.getAttribute("src");
  let previewUrl = null;
  function releasePreview() {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      previewUrl = null;
    }
  }
  function updateInitial() {
    if (name && initial) {
      const text = name.value.trim();
      initial.textContent = Array.from(text)[0]?.toUpperCase() || "?";
    }
  }
  button.addEventListener("click", () => input.click());
  name?.addEventListener("input", updateInitial);
  input.addEventListener("change", () => {
    releasePreview();
    const file = input.files[0];
    if (!file) {
      if (originalUrl && !clearCheckbox?.checked) {
        img.src = originalUrl;
        img.hidden = false;
      } else {
        img.hidden = true;
      }
      return;
    }
    if (clearCheckbox) clearCheckbox.checked = false;
    previewUrl = URL.createObjectURL(file);
    img.src = previewUrl;
    img.hidden = false;
    if (caption) caption.textContent = "Картинка выбрана. Нажмите «Сохранить», чтобы применить её.";
  });
  clearCheckbox?.addEventListener("change", () => {
    releasePreview();
    if (clearCheckbox.checked) {
      input.value = "";
      img.hidden = true;
      updateInitial();
      if (caption) caption.textContent = "После сохранения аватаром станет буква имени.";
    } else if (originalUrl) {
      img.src = originalUrl;
      img.hidden = false;
    }
  });
  window.addEventListener("pagehide", releasePreview);
});
