document.addEventListener("DOMContentLoaded", () => {
  const knop = document.querySelector(".user-menu");
  const panel = document.getElementById("userSidebar");
  const fon = document.getElementById("sidebarOverlay");
  if (!knop || !panel || !fon) return;

  knop.setAttribute("role", "button");
  knop.setAttribute("tabindex", "0");
  knop.setAttribute("aria-controls", panel.id);
  knop.setAttribute("aria-expanded", "false");
  panel.setAttribute("aria-hidden", "true");

  function otkryt() {
    panel.classList.add("show");
    fon.classList.add("show");
    knop.setAttribute("aria-expanded", "true");
    panel.setAttribute("aria-hidden", "false");
  }

  function zakryt() {
    panel.classList.remove("show");
    fon.classList.remove("show");
    knop.setAttribute("aria-expanded", "false");
    panel.setAttribute("aria-hidden", "true");
  }

  function pereklyuchit() {
    if (panel.classList.contains("show")) zakryt();
    else otkryt();
  }

  knop.addEventListener("click", (sob) => {
    sob.preventDefault();
    pereklyuchit();
  });

  knop.addEventListener("keydown", (sob) => {
    if (sob.key === "Enter" || sob.key === " ") {
      sob.preventDefault();
      pereklyuchit();
    }
  });

  document.addEventListener("keydown", (sob) => {
    if (sob.key === "Escape" && panel.classList.contains("show")) {
      zakryt();
      knop.focus();
    }
  });

  document.addEventListener("click", (sob) => {
    const vnutri = panel.contains(sob.target) || knop.contains(sob.target);
    if (!vnutri) zakryt();
  });
});
