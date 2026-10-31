document.addEventListener("click", async sob => {
  const btn = sob.target.closest(".share-button");
  if (!btn) return;
  sob.preventDefault();
  const adr = new URL(btn.dataset.url || window.location.href, window.location.origin);
  if (/^\/(users|projects)\/[0-9]+$/.test(adr.pathname)) {
    adr.pathname += "/";
  }
  const ssyl = adr.href;
  try {
    if (!navigator.clipboard || typeof navigator.clipboard.writeText !== "function") {
      window.prompt("Скопируйте ссылку:", ssyl);
      return;
    }
    await navigator.clipboard.writeText(ssyl);
    if (window.toast) {
      window.toast("Ссылка скопирована");
    } else {
      window.alert("Ссылка скопирована");
    }
  } catch {
    window.prompt("Скопируйте ссылку:", ssyl);
  }
});
