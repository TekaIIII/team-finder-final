document.addEventListener("DOMContentLoaded", () => {
  async function sendRequest(url) {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": window.getCookie("csrftoken")
      },
      body: JSON.stringify({})
    });
    if (response.redirected) {
      window.location.href = response.url;
      return null;
    }
    const data = await response.json().catch(() => ({}));
    if (!response.ok || data.status !== "ok") {
      throw new Error(data.error || "Не удалось выполнить действие.");
    }
    return data;
  }
  function connectButton(id, getAddress) {
    const button = document.getElementById(id);
    if (!button) return;
    button.addEventListener("click", async event => {
      event.preventDefault();
      if (button.disabled) return;
      button.disabled = true;
      try {
        const data = await sendRequest(getAddress(button));
        if (data) window.location.reload();
      } catch (error) {
        button.disabled = false;
        if (window.toast) {
          window.toast(error.message, {
            type: "error"
          });
        } else {
          window.alert(error.message);
        }
      }
    });
  }
  connectButton("complete-project-btn", button => `/projects/${button.dataset.id}/complete/`);
  connectButton("participate-btn", button => `/projects/${button.dataset.project}/toggle-participate/`);
  const form = document.querySelector(".project-create-form");
  if (!form) return;
  const titleInput = form.elements.namedItem("name");
  const descriptionInput = form.elements.namedItem("description");
  const statusInput = form.elements.namedItem("status");
  if (!titleInput || !descriptionInput || !statusInput) return;
  const preview = document.createElement("fieldset");
  const caption = document.createElement("legend");
  const title = document.createElement("h3");
  const description = document.createElement("p");
  const statusLabel = document.createElement("p");
  const wordCount = document.createElement("small");
  caption.textContent = "Предпросмотр карточки";
  Object.assign(preview.style, {
    border: "1px solid #d1d5db",
    borderRadius: "12px",
    padding: "16px",
    marginBottom: "20px",
    backgroundColor: "#f9fafb",
    minWidth: "0"
  });
  title.style.overflowWrap = "anywhere";
  description.style.overflowWrap = "anywhere";
  wordCount.style.color = "#6b7280";
  preview.append(caption, title, description, statusLabel, wordCount);
  form.insertBefore(preview, form.querySelector(".form-actions"));
  function shortenText(text, limit) {
    const normalized = text.trim().replace(/\s+/g, " ");
    if (normalized.length <= limit) return normalized;
    const part = normalized.slice(0, limit - 1);
    const lastSpace = part.lastIndexOf(" ");
    return (lastSpace > 0 ? part.slice(0, lastSpace) : part) + "…";
  }
  function updatePreview() {
    const text = descriptionInput.value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    title.textContent = titleInput.value.trim() || "Название вашего проекта";
    description.textContent = shortenText(text, 150) || "Здесь появится краткое описание проекта.";
    statusLabel.textContent = statusInput.value === "closed" ? "Статус: закрыт" : "Статус: открыт";
    wordCount.textContent = `Слов в описании: ${words}`;
  }
  form.addEventListener("input", updatePreview);
  form.addEventListener("change", updatePreview);
  updatePreview();
});
