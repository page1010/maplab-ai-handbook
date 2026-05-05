async function readJson(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load ${path}`);
  return res.json();
}

function renderRoles(roles) {
  const root = document.getElementById("roles");
  root.innerHTML = "";
  roles.forEach((role) => {
    const div = document.createElement("div");
    div.className = "item";
    div.innerHTML = `
      <div><strong>${role.role_id}</strong> — ${role.name}</div>
      <div class="muted">${role.purpose}</div>
      <div>${role.capabilities.map((x) => `<span class="tag">${x}</span>`).join("")}</div>
      <div class="muted">Runtimes: ${role.preferred_runtimes.map((x) => `<code>${x}</code>`).join(" ")}</div>
    `;
    root.appendChild(div);
  });
}

function renderPipelines(pipelines) {
  const root = document.getElementById("pipelines");
  root.innerHTML = "";
  pipelines.forEach((p) => {
    const div = document.createElement("div");
    div.className = "item";
    div.innerHTML = `
      <div><strong>${p.pipeline_id}</strong> — ${p.name}</div>
      <ol>${p.steps.map((s) => `<li><code>${s.id}</code> (${s.input_type} -> ${s.output_type})</li>`).join("")}</ol>
    `;
    root.appendChild(div);
  });
}

async function boot() {
  try {
    const [rolesCfg, taskCfg] = await Promise.all([
      readJson("./config/roles.json"),
      readJson("./config/task_templates.json")
    ]);
    renderRoles(rolesCfg.roles || []);
    renderPipelines(taskCfg.pipelines || []);
  } catch (err) {
    document.body.insertAdjacentHTML("beforeend", `<p style="color:#b91c1c;">${err.message}</p>`);
  }
}

boot();
