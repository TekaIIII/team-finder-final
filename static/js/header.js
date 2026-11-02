document.addEventListener("DOMContentLoaded", () => {
  const button = document.querySelector(".user-menu");
  const panel = document.getElementById("userSidebar");
  const overlay = document.getElementById("sidebarOverlay");
  if (!button || !panel || !overlay) return;
  button.setAttribute("role", "button");
  button.setAttribute("tabindex", "0");
  button.setAttribute("aria-controls", panel.id);
  button.setAttribute("aria-expanded", "false");
  panel.setAttribute("aria-hidden", "true");
  function openMenu() {
    panel.classList.add("show");
    overlay.classList.add("show");
    button.setAttribute("aria-expanded", "true");
    panel.setAttribute("aria-hidden", "false");
  }
  function closeMenu() {
    panel.classList.remove("show");
    overlay.classList.remove("show");
    button.setAttribute("aria-expanded", "false");
    panel.setAttribute("aria-hidden", "true");
  }
  function toggleMenu() {
    if (panel.classList.contains("show")) closeMenu();else openMenu();
  }
  button.addEventListener("click", event => {
    event.preventDefault();
    toggleMenu();
  });
  button.addEventListener("keydown", event => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      toggleMenu();
    }
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && panel.classList.contains("show")) {
      closeMenu();
      button.focus();
    }
  });
  document.addEventListener("click", event => {
    const isInside = panel.contains(event.target) || button.contains(event.target);
    if (!isInside) closeMenu();
  });
});
