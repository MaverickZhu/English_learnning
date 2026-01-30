const views = document.querySelectorAll(".view");
const navItems = document.querySelectorAll(".nav-item");
const viewLinks = document.querySelectorAll("[data-view-link]");
const pageTitle = document.getElementById("page-title");
const pageDesc = document.getElementById("page-desc");

const API_BASE = "http://localhost:28000";
const tokenKey = "web_token";
const userIdKey = "web_user_id";
const adminTokenKey = "web_admin_token";

const viewMeta = {
  home: {
    title: "首页",
    desc: "沉浸式英语学习：语音 + 配图 + 练习 + 测试",
  },
  learn: {
    title: "学习",
    desc: "词义/句意/文章理解，配合语音与图片",
  },
  practice: {
    title: "练习",
    desc: "多题型训练与即时反馈",
  },
  exam: {
    title: "考试",
    desc: "考级模拟与成绩分析",
  },
  report: {
    title: "报告",
    desc: "学习趋势、弱项与建议",
  },
  profile: {
    title: "我的",
    desc: "目标与偏好设置",
  },
};

function setView(name) {
  views.forEach((view) => {
    view.classList.toggle("is-visible", view.dataset.view === name);
  });
  navItems.forEach((item) => {
    item.classList.toggle("is-active", item.dataset.view === name);
  });
  pageTitle.textContent = viewMeta[name].title;
  pageDesc.textContent = viewMeta[name].desc;
}

function getToken() {
  return localStorage.getItem(tokenKey);
}

function getUserId() {
  return localStorage.getItem(userIdKey);
}

function parseJwtPayload(token) {
  try {
    const payload = token.split(".")[1];
    if (!payload) return null;
    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), "=");
    return JSON.parse(atob(padded));
  } catch (err) {
    console.warn("parse token failed", err);
    return null;
  }
}

async function api(path, options = {}) {
  const headers = options.headers || {};
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "请求失败");
  }
  return response.json();
}

navItems.forEach((item) => {
  item.addEventListener("click", () => setView(item.dataset.view));
});

viewLinks.forEach((item) => {
  item.addEventListener("click", () => setView(item.dataset.viewLink));
});

document.getElementById("quick-start").addEventListener("click", () => setView("learn"));

const wordAudio = document.getElementById("word-audio");
const wordImage = document.getElementById("word-image");
const wordTitle = document.getElementById("word-title");
const wordMeaning = document.getElementById("word-meaning");
const wordExample = document.getElementById("word-example");
const lessonMeta = document.getElementById("lesson-meta");
const prevLessonBtn = document.getElementById("prev-lesson");
const nextLessonBtn = document.getElementById("next-lesson");
const adminTokenInput = document.getElementById("admin-token");
const saveAdminTokenBtn = document.getElementById("save-admin-token");
const uploadImageInput = document.getElementById("upload-image");
const uploadAudioInput = document.getElementById("upload-audio");
const mediaStatus = document.getElementById("media-status");
const newsTitle = document.getElementById("news-title");
const newsSummary = document.getElementById("news-summary");
const newsPassage = document.getElementById("news-passage");
const newsSource = document.getElementById("news-source");
const newsLink = document.getElementById("news-link");
const newsWords = document.getElementById("news-words");
const newsSentences = document.getElementById("news-sentences");
const newsExercises = document.getElementById("news-exercises");
const newsStatus = document.getElementById("news-status");
let currentWordId = null;
let lessonItems = [];
let lessonIndex = 0;

const mockWord = {
  text: "gratitude",
  meaning: "感激；感谢",
  example: "She expressed gratitude for the support.",
  audio_url: "https://upload.wikimedia.org/wikipedia/commons/transcoded/3/3f/En-us-gratitude.ogg/En-us-gratitude.ogg.mp3",
  image_url:
    "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=80",
};

async function loadLesson() {
  try {
    const level = document.getElementById("learn-level").value;
    const data = await api(`/words?limit=10&level=${level}`);
    const items = data.items || data || [];
    if (items.length > 0) {
      lessonItems = items;
      lessonIndex = 0;
      renderLesson();
      return;
    }
  } catch (err) {
    console.warn(err);
  }
  wordTitle.textContent = mockWord.text;
  wordMeaning.textContent = mockWord.meaning;
  wordExample.textContent = mockWord.example;
  wordAudio.src = mockWord.audio_url;
  wordImage.style.backgroundImage = `url('${mockWord.image_url}')`;
  currentWordId = null;
  lessonMeta.textContent = "0 / 0";
}

document.getElementById("load-lesson").addEventListener("click", loadLesson);
loadLesson();

function renderLesson() {
  const item = lessonItems[lessonIndex];
  if (!item) return;
  wordTitle.textContent = item.text;
  wordMeaning.textContent = item.meaning;
  wordExample.textContent = item.example || "";
  wordAudio.src = item.audio_url || mockWord.audio_url;
  wordImage.style.backgroundImage = `url('${item.image_url || mockWord.image_url}')`;
  currentWordId = item.id;
  lessonMeta.textContent = `${lessonIndex + 1} / ${lessonItems.length}`;
}

function getSourceLabel(url) {
  try {
    const { hostname } = new URL(url);
    return hostname.replace("www.", "");
  } catch (err) {
    return "news";
  }
}

function renderNewsLearning(payload) {
  if (!payload) return;
  const { article, passage, words, sentences, exercises } = payload;
  newsTitle.textContent = article.title || "未获取标题";
  newsSummary.textContent = article.summary || "";
  newsPassage.textContent = passage.content || "";
  newsSource.textContent = getSourceLabel(article.url || "");
  newsLink.href = article.url || "#";
  newsLink.textContent = article.url ? "查看原文" : "暂无链接";
  newsWords.innerHTML = (words || [])
    .map((item) => `<li><strong>${item.text}</strong> · ${item.meaning}</li>`)
    .join("");
  newsSentences.innerHTML = (sentences || [])
    .map((item) => `<li>${item.text}<br /><small>${item.meaning}</small></li>`)
    .join("");
  newsExercises.innerHTML = (exercises || [])
    .map((item) => {
      const answer = item.answer ? `<div>答案：${item.answer}</div>` : "";
      return `<div class="news-exercise"><div>${item.prompt}</div>${answer}</div>`;
    })
    .join("");
  newsStatus.textContent = `已加载：${words.length} 词 · ${sentences.length} 句 · ${exercises.length} 练习`;
}

async function loadNewsLearning() {
  newsStatus.textContent = "加载新闻内容中...";
  try {
    const data = await api("/news/latest");
    renderNewsLearning(data);
  } catch (err) {
    newsStatus.textContent = `加载失败：${err.message}`;
  }
}

prevLessonBtn.addEventListener("click", () => {
  if (lessonItems.length === 0) return;
  lessonIndex = Math.max(0, lessonIndex - 1);
  renderLesson();
});

nextLessonBtn.addEventListener("click", () => {
  if (lessonItems.length === 0) return;
  lessonIndex = Math.min(lessonItems.length - 1, lessonIndex + 1);
  renderLesson();
});

document.getElementById("reload-news").addEventListener("click", loadNewsLearning);
loadNewsLearning();

const storedAdminToken = localStorage.getItem(adminTokenKey);
if (storedAdminToken) {
  adminTokenInput.value = storedAdminToken;
}

saveAdminTokenBtn.addEventListener("click", () => {
  const value = adminTokenInput.value.trim();
  if (!value) {
    mediaStatus.textContent = "请输入管理员 Token";
    return;
  }
  localStorage.setItem(adminTokenKey, value);
  mediaStatus.textContent = "已保存管理员 Token";
});

async function uploadMedia(kind, file) {
  if (!file) return;
  if (!currentWordId) {
    mediaStatus.textContent = "未加载到单词，无法写回";
    return;
  }
  const adminToken = localStorage.getItem(adminTokenKey) || adminTokenInput.value.trim();
  if (!adminToken) {
    mediaStatus.textContent = "请先填写管理员 Token";
    return;
  }
  const form = new FormData();
  form.append("kind", kind);
  form.append("file", file);
  mediaStatus.textContent = "上传中...";
  const res = await fetch(`${API_BASE}/admin/media/upload`, {
    method: "POST",
    headers: { "X-Admin-Token": adminToken },
    body: form,
  });
  if (!res.ok) {
    mediaStatus.textContent = `上传失败：${await res.text()}`;
    return;
  }
  const data = await res.json();
  const field = kind === "image" ? "image_url" : "audio_url";
  await api(`/words/${currentWordId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ [field]: data.url }),
  });
  if (kind === "image") {
    wordImage.style.backgroundImage = `url('${data.url}')`;
  } else {
    wordAudio.src = data.url;
  }
  mediaStatus.textContent = "上传并绑定成功";
}

uploadImageInput.addEventListener("change", (e) => {
  uploadMedia("image", e.target.files?.[0]);
});

uploadAudioInput.addEventListener("change", (e) => {
  uploadMedia("audio", e.target.files?.[0]);
});

const practicePrompt = document.getElementById("practice-prompt");
const practiceOptions = document.getElementById("practice-options");
const practiceResult = document.getElementById("practice-result");
let currentAnswer = null;
let selectedOption = null;
let currentExerciseId = null;

const mockPractice = {
  prompt: "Choose the image that matches: gratitude",
  options: ["Option A", "Option B", "Option C", "Option D"],
  answer: "Option A",
};

function renderPractice(options) {
  practicePrompt.textContent = options.prompt;
  practiceOptions.innerHTML = "";
  options.options.forEach((option) => {
    const button = document.createElement("button");
    button.className = "practice-option";
    button.textContent = option;
    button.addEventListener("click", () => {
      selectedOption = option;
      document.querySelectorAll(".practice-option").forEach((btn) => btn.classList.remove("is-selected"));
      button.classList.add("is-selected");
    });
    practiceOptions.appendChild(button);
  });
  practiceResult.textContent = "";
  currentAnswer = options.answer;
  currentExerciseId = options.exercise_id || null;
}

document.getElementById("generate-practice").addEventListener("click", async () => {
  try {
    const level = document.getElementById("learn-level").value;
    const exerciseType = document.getElementById("practice-type").value;
    const data = await api("/practice/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ limit: 1, level, exercise_type: exerciseType }),
    });
    const item = data.items && data.items[0];
    if (item) {
      renderPractice({
        exercise_id: item.id,
        prompt: item.prompt,
        options: item.options || ["选项 A", "选项 B", "选项 C", "选项 D"],
        answer: item.answer,
      });
      return;
    }
  } catch (err) {
    console.warn(err);
  }
  renderPractice(mockPractice);
});
renderPractice(mockPractice);

document.getElementById("practice-check").addEventListener("click", async () => {
  if (!selectedOption) {
    practiceResult.textContent = "请选择一个答案";
    return;
  }
  if (currentExerciseId) {
    try {
      const data = await api("/practice/score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ exercise_id: currentExerciseId, answer: selectedOption }),
      });
      practiceResult.textContent = data.correct
        ? `正确 ✅ 解析：${data.explanation || "无"}`
        : `错误 ❌ 正确答案：${data.expected}`;
      return;
    } catch (err) {
      console.warn(err);
    }
  }
  practiceResult.textContent = selectedOption === currentAnswer ? "正确 ✅" : "再试一次 ❌";
});

const examCard = document.getElementById("exam-card");
const examQuestions = document.getElementById("exam-questions");
const examResult = document.getElementById("exam-result");
let currentExam = null;
let examExercises = [];
let examAnswers = {};

function renderExamQuestions(items) {
  examQuestions.innerHTML = "";
  items.forEach((item, index) => {
    const wrapper = document.createElement("div");
    wrapper.className = "exam-question";
    wrapper.innerHTML = `
      <div class="exam-q-title">Q${index + 1} · ${item.exercise_type}</div>
      <div class="exam-q-prompt">${item.prompt}</div>
    `;
    const options = document.createElement("div");
    options.className = "exam-options";
    (item.options || ["选项 A", "选项 B", "选项 C", "选项 D"]).forEach((option) => {
      const button = document.createElement("button");
      button.className = "practice-option";
      button.textContent = option;
      button.addEventListener("click", () => {
        options.querySelectorAll("button").forEach((btn) => btn.classList.remove("is-selected"));
        button.classList.add("is-selected");
        examAnswers[item.id] = option;
      });
      options.appendChild(button);
    });
    wrapper.appendChild(options);
    examQuestions.appendChild(wrapper);
  });
}

document.getElementById("generate-exam").addEventListener("click", () => {
  const title = document.getElementById("exam-title").value || "模拟考试";
  const userId = getUserId();
  if (!getToken() || !userId) {
    examCard.innerHTML = `<div class="exam-info">请先登录并填写用户ID</div>`;
    return;
  }
  const level = document.getElementById("learn-level").value;
  api("/exam/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: Number(userId), title, limit: 8, level }),
  })
    .then((data) => {
      currentExam = data;
      examAnswers = {};
      examExercises = [];
      examCard.innerHTML = `
        <div class="exam-info">
          <strong>${data.title}</strong>
          <p>题量：${data.exercise_ids.length} · 时长：${data.duration_minutes} 分钟</p>
          <button class="primary" id="start-exam">开始考试</button>
        </div>
      `;
      const startBtn = document.getElementById("start-exam");
      if (startBtn) {
        startBtn.addEventListener("click", async () => {
          const tasks = data.exercise_ids.map((id) => api(`/exercises/${id}`));
          const items = await Promise.all(tasks);
          examExercises = items;
          renderExamQuestions(items);
          examResult.textContent = "";
        });
      }
    })
    .catch((err) => {
      examCard.innerHTML = `<div class="exam-info">生成失败：${err.message}</div>`;
    });
});

document.getElementById("submit-exam").addEventListener("click", async () => {
  if (!currentExam) {
    examResult.textContent = "请先生成考试";
    return;
  }
  try {
    const data = await api("/exam/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ exam_id: currentExam.id, answers: examAnswers }),
    });
    examResult.textContent = `得分：${data.score} 分（${data.correct}/${data.total}）`;
  } catch (err) {
    examResult.textContent = `提交失败：${err.message}`;
  }
});

const reportSummary = document.getElementById("report-summary");
const reportSuggestions = document.getElementById("report-suggestions");

function renderReport() {
  const userId = getUserId();
  if (!getToken() || !userId) {
    reportSummary.innerHTML = `<p>请先登录</p>`;
    reportSuggestions.innerHTML = "";
    return;
  }
  api("/reports/summary", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: Number(userId), days: 30 }),
  })
    .then((data) => {
      reportSummary.innerHTML = `
        <p>学习记录：${data.study_total}</p>
        <p>正确率：${Math.round(data.study_accuracy * 100)}%</p>
        <p>考试次数：${data.exam_total}</p>
        <p>考试均分：${data.exam_avg_score}</p>
      `;
      reportSuggestions.innerHTML = data.suggestions.map((s) => `<li>${s}</li>`).join("");
    })
    .catch((err) => {
      reportSummary.innerHTML = `<p>加载失败：${err.message}</p>`;
      reportSuggestions.innerHTML = "";
    });
}

document.getElementById("refresh-report").addEventListener("click", renderReport);
renderReport();

const userIdInput = document.getElementById("user-id");
const userEmailInput = document.getElementById("user-email");
const userPasswordInput = document.getElementById("user-password");
const profileStatus = document.getElementById("profile-status");
const registerBtn = document.getElementById("register-btn");

const storedUserId = getUserId();
if (storedUserId) {
  userIdInput.value = storedUserId;
}
const storedToken = getToken();
if (storedToken && !storedUserId) {
  const payload = parseJwtPayload(storedToken);
  if (payload?.sub) {
    localStorage.setItem(userIdKey, String(payload.sub));
    userIdInput.value = String(payload.sub);
  }
}

document.getElementById("login-btn").addEventListener("click", async () => {
  const email = userEmailInput.value.trim();
  const password = userPasswordInput.value.trim();
  if (!email || !password) {
    profileStatus.textContent = "请输入邮箱与密码";
    return;
  }
  try {
    const data = await api("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    localStorage.setItem(tokenKey, data.access_token);
    const payload = parseJwtPayload(data.access_token);
    if (payload?.sub) {
      localStorage.setItem(userIdKey, String(payload.sub));
      userIdInput.value = String(payload.sub);
    }
    profileStatus.textContent = "登录成功";
  } catch (err) {
    profileStatus.textContent = `登录失败：${err.message}`;
  }
});

registerBtn.addEventListener("click", async () => {
  const email = userEmailInput.value.trim();
  const password = userPasswordInput.value.trim();
  if (!email || !password) {
    profileStatus.textContent = "请输入邮箱与密码";
    return;
  }
  try {
    const data = await api("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (data?.id) {
      localStorage.setItem(userIdKey, String(data.id));
      userIdInput.value = String(data.id);
    }
    profileStatus.textContent = "注册成功，请登录";
  } catch (err) {
    profileStatus.textContent = `注册失败：${err.message}`;
  }
});

document.getElementById("save-profile").addEventListener("click", () => {
  const userId = userIdInput.value.trim();
  if (userId) {
    localStorage.setItem(userIdKey, userId);
    profileStatus.textContent = "已保存用户ID";
  } else {
    profileStatus.textContent = "请输入用户ID";
  }
});
