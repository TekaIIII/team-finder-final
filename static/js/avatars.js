// Если файл недоступен, под картинкой остаётся буква имени.
document.addEventListener("error", (sob) => {
  if (sob.target.matches?.(".buk-ava-img")) {
    sob.target.hidden = true;
  }
}, true);

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".buk-ava-img[src]").forEach((img) => {
    if (img.complete && img.naturalWidth === 0) img.hidden = true;
  });

  const vvod = document.getElementById("id_avatar");
  const img = document.querySelector(".avatar-preview .buk-ava-img");
  const knop = document.getElementById("vybrat-avatar");
  if (!vvod || !img || !knop) return;

  const sbros = document.getElementById("id_sbros_avy");
  const imya = document.getElementById("id_name");
  const bukva = document.querySelector(".avatar-preview .buk-ava-letter");
  const podpis = document.getElementById("avatar-note");
  const starAdr = img.getAttribute("src");
  let vremAdr = null;

  function osvobodit() {
    if (vremAdr) {
      URL.revokeObjectURL(vremAdr);
      vremAdr = null;
    }
  }

  function obnovitBukvu() {
    if (imya && bukva) {
      const s = imya.value.trim();
      bukva.textContent = Array.from(s)[0]?.toUpperCase() || "?";
    }
  }

  knop.addEventListener("click", () => vvod.click());
  imya?.addEventListener("input", obnovitBukvu);

  vvod.addEventListener("change", () => {
    osvobodit();
    const fail = vvod.files[0];
    if (!fail) {
      if (starAdr && !sbros?.checked) {
        img.src = starAdr;
        img.hidden = false;
      } else {
        img.hidden = true;
      }
      return;
    }
    if (sbros) sbros.checked = false;
    vremAdr = URL.createObjectURL(fail);
    img.src = vremAdr;
    img.hidden = false;
    if (podpis) podpis.textContent = "Картинка выбрана. Нажмите «Сохранить», чтобы применить её.";
  });

  sbros?.addEventListener("change", () => {
    osvobodit();
    if (sbros.checked) {
      vvod.value = "";
      img.hidden = true;
      obnovitBukvu();
      if (podpis) podpis.textContent = "После сохранения аватаром станет буква имени.";
    } else if (starAdr) {
      img.src = starAdr;
      img.hidden = false;
    }
  });

  window.addEventListener("pagehide", osvobodit);
});
