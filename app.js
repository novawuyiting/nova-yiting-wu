const postData = JSON.parse(document.getElementById("posts-data").textContent);
const postList = document.querySelector("#post-list");
const topicButtons = document.querySelectorAll(".topic");
const languageStorageKey = "nova-yiting-wu.language.v1";
let activeTopic = "all";

function currentLanguage() {
  try {
    return localStorage.getItem(languageStorageKey) || (document.documentElement.lang.startsWith("en") ? "en" : "zh");
  } catch {
    return document.documentElement.lang.startsWith("en") ? "en" : "zh";
  }
}

function formatDate(value) {
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

function metricLabel(label, value) {
  const metricName = {
    "Page View": "pageViews",
    Share: "shares",
    "Agent Use": "agentUse",
  }[label];

  return `<span>${label} <strong data-metric="${metricName}">${value.toLocaleString("en")}</strong></span>`;
}

function renderPosts(topic = "all") {
  activeTopic = topic;
  const language = currentLanguage();
  const isEnglish = language === "en";
  const posts = topic === "all" ? postData : postData.filter((post) => post.topics.includes(topic));

  postList.innerHTML = posts
    .map(
      (post) => `
        <article class="post-row" data-slug="${post.slug || post.url.replace(/^.*\//, "").replace(/\.html$/, "")}">
          <div>
            <div class="post-meta">${formatDate(post.date)} · ${post.topics.join(" / ")}</div>
            <h3><a href="${post.url}">${isEnglish ? post.titleEn : post.title}</a></h3>
            <p>${isEnglish ? post.summaryEn : post.summary}</p>
            <div class="metric-row" aria-label="Article metrics" data-slug="${post.slug || post.url.replace(/^.*\//, "").replace(/\.html$/, "")}">
              ${metricLabel("Page View", post.metrics.pageViews)}
              ${metricLabel("Share", post.metrics.shares)}
              ${metricLabel("Agent Use", post.metrics.agentUse)}
            </div>
            <div class="post-topics" aria-label="Topics">
              ${post.topics.map((item) => `<span>${item}</span>`).join("")}
            </div>
          </div>
          <a class="arrow-link" href="${post.url}">
            ${isEnglish ? "Open" : "打开"}
            <span aria-hidden="true">→</span>
          </a>
        </article>
      `,
    )
    .join("");

  postList.querySelectorAll("[data-slug]").forEach((node) => {
    window.NovaMetrics?.getMetrics(node.dataset.slug);
    node.querySelectorAll("[data-metric]").forEach((metricNode) => {
      const metrics = window.NovaMetrics?.getMetrics(node.dataset.slug);
      if (!metrics) return;
      metricNode.textContent = (metrics[metricNode.dataset.metric] || 0).toLocaleString("en");
    });
  });
}

topicButtons.forEach((button) => {
  button.addEventListener("click", () => {
    topicButtons.forEach((item) => item.classList.remove("is-active"));
    button.classList.add("is-active");
    renderPosts(button.dataset.topic);
  });
});

window.addEventListener("nova-language-change", () => renderPosts(activeTopic));

renderPosts();
