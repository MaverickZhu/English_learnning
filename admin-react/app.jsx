const { useState, useEffect } = React;

const API_BASE = "http://localhost:28000";

function App() {
  const [view, setView] = useState("content");
  const [token, setToken] = useState(localStorage.getItem("admin_token") || "");
  const [contentType, setContentType] = useState("words");
  const [contentKeyword, setContentKeyword] = useState("");
  const [contentLevel, setContentLevel] = useState("");
  const [contentTags, setContentTags] = useState("");
  const [contentItems, setContentItems] = useState([]);
  const [contentSelected, setContentSelected] = useState([]);
  const [contentTotal, setContentTotal] = useState(0);
  const [contentSkip, setContentSkip] = useState(0);
  const [contentLimit] = useState(10);
  const [bulkTags, setBulkTags] = useState("");
  const [bulkTagMode, setBulkTagMode] = useState("replace");
  const [bulkLevel, setBulkLevel] = useState("");
  const [bulkImageUrl, setBulkImageUrl] = useState("");
  const [bulkAudioUrl, setBulkAudioUrl] = useState("");
  const [jobs, setJobs] = useState([]);
  const [jobDetails, setJobDetails] = useState(null);
  const [jobErrors, setJobErrors] = useState(null);
  const [auditItems, setAuditItems] = useState([]);
  const [auditAction, setAuditAction] = useState("");
  const [editRow, setEditRow] = useState(null);
  const [editValue, setEditValue] = useState("");
  const [editField, setEditField] = useState("text");
  const [importEntity, setImportEntity] = useState("word");
  const [importMode, setImportMode] = useState("upsert");
  const [importJson, setImportJson] = useState('{"items": []}');
  const [importResult, setImportResult] = useState("");
  const [mappingJson, setMappingJson] = useState("");
  const [importFile, setImportFile] = useState(null);

  useEffect(() => {
    localStorage.setItem("admin_token", token);
  }, [token]);

  const request = async (path) => {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { "X-Admin-Token": token },
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  };

  const loadContent = async () => {
    const params = new URLSearchParams();
    params.set("limit", String(contentLimit));
    params.set("skip", String(contentSkip));
    if (contentKeyword) params.set("keyword", contentKeyword);
    if (contentLevel) params.set("level", contentLevel);
    if (contentTags) params.set("tags", contentTags);
    const data = await request(`/${contentType}?${params.toString()}`);
    const items = data.items || data;
    setContentItems(items);
    setContentTotal(data.total || items.length);
    setContentSelected([]);
  };

  useEffect(() => {
    loadContent();
  }, [contentSkip, contentType]);

  const loadJobs = async () => {
    const data = await request("/admin/import/jobs");
    setJobs(data.items || []);
  };

  const loadJobDetail = async (jobId) => {
    const data = await request(`/admin/import/jobs/${jobId}`);
    setJobDetails(data);
    const errors = await request(`/admin/import/jobs/${jobId}/errors?skip=0&limit=50`);
    setJobErrors(errors);
  };

  const loadAudit = async () => {
    const query = auditAction ? `?action=${encodeURIComponent(auditAction)}` : "";
    const data = await request(`/admin/audit${query}`);
    setAuditItems(data.items || []);
  };

  const startEdit = (item, field) => {
    setEditRow(item);
    setEditField(field);
    setEditValue(item[field] || "");
  };

  const saveEdit = async () => {
    if (!editRow) return;
    await updateItem(editField, editValue, { closeAfter: true });
  };

  const updateItem = async (field, rawValue, options = {}) => {
    if (!editRow) return;
    let value = rawValue;
    if (field === "tags" || field === "options") {
      value = String(rawValue || "")
        .split(",")
        .map((v) => v.trim())
        .filter(Boolean);
    }
    const payload = { [field]: value };
    const res = await fetch(`${API_BASE}/${contentType}/${editRow.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json", "X-Admin-Token": token },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      alert(await res.text());
      return;
    }
    if (options.closeAfter) {
      setEditRow(null);
      setEditValue("");
    } else {
      setEditRow({ ...editRow, [field]: value });
    }
    loadContent();
  };

  const uploadMedia = async (kind, file) => {
    if (!editRow || !file) {
      alert("请先选择要编辑的内容与文件");
      return;
    }
    const form = new FormData();
    form.append("kind", kind);
    form.append("file", file);
    const res = await fetch(`${API_BASE}/admin/media/upload`, {
      method: "POST",
      headers: { "X-Admin-Token": token },
      body: form,
    });
    if (!res.ok) {
      alert(await res.text());
      return;
    }
    const data = await res.json();
    const field = kind === "image" ? "image_url" : "audio_url";
    await updateItem(field, data.url, { closeAfter: false });
    setEditField(field);
    setEditValue(data.url);
  };

  const toggleSelect = (id) => {
    setContentSelected((prev) => (prev.includes(id) ? prev.filter((v) => v !== id) : [...prev, id]));
  };

  const toggleSelectAll = () => {
    if (!contentItems.length) return;
    const allSelected = contentSelected.length === contentItems.length;
    setContentSelected(allSelected ? [] : contentItems.map((item) => item.id));
  };

  const bulkDelete = async () => {
    if (!contentSelected.length) {
      alert("请选择要删除的内容");
      return;
    }
    const res = await fetch(`${API_BASE}/admin/${contentType}/bulk-delete`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Admin-Token": token },
      body: JSON.stringify({ ids: contentSelected, atomic: true }),
    });
    if (!res.ok) {
      alert(await res.text());
      return;
    }
    setContentSelected([]);
    loadContent();
  };

  const bulkAssignTags = async () => {
    if (!contentSelected.length) {
      alert("请选择要操作的内容");
      return;
    }
    const tags = bulkTags
      .split(",")
      .map((v) => v.trim())
      .filter(Boolean);
    if (!tags.length) {
      alert("请输入 tags");
      return;
    }
    const items = contentSelected.map((id) => ({ entity_id: id, tags, mode: bulkTagMode }));
    const res = await fetch(`${API_BASE}/admin/tags/bulk-assign`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Admin-Token": token },
      body: JSON.stringify({ entity_type: contentType.slice(0, -1), items, atomic: true }),
    });
    if (!res.ok) {
      alert(await res.text());
      return;
    }
    loadContent();
  };

  const bulkUpdateField = async (field, value) => {
    if (!contentSelected.length) {
      alert("请选择要操作的内容");
      return;
    }
    if (!value) {
      alert("请输入值");
      return;
    }
    const payload = { [field]: value };
    await Promise.all(
      contentSelected.map((id) =>
        fetch(`${API_BASE}/${contentType}/${id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json", "X-Admin-Token": token },
          body: JSON.stringify(payload),
        })
      )
    );
    loadContent();
  };

  const validateImport = async () => {
    const payload = JSON.parse(importJson);
    payload.entity_type = importEntity;
    const data = await request("/admin/import/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Admin-Token": token },
      body: JSON.stringify(payload),
    });
    setImportResult(JSON.stringify(data, null, 2));
  };

  const executeImport = async () => {
    const payload = JSON.parse(importJson);
    payload.entity_type = importEntity;
    payload.mode = importMode;
    const data = await request("/admin/import/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Admin-Token": token },
      body: JSON.stringify(payload),
    });
    setImportResult(JSON.stringify(data, null, 2));
  };

  const uploadImport = async () => {
    if (!importFile) {
      setImportResult("请选择文件");
      return;
    }
    const form = new FormData();
    form.append("entity_type", importEntity);
    form.append("mode", importMode);
    if (mappingJson) form.append("mapping", mappingJson);
    form.append("file", importFile);
    const res = await fetch(`${API_BASE}/admin/import/upload`, {
      method: "POST",
      headers: { "X-Admin-Token": token },
      body: form,
    });
    const text = await res.text();
    if (!res.ok) {
      setImportResult(text);
      return;
    }
    setImportResult(text);
  };

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-badge">EL</div>
          <div>
            <div>Admin React</div>
            <small>内容管理</small>
          </div>
        </div>
        <button className={`nav-btn ${view === "content" ? "active" : ""}`} onClick={() => setView("content")}>
          内容列表
        </button>
        <button className={`nav-btn ${view === "import" ? "active" : ""}`} onClick={() => setView("import")}>
          批量导入
        </button>
        <button className={`nav-btn ${view === "jobs" ? "active" : ""}`} onClick={() => setView("jobs")}>
          导入任务
        </button>
        <button className={`nav-btn ${view === "audit" ? "active" : ""}`} onClick={() => setView("audit")}>
          审计日志
        </button>
      </aside>

      <main className="main">
        <div className="topbar">
          <h2>{view === "content" ? "内容列表" : view === "import" ? "批量导入" : "导入任务"}</h2>
          <div>
            <input
              className="token-input"
              placeholder="X-Admin-Token"
              value={token}
              onChange={(e) => setToken(e.target.value)}
            />
            <button className="primary">保存</button>
          </div>
        </div>

        {view === "content" && (
          <div className="panel">
            <div className="toolbar">
              <select value={contentType} onChange={(e) => setContentType(e.target.value)}>
                <option value="words">单词</option>
                <option value="sentences">句子</option>
                <option value="passages">文章</option>
                <option value="exercises">练习</option>
              </select>
              <input
                placeholder="keyword"
                value={contentKeyword}
                onChange={(e) => setContentKeyword(e.target.value)}
              />
              <input placeholder="level" value={contentLevel} onChange={(e) => setContentLevel(e.target.value)} />
              <input placeholder="tags" value={contentTags} onChange={(e) => setContentTags(e.target.value)} />
              <button className="primary" onClick={() => loadContent()}>
                搜索
              </button>
            </div>
            <div className="muted">总数：{contentTotal}</div>
            <div className="toolbar">
              <button className="ghost" onClick={toggleSelectAll}>
                {contentSelected.length === contentItems.length && contentItems.length > 0 ? "取消全选" : "全选当前页"}
              </button>
              <span className="muted">已选 {contentSelected.length} 条</span>
              <button className="primary" onClick={bulkDelete}>
                批量删除
              </button>
            </div>
            <div className="panel" style={{ marginTop: 12 }}>
              <div className="muted">批量运营工具</div>
              <div className="toolbar">
                <input
                  placeholder="tags(逗号)"
                  value={bulkTags}
                  onChange={(e) => setBulkTags(e.target.value)}
                />
                <select value={bulkTagMode} onChange={(e) => setBulkTagMode(e.target.value)}>
                  <option value="replace">replace</option>
                  <option value="add">add</option>
                  <option value="remove">remove</option>
                </select>
                <button className="primary" onClick={bulkAssignTags}>
                  批量设置标签
                </button>
              </div>
              <div className="toolbar">
                <input placeholder="level" value={bulkLevel} onChange={(e) => setBulkLevel(e.target.value)} />
                <button className="ghost" onClick={() => bulkUpdateField("level", bulkLevel)}>
                  批量设置等级
                </button>
              </div>
              <div className="toolbar">
                <input
                  placeholder="image_url"
                  value={bulkImageUrl}
                  onChange={(e) => setBulkImageUrl(e.target.value)}
                />
                <button className="ghost" onClick={() => bulkUpdateField("image_url", bulkImageUrl)}>
                  批量设置图片
                </button>
              </div>
              <div className="toolbar">
                <input
                  placeholder="audio_url"
                  value={bulkAudioUrl}
                  onChange={(e) => setBulkAudioUrl(e.target.value)}
                />
                <button className="ghost" onClick={() => bulkUpdateField("audio_url", bulkAudioUrl)}>
                  批量设置音频
                </button>
              </div>
            </div>
            <table className="table">
              <thead>
                <tr>
                  <th>
                    <input
                      type="checkbox"
                      checked={contentItems.length > 0 && contentSelected.length === contentItems.length}
                      onChange={toggleSelectAll}
                    />
                  </th>
                  <th>ID</th>
                  <th>内容</th>
                  <th>等级</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {contentItems.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <input
                        type="checkbox"
                        checked={contentSelected.includes(item.id)}
                        onChange={() => toggleSelect(item.id)}
                      />
                    </td>
                    <td>{item.id}</td>
                    <td>{item.text || item.title || item.prompt}</td>
                    <td>{item.level || "-"}</td>
                    <td>
                      <button className="ghost" onClick={() => startEdit(item, "text")}>
                        编辑
                      </button>
                      <button
                        className="ghost"
                        onClick={async () => {
                          const res = await fetch(`${API_BASE}/${contentType}/${item.id}`, {
                            method: "DELETE",
                            headers: { "X-Admin-Token": token },
                          });
                          if (!res.ok) {
                            alert(await res.text());
                            return;
                          }
                          loadContent();
                        }}
                      >
                        删除
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {editRow && (
              <div className="panel" style={{ marginTop: 12 }}>
                <div className="toolbar">
                  <span className="muted">编辑 ID {editRow.id}</span>
                  <select value={editField} onChange={(e) => setEditField(e.target.value)}>
                    <option value="text">text</option>
                    <option value="meaning">meaning</option>
                    <option value="title">title</option>
                    <option value="prompt">prompt</option>
                    <option value="level">level</option>
                    <option value="tags">tags(逗号)</option>
                    <option value="options">options(逗号)</option>
                    <option value="image_url">image_url</option>
                    <option value="audio_url">audio_url</option>
                  </select>
                  <input value={editValue} onChange={(e) => setEditValue(e.target.value)} />
                  <button className="primary" onClick={saveEdit}>
                    保存
                  </button>
                </div>
                <div className="media-panel">
                  <div className="media-row">
                    <div className="media-item">
                      <div className="muted">图片预览</div>
                      {editRow.image_url ? (
                        <img className="media-image" src={editRow.image_url} alt="image" />
                      ) : (
                        <div className="muted">未绑定图片</div>
                      )}
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => uploadMedia("image", e.target.files && e.target.files[0])}
                      />
                    </div>
                    <div className="media-item">
                      <div className="muted">音频预览</div>
                      {editRow.audio_url ? (
                        <audio controls src={editRow.audio_url} />
                      ) : (
                        <div className="muted">未绑定音频</div>
                      )}
                      <input
                        type="file"
                        accept="audio/*"
                        onChange={(e) => uploadMedia("audio", e.target.files && e.target.files[0])}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div className="toolbar">
              <button
                className="ghost"
                onClick={() => setContentSkip(Math.max(0, contentSkip - contentLimit))}
              >
                上一页
              </button>
              <button className="ghost" onClick={() => setContentSkip(contentSkip + contentLimit)}>
                下一页
              </button>
              <button className="primary" onClick={loadContent}>
                刷新
              </button>
            </div>
          </div>
        )}

        {view === "import" && (
          <div className="panel">
            <div className="toolbar">
              <select value={importEntity} onChange={(e) => setImportEntity(e.target.value)}>
                <option value="word">单词</option>
                <option value="sentence">句子</option>
                <option value="passage">文章</option>
                <option value="exercise">练习</option>
              </select>
              <select value={importMode} onChange={(e) => setImportMode(e.target.value)}>
                <option value="upsert">upsert</option>
                <option value="insert_only">insert_only</option>
                <option value="update_only">update_only</option>
              </select>
            </div>
            <textarea value={importJson} onChange={(e) => setImportJson(e.target.value)} />
            <div className="toolbar">
              <button className="primary" onClick={validateImport}>
                校验
              </button>
              <button className="primary" onClick={executeImport}>
                导入
              </button>
            </div>
            <div className="toolbar">
              <input
                type="file"
                onChange={(e) => setImportFile(e.target.files ? e.target.files[0] : null)}
              />
              <input
                placeholder='mapping JSON: {"text":"单词"}'
                value={mappingJson}
                onChange={(e) => setMappingJson(e.target.value)}
              />
              <button className="primary" onClick={uploadImport}>
                上传导入
              </button>
            </div>
            <pre>{importResult}</pre>
          </div>
        )}

        {view === "jobs" && (
          <div className="panel">
            <button className="primary" onClick={loadJobs}>
              刷新
            </button>
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>状态</th>
                  <th>类型</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((job) => (
                  <tr key={job.id}>
                    <td>{job.id}</td>
                    <td>{job.status}</td>
                    <td>{job.entity_type}</td>
                    <td>
                      <button className="ghost" onClick={() => loadJobDetail(job.id)}>
                        查看
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {jobDetails && (
              <div className="panel" style={{ marginTop: 12 }}>
                <div className="muted">任务详情 #{jobDetails.id}</div>
                <pre>{JSON.stringify(jobDetails, null, 2)}</pre>
                {jobErrors && (
                  <pre>{JSON.stringify(jobErrors, null, 2)}</pre>
                )}
                <div className="toolbar">
                  <button
                    className="ghost"
                    onClick={async () => {
                      const res = await fetch(`${API_BASE}/admin/import/jobs/${jobDetails.id}/retry`, {
                        method: "POST",
                        headers: { "X-Admin-Token": token },
                      });
                      if (!res.ok) {
                        alert(await res.text());
                        return;
                      }
                      alert("已触发重试");
                    }}
                  >
                    重试
                  </button>
                  <button
                    className="ghost"
                    onClick={async () => {
                      const res = await fetch(`${API_BASE}/admin/import/jobs/${jobDetails.id}/cancel`, {
                        method: "POST",
                        headers: { "X-Admin-Token": token },
                      });
                      if (!res.ok) {
                        alert(await res.text());
                        return;
                      }
                      alert("已取消任务");
                      loadJobDetail(jobDetails.id);
                      loadJobs();
                    }}
                  >
                    取消任务
                  </button>
                  <button
                    className="ghost"
                    onClick={() => {
                      const blob = new Blob([JSON.stringify(jobErrors || {}, null, 2)], {
                        type: "application/json",
                      });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `job-${jobDetails.id}-errors.json`;
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                  >
                    导出错误 JSON
                  </button>
                  <button
                    className="ghost"
                    onClick={() => {
                      const rows = (jobErrors && jobErrors.error_details) || [];
                      const csvRows = ["index,field,message"];
                      rows.forEach((row) => {
                        const message = (row.message || "").replace(/"/g, '""');
                        csvRows.push(`${row.index},${row.field},"${message}"`);
                      });
                      const blob = new Blob([csvRows.join("\n")], { type: "text/csv" });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `job-${jobDetails.id}-errors.csv`;
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                  >
                    导出错误 CSV
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {view === "audit" && (
          <div className="panel">
            <div className="toolbar">
              <input
                placeholder="action"
                value={auditAction}
                onChange={(e) => setAuditAction(e.target.value)}
              />
              <button className="primary" onClick={loadAudit}>
                加载
              </button>
            </div>
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>action</th>
                  <th>entity_type</th>
                  <th>entity_id</th>
                </tr>
              </thead>
              <tbody>
                {auditItems.map((item) => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.action}</td>
                    <td>{item.entity_type || "-"}</td>
                    <td>{item.entity_id || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
