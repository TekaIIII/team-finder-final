document.addEventListener("DOMContentLoaded", () => {
  async function zapros(adr) {
    const otv = await fetch(adr, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": window.getCookie("csrftoken")
      },
      body: JSON.stringify({})
    });
    if (otv.redirected) {
      window.location.href = otv.url;
      return null;
    }
    const d = await otv.json().catch(() => ({}));
    if (!otv.ok || d.status !== "ok") {
      throw new Error(d.error || "Не удалось выполнить действие.");
    }
    return d;
  }
  function podklyuchit(id, adres) {
    const btn = document.getElementById(id);
    if (!btn) return;
    btn.addEventListener("click", async sob => {
      sob.preventDefault();
      if (btn.disabled) return;
      btn.disabled = true;
      try {
        const d = await zapros(adres(btn));
        if (d) window.location.reload();
      } catch (err) {
        btn.disabled = false;
        if (window.toast) {
          window.toast(err.message, {
            type: "error"
          });
        } else {
          window.alert(err.message);
        }
      }
    });
  }
  podklyuchit("complete-project-btn", btn => `/projects/${btn.dataset.id}/complete/`);
  podklyuchit("participate-btn", btn => `/projects/${btn.dataset.project}/toggle-participate/`);
  const frm = document.querySelector(".project-create-form");
  if (!frm) return;
  const nazv = frm.elements.namedItem("name");
  const opis = frm.elements.namedItem("description");
  const st = frm.elements.namedItem("status");
  if (!nazv || !opis || !st) return;
  const blok = document.createElement("fieldset");
  const podpis = document.createElement("legend");
  const zag = document.createElement("h3");
  const txt = document.createElement("p");
  const metka = document.createElement("p");
  const schet = document.createElement("small");
  podpis.textContent = "Предпросмотр карточки";
  Object.assign(blok.style, {
    border: "1px solid #d1d5db",
    borderRadius: "12px",
    padding: "16px",
    marginBottom: "20px",
    backgroundColor: "#f9fafb",
    minWidth: "0"
  });
  zag.style.overflowWrap = "anywhere";
  txt.style.overflowWrap = "anywhere";
  schet.style.color = "#6b7280";
  blok.append(podpis, zag, txt, metka, schet);
  frm.insertBefore(blok, frm.querySelector(".form-actions"));
  function sokratit(stroka, lim) {
    const s = stroka.trim().replace(/\s+/g, " ");
    if (s.length <= lim) return s;
    const kus = s.slice(0, lim - 1);
    const prob = kus.lastIndexOf(" ");
    return (prob > 0 ? kus.slice(0, prob) : kus) + "…";
  }
  function obnovit() {
    const s = opis.value.trim();
    const slova = s ? s.split(/\s+/).length : 0;
    zag.textContent = nazv.value.trim() || "Название вашего проекта";
    txt.textContent = sokratit(s, 150) || "Здесь появится краткое описание проекта.";
    metka.textContent = st.value === "closed" ? "Статус: закрыт" : "Статус: открыт";
    schet.textContent = `Слов в описании: ${slova}`;
  }
  frm.addEventListener("input", obnovit);
  frm.addEventListener("change", obnovit);
  obnovit();
});
