(function () {
  const modal = document.getElementById("qr-modal");
  const modalImage = modal?.querySelector("img");
  const modalUrl = modal?.querySelector(".qr-url");
  const closeButton = modal?.querySelector(".qr-close");

  function absoluteUrl(hash) {
    const url = new URL(window.location.href);
    url.hash = hash.replace(/^#?/, "");
    return url.toString();
  }

  function noteShare(slug) {
    if (window.NovaMetrics && slug) {
      window.NovaMetrics.incrementShare(slug);
    }
  }

  async function copyLink(url, output) {
    try {
      await navigator.clipboard.writeText(url);
      output.textContent = "Link copied";
    } catch {
      output.textContent = "Link ready";
    }
  }

  function openEmail(title, url) {
    const subject = encodeURIComponent(title);
    const body = encodeURIComponent(`${title}\n\n${url}`);
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
  }

  function openQr(title, url) {
    if (!modal || !modalImage || !modalUrl) return;

    modalImage.src = `https://api.qrserver.com/v1/create-qr-code/?size=240x240&margin=12&data=${encodeURIComponent(url)}`;
    modalImage.alt = `QR code for ${title}`;
    modalUrl.textContent = url;
    modal.hidden = false;
  }

  document.querySelectorAll(".share-panel").forEach((panel) => {
    const output = panel.querySelector("output");
    const slug = document.querySelector("[data-article-slug]")?.dataset.articleSlug;

    panel.addEventListener("click", (event) => {
      const button = event.target.closest("[data-share-action]");
      if (!button) return;

      const url = absoluteUrl(panel.dataset.shareUrl || "");
      const title = panel.dataset.shareTitle || document.title;
      const action = button.dataset.shareAction;

      noteShare(slug);

      if (action === "copy") {
        copyLink(url, output);
      }

      if (action === "email") {
        output.textContent = "Opening email";
        openEmail(title, url);
      }

      if (action === "qr") {
        output.textContent = "QR opened";
        openQr(title, url);
      }
    });
  });

  closeButton?.addEventListener("click", () => {
    modal.hidden = true;
  });

  modal?.addEventListener("click", (event) => {
    if (event.target === modal) {
      modal.hidden = true;
    }
  });
})();
