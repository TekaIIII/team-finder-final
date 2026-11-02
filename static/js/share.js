document.addEventListener("click", async event => {
  const button = event.target.closest(".share-button");
  if (!button) return;
  event.preventDefault();
  const url = new URL(button.dataset.url || window.location.href, window.location.origin);
  if (/^\/(users|projects)\/[0-9]+$/.test(url.pathname)) {
    url.pathname += "/";
  }
  const shareUrl = url.href;
  try {
    if (!navigator.clipboard || typeof navigator.clipboard.writeText !== "function") {
      window.prompt("Скопируйте ссылку:", shareUrl);
      return;
    }
    await navigator.clipboard.writeText(shareUrl);
    if (window.toast) {
      window.toast("Ссылка скопирована");
    } else {
      window.alert("Ссылка скопирована");
    }
  } catch {
    window.prompt("Скопируйте ссылку:", shareUrl);
  }
});
