document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("skills-container");
  const addButton = document.getElementById("add-skill-btn");
  const inputWrapper = document.getElementById("skill-input-wrapper");
  const input = document.getElementById("skill-input");
  const suggestions = document.getElementById("skill-suggestions");
  if (!container || !addButton || !inputWrapper || !input || !suggestions) {
    return;
  }
  const projectId = container.dataset.projectId;
  const baseUrl = `/projects/${projectId}/skills/`;
  let timer;
  let requestVersion = 0;
  let isAdding = false;
  input.maxLength = 124;
  function showError(error) {
    if (window.toast) {
      window.toast(error.message, {
        type: "error"
      });
    } else {
      window.alert(error.message);
    }
  }
  async function sendPost(url, body = {}) {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": window.getCookie("csrftoken")
      },
      body: JSON.stringify(body)
    });
    if (response.redirected) {
      throw new Error("Войдите в аккаунт.");
    }
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.error || "Не удалось выполнить запрос.");
    }
    return data;
  }
  function hideInput() {
    clearTimeout(timer);
    requestVersion += 1;
    inputWrapper.classList.add("hidden");
    suggestions.classList.add("hidden");
    suggestions.replaceChildren();
    addButton.classList.remove("hidden");
  }
  async function addSkill(body) {
    if (isAdding) return;
    isAdding = true;
    input.disabled = true;
    try {
      const skill = await sendPost(`${baseUrl}add/`, body);
      if (!container.querySelector(`.skill-chip[data-id="${skill.id}"]`)) {
        const chip = document.createElement("span");
        chip.className = "skill-chip";
        chip.dataset.id = skill.id;
        chip.textContent = `${skill.name} `;
        const button = document.createElement("button");
        button.type = "button";
        button.className = "remove-skill-btn";
        button.textContent = "×";
        button.setAttribute("aria-label", `Удалить ${skill.name}`);
        chip.appendChild(button);
        container.insertBefore(chip, addButton);
        container.querySelector(".skill-empty")?.remove();
      }
      input.value = "";
      hideInput();
    } catch (error) {
      showError(error);
    } finally {
      isAdding = false;
      input.disabled = false;
    }
  }
  addButton.addEventListener("click", () => {
    addButton.classList.add("hidden");
    inputWrapper.classList.remove("hidden");
    input.value = "";
    suggestions.replaceChildren();
    suggestions.classList.add("hidden");
    input.focus();
  });
  input.addEventListener("input", () => {
    clearTimeout(timer);
    const currentVersion = ++requestVersion;
    const query = input.value.trim();
    suggestions.replaceChildren();
    suggestions.classList.add("hidden");
    if (!query) return;
    timer = setTimeout(async () => {
      try {
        const response = await fetch(`/projects/skills/?q=${encodeURIComponent(query)}`);
        if (!response.ok) {
          throw new Error("Не удалось загрузить навыки.");
        }
        const skills = await response.json();
        if (currentVersion !== requestVersion) return;
        function addSuggestion(caption, body, className) {
          const item = document.createElement("li");
          item.textContent = caption;
          item.className = className;
          item.addEventListener("mousedown", event => {
            event.preventDefault();
            addSkill(body);
          });
          suggestions.appendChild(item);
        }
        skills.forEach(skill => {
          addSuggestion(skill.name, {
            skill_id: skill.id
          }, "suggestion-item");
        });
        const hasExactMatch = skills.some(skill => skill.name.toLowerCase() === query.toLowerCase());
        if (!hasExactMatch) {
          addSuggestion(`Создать «${query}»`, {
            name: query
          }, "create-new");
        }
        suggestions.classList.remove("hidden");
      } catch (error) {
        if (currentVersion === requestVersion) {
          showError(error);
        }
      }
    }, 200);
  });
  input.addEventListener("keydown", event => {
    if (event.key === "Escape") {
      hideInput();
    }
    if (event.key === "Enter") {
      event.preventDefault();
      const name = input.value.trim();
      if (name) {
        addSkill({
          name: name
        });
      }
    }
  });
  input.addEventListener("blur", hideInput);
  container.addEventListener("click", async event => {
    const button = event.target.closest(".remove-skill-btn");
    if (!button) return;
    const chip = button.closest(".skill-chip");
    button.disabled = true;
    try {
      await sendPost(`${baseUrl}${chip.dataset.id}/remove/`);
      chip.remove();
      if (!container.querySelector(".skill-chip")) {
        const emptyLabel = document.createElement("span");
        emptyLabel.className = "skill-empty";
        emptyLabel.textContent = "Навыки не указаны";
        container.insertBefore(emptyLabel, addButton);
      }
    } catch (error) {
      button.disabled = false;
      showError(error);
    }
  });
});
