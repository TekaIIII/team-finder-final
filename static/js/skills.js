document.addEventListener("DOMContentLoaded", () => {
  const obl = document.getElementById("skills-container");
  const dobBtn = document.getElementById("add-skill-btn");
  const obert = document.getElementById("skill-input-wrapper");
  const vvod = document.getElementById("skill-input");
  const podsk = document.getElementById("skill-suggestions");
  if (!obl || !dobBtn || !obert || !vvod || !podsk) {
    return;
  }
  const prId = obl.dataset.projectId;
  const baza = `/projects/${prId}/skills/`;
  let taymer;
  let rev = 0;
  let dobavlyaem = false;
  vvod.maxLength = 124;
  function pokazatOsh(err) {
    if (window.toast) {
      window.toast(err.message, {
        type: "error"
      });
    } else {
      window.alert(err.message);
    }
  }
  async function poslat(adr, telo = {}) {
    const otv = await fetch(adr, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": window.getCookie("csrftoken")
      },
      body: JSON.stringify(telo)
    });
    if (otv.redirected) {
      throw new Error("Войдите в аккаунт.");
    }
    const dann = await otv.json().catch(() => ({}));
    if (!otv.ok) {
      throw new Error(dann.error || "Не удалось выполнить запрос.");
    }
    return dann;
  }
  function skrytVvod() {
    clearTimeout(taymer);
    rev += 1;
    obert.classList.add("hidden");
    podsk.classList.add("hidden");
    podsk.replaceChildren();
    dobBtn.classList.remove("hidden");
  }
  async function dobavitNav(telo) {
    if (dobavlyaem) return;
    dobavlyaem = true;
    vvod.disabled = true;
    try {
      const nav = await poslat(`${baza}add/`, telo);
      if (!obl.querySelector(`.skill-chip[data-id="${nav.id}"]`)) {
        const teg = document.createElement("span");
        teg.className = "skill-chip";
        teg.dataset.id = nav.id;
        teg.textContent = `${nav.name} `;
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "remove-skill-btn";
        btn.textContent = "×";
        btn.setAttribute("aria-label", `Удалить ${nav.name}`);
        teg.appendChild(btn);
        obl.insertBefore(teg, dobBtn);
        obl.querySelector(".skill-empty")?.remove();
      }
      vvod.value = "";
      skrytVvod();
    } catch (err) {
      pokazatOsh(err);
    } finally {
      dobavlyaem = false;
      vvod.disabled = false;
    }
  }
  dobBtn.addEventListener("click", () => {
    dobBtn.classList.add("hidden");
    obert.classList.remove("hidden");
    vvod.value = "";
    podsk.replaceChildren();
    podsk.classList.add("hidden");
    vvod.focus();
  });
  vvod.addEventListener("input", () => {
    clearTimeout(taymer);
    const revZap = ++rev;
    const q = vvod.value.trim();
    podsk.replaceChildren();
    podsk.classList.add("hidden");
    if (!q) return;
    taymer = setTimeout(async () => {
      try {
        const otv = await fetch(`/projects/skills/?q=${encodeURIComponent(q)}`);
        if (!otv.ok) {
          throw new Error("Не удалось загрузить навыки.");
        }
        const navyki = await otv.json();
        if (revZap !== rev) return;
        function dobavitPunkt(podpis, telo, klass) {
          const punkt = document.createElement("li");
          punkt.textContent = podpis;
          punkt.className = klass;
          punkt.addEventListener("mousedown", sob => {
            sob.preventDefault();
            dobavitNav(telo);
          });
          podsk.appendChild(punkt);
        }
        navyki.forEach(nav => {
          dobavitPunkt(nav.name, {
            skill_id: nav.id
          }, "suggestion-item");
        });
        const tochno = navyki.some(nav => nav.name.toLowerCase() === q.toLowerCase());
        if (!tochno) {
          dobavitPunkt(`Создать «${q}»`, {
            name: q
          }, "create-new");
        }
        podsk.classList.remove("hidden");
      } catch (err) {
        if (revZap === rev) {
          pokazatOsh(err);
        }
      }
    }, 200);
  });
  vvod.addEventListener("keydown", sob => {
    if (sob.key === "Escape") {
      skrytVvod();
    }
    if (sob.key === "Enter") {
      sob.preventDefault();
      const imya = vvod.value.trim();
      if (imya) {
        dobavitNav({
          name: imya
        });
      }
    }
  });
  vvod.addEventListener("blur", skrytVvod);
  obl.addEventListener("click", async sob => {
    const btn = sob.target.closest(".remove-skill-btn");
    if (!btn) return;
    const teg = btn.closest(".skill-chip");
    btn.disabled = true;
    try {
      await poslat(`${baza}${teg.dataset.id}/remove/`);
      teg.remove();
      if (!obl.querySelector(".skill-chip")) {
        const pusto = document.createElement("span");
        pusto.className = "skill-empty";
        pusto.textContent = "Навыки не указаны";
        obl.insertBefore(pusto, dobBtn);
      }
    } catch (err) {
      btn.disabled = false;
      pokazatOsh(err);
    }
  });
});
