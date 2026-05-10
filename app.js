const postData = JSON.parse(document.getElementById("posts-data").textContent);
const postList = document.querySelector("#post-list");
const topicButtons = document.querySelectorAll(".topic");

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
  const posts = topic === "all" ? postData : postData.filter((post) => post.topics.includes(topic));

  postList.innerHTML = posts
    .map(
      (post) => `
        <article class="post-row" data-slug="${post.slug || post.url.replace(/^.*\//, "").replace(/\.html$/, "")}">
          <div>
            <div class="post-meta">${formatDate(post.date)} · ${post.topics.join(" / ")}</div>
            <h3><a href="${post.url}">${post.title}</a></h3>
            <p>${post.summary}</p>
            <p class="translation-line">${post.titleEn} · ${post.summaryEn}</p>
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
            Open
            <span aria-hidden="true">→</span>
          </a>
        </article>
      `,
    )
    .join("");
}

topicButtons.forEach((button) => {
  button.addEventListener("click", () => {
    topicButtons.forEach((item) => item.classList.remove("is-active"));
    button.classList.add("is-active");
    renderPosts(button.dataset.topic);
  });
});

renderPosts();
