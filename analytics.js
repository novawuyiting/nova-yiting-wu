(function () {
  const defaults = {
    "2026-05-10-me-and-my-rocky": {
      pageViews: 0,
      shares: 0,
      agentUse: 0,
    },
  };

  const storageKey = "nova-yiting-wu.metrics.v1";
  const sessionKey = "nova-yiting-wu.page-viewed.v1";

  function readStore() {
    try {
      return JSON.parse(localStorage.getItem(storageKey)) || {};
    } catch {
      return {};
    }
  }

  function writeStore(store) {
    localStorage.setItem(storageKey, JSON.stringify(store));
  }

  function getMetrics(slug) {
    const store = readStore();
    return { ...(defaults[slug] || {}), ...(store[slug] || {}) };
  }

  function setMetric(slug, metric, value) {
    const store = readStore();
    store[slug] = { ...(store[slug] || {}), [metric]: value };
    writeStore(store);
    renderMetrics(slug);
  }

  function increment(slug, metric) {
    const current = getMetrics(slug)[metric] || 0;
    setMetric(slug, metric, current + 1);
  }

  function renderMetrics(slug) {
    const metrics = getMetrics(slug);
    document.querySelectorAll(`[data-slug="${slug}"] [data-metric]`).forEach((node) => {
      const metric = node.dataset.metric;
      node.textContent = (metrics[metric] || 0).toLocaleString("en");
    });
  }

  function currentSlug() {
    return document.querySelector("[data-article-slug]")?.dataset.articleSlug;
  }

  function trackPageView() {
    const slug = currentSlug();
    if (!slug) return;

    const viewed = JSON.parse(sessionStorage.getItem(sessionKey) || "{}");
    if (viewed[slug]) {
      renderMetrics(slug);
      return;
    }

    viewed[slug] = true;
    sessionStorage.setItem(sessionKey, JSON.stringify(viewed));
    increment(slug, "pageViews");
  }

  async function shareArticle(button) {
    const slug = currentSlug();
    const shareData = {
      title: button.dataset.shareTitle || document.title,
      text: "Nova Yiting Wu · Exchange Ideas & Beyond",
      url: window.location.href,
    };

    if (slug) increment(slug, "shares");

    if (navigator.share) {
      await navigator.share(shareData);
      return;
    }

    try {
      await navigator.clipboard.writeText(window.location.href);
      button.textContent = "Link copied";
    } catch {
      button.textContent = "Link ready";
    }
  }

  document.querySelectorAll("[data-slug]").forEach((node) => renderMetrics(node.dataset.slug));
  trackPageView();

  document.querySelectorAll(".share-button").forEach((button) => {
    button.addEventListener("click", () => {
      shareArticle(button).catch(() => {
        button.textContent = "Share noted";
      });
    });
  });

  window.NovaMetrics = {
    getMetrics,
    incrementAgentUse(slug) {
      increment(slug, "agentUse");
    },
  };
})();
