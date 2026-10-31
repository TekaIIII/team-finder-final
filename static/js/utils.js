// Global utilities
(function () {
  // CSRF cookie utility
  if (!window.getCookie) {
    window.getCookie = function (imya) {
      let znach = null;
      if (document.cookie && document.cookie !== "") {
        const chasti = document.cookie.split(";");
        for (let chast of chasti) {
          chast = chast.trim();
          if (chast.startsWith(imya + "=")) {
            znach = decodeURIComponent(chast.substring(imya.length + 1));
            break;
          }
        }
      }
      return znach;
    };
  }

  // Minimal toast notifications
  if (!window.toast) {
    function poluchitObl() {
      let c = document.getElementById("tf-toast-container");
      if (c) return c;
      c = document.createElement("div");
      c.id = "tf-toast-container";
      c.style.position = "fixed";
      c.style.left = "50%";
      c.style.top = "50%";
      c.style.transform = "translate(-50%, -50%)";
      c.style.display = "flex";
      c.style.flexDirection = "column";
      c.style.alignItems = "center";
      c.style.gap = "8px";
      c.style.zIndex = "2147483647";
      document.body.appendChild(c);
      return c;
    }
    window.toast = function (tekst, param = {}) {
      const {
        type: tip = "info",
        duration: ms = 2200
      } = param;
      const obl = poluchitObl();
      const el = document.createElement("div");
      el.textContent = tekst;
      el.style.maxWidth = "90vw";
      el.style.background = tip === "error" ? "rgba(220, 38, 38, 0.95)" : "rgba(17,17,17,0.92)";
      el.style.color = "#fff";
      el.style.padding = "12px 16px";
      el.style.borderRadius = "8px";
      el.style.boxShadow = "0 6px 20px rgba(0,0,0,0.25)";
      el.style.fontSize = "14px";
      el.style.lineHeight = "1.35";
      el.style.wordBreak = "break-all";
      el.style.textAlign = "center";
      el.style.opacity = "0";
      el.style.transition = "opacity 180ms ease";
      obl.appendChild(el);
      requestAnimationFrame(() => {
        el.style.opacity = "1";
      });
      setTimeout(() => {
        el.style.opacity = "0";
        setTimeout(() => {
          el.remove();
        }, 200);
      }, Math.max(1200, ms));
    };
  }
})();
