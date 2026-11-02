// Global utilities
(function () {
  // CSRF cookie utility
  if (!window.getCookie) {
    window.getCookie = function (name) {
      let value = null;
      if (document.cookie && document.cookie !== "") {
        const parts = document.cookie.split(";");
        for (let part of parts) {
          part = part.trim();
          if (part.startsWith(name + "=")) {
            value = decodeURIComponent(part.substring(name.length + 1));
            break;
          }
        }
      }
      return value;
    };
  }

  // Minimal toast notifications
  if (!window.toast) {
    function getContainer() {
      let container = document.getElementById("tf-toast-container");
      if (container) return container;
      container = document.createElement("div");
      container.id = "tf-toast-container";
      container.style.position = "fixed";
      container.style.left = "50%";
      container.style.top = "50%";
      container.style.transform = "translate(-50%, -50%)";
      container.style.display = "flex";
      container.style.flexDirection = "column";
      container.style.alignItems = "center";
      container.style.gap = "8px";
      container.style.zIndex = "2147483647";
      document.body.appendChild(container);
      return container;
    }
    window.toast = function (message, options = {}) {
      const {
        type = "info",
        duration = 2200
      } = options;
      const container = getContainer();
      const toastElement = document.createElement("div");
      toastElement.textContent = message;
      toastElement.style.maxWidth = "90vw";
      toastElement.style.background = type === "error" ? "rgba(220, 38, 38, 0.95)" : "rgba(17,17,17,0.92)";
      toastElement.style.color = "#fff";
      toastElement.style.padding = "12px 16px";
      toastElement.style.borderRadius = "8px";
      toastElement.style.boxShadow = "0 6px 20px rgba(0,0,0,0.25)";
      toastElement.style.fontSize = "14px";
      toastElement.style.lineHeight = "1.35";
      toastElement.style.wordBreak = "break-all";
      toastElement.style.textAlign = "center";
      toastElement.style.opacity = "0";
      toastElement.style.transition = "opacity 180ms ease";
      container.appendChild(toastElement);
      requestAnimationFrame(() => {
        toastElement.style.opacity = "1";
      });
      setTimeout(() => {
        toastElement.style.opacity = "0";
        setTimeout(() => {
          toastElement.remove();
        }, 200);
      }, Math.max(1200, duration));
    };
  }
})();
