const API_BASE = "http://localhost:28000";
const tokenInput = document.getElementById("admin-token");
const saveTokenButton = document.getElementById("save-token");

const navItems = document.querySelectorAll(".nav-item");
const panels = document.querySelectorAll(".panel");

function setView(view) {
  panels.forEach((panel) => {
    panel.classList.toggle("is-visible", panel.dataset.view === view);
  });
  navItems.forEach((item) => {
    item.classList.toggle("is-active", item.dataset.view === view);
  });
}

navItems.forEach((item) => {
  item.addEventListener("click", () => setView(item.dataset.view));
});

saveTokenButton.addEventListener("click", () => {
  localStorage.setItem("admin_token", tokenInput.value.trim());
});

tokenInput.value = localStorage.getItem("admin_token") || "";

async function api(path, options = {}) {
  const headers = options.headers || {};
  const token = localStorage.getItem("admin_token") || "";
  if (token) {
    headers["X-Admin-Token"] = token;
  }
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

document.getElementById("search-content").addEventListener("click", async () => {
  const type = document.getElementById("content-type").value;
  const keyword = document.getElementById("content-keyword").value;
  const list = document.getElementById("content-list");
  list.innerHTML = "加载中...";
  try {
    const data = await api(`/${type}?keyword=${encodeURIComponent(keyword)}`);
    const items = data.items || data;
    list.innerHTML = items
      .map((item) => `<div class="list-item">${JSON.stringify(item)}</div>`)
      .join("");
  } catch (err) {
    list.innerHTML = `<div class="list-item">错误：${err.message}</div>`;
  }
});

document.getElementById("get-template").addEventListener("click", async () => {
  const entity = document.getElementById("import-entity").value;
  const result = document.getElementById("import-result");
  try {
    const data = await api(`/admin/import/template?entity_type=${entity}`);
    result.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    result.textContent = err.message;
  }
});

document.getElementById("validate-import").addEventListener("click", async () => {
  const entity = document.getElementById("import-entity").value;
  const jsonText = document.getElementById("import-json").value || '{"items":[]}';
  const result = document.getElementById("import-result");
  try {
    const payload = JSON.parse(jsonText);
    payload.entity_type = entity;
    const data = await api("/admin/import/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    result.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    result.textContent = err.message;
  }
});

document.getElementById("execute-import").addEventListener("click", async () => {
  const entity = document.getElementById("import-entity").value;
  const mode = document.getElementById("import-mode").value;
  const jsonText = document.getElementById("import-json").value || '{"items":[]}';
  const result = document.getElementById("import-result");
  try {
    const payload = JSON.parse(jsonText);
    payload.entity_type = entity;
    payload.mode = mode;
    const data = await api("/admin/import/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    result.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    result.textContent = err.message;
  }
});

document.getElementById("save-exam-config").addEventListener("click", async () => {
  const name = document.getElementById("exam-name").value;
  const duration = Number(document.getElementById("exam-duration").value || 30);
  const level = document.getElementById("exam-level").value || null;
  const distributionText = document.getElementById("exam-distribution").value;
  const result = document.getElementById("exam-config-result");
  try {
    const payload = {
      name,
      duration_minutes: duration,
      level,
      distribution: JSON.parse(distributionText),
    };
    const data = await api("/exam/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    result.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    result.textContent = err.message;
  }
});

document.getElementById("load-jobs").addEventListener("click", async () => {
  const status = document.getElementById("job-status").value;
  const list = document.getElementById("job-list");
  list.innerHTML = "加载中...";
  try {
    const data = await api(`/admin/import/jobs${status ? `?status=${status}` : ""}`);
    list.innerHTML = data.items
      .map((item) => `<div class="list-item">#${item.id} ${item.status} ${item.entity_type}</div>`)
      .join("");
  } catch (err) {
    list.innerHTML = `<div class="list-item">错误：${err.message}</div>`;
  }
});

document.getElementById("load-audit").addEventListener("click", async () => {
  const action = document.getElementById("audit-action").value;
  const list = document.getElementById("audit-list");
  list.innerHTML = "加载中...";
  try {
    const data = await api(`/admin/audit${action ? `?action=${action}` : ""}`);
    list.innerHTML = data.items
      .map((item) => `<div class="list-item">#${item.id} ${item.action}</div>`)
      .join("");
  } catch (err) {
    list.innerHTML = `<div class="list-item">错误：${err.message}</div>`;
  }
});

setView("dashboard");
