(function () {
  const storageKey = "nova-yiting-wu.language.v1";
  const choices = document.querySelectorAll("[data-language-choice]");
  const localizedNodes = document.querySelectorAll("[data-lang]");

  if (!choices.length || !localizedNodes.length) return;

  function readLanguage() {
    try {
      return localStorage.getItem(storageKey);
    } catch {
      return null;
    }
  }

  function saveLanguage(language) {
    try {
      localStorage.setItem(storageKey, language);
    } catch {
      // Direct file previews can block storage; the visible switch should still work.
    }
  }

  function setLanguage(language) {
    document.documentElement.lang = language === "zh" ? "zh-Hans" : "en";
    saveLanguage(language);

    localizedNodes.forEach((node) => {
      node.hidden = node.dataset.lang !== language;
    });

    choices.forEach((button) => {
      const isActive = button.dataset.languageChoice === language;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });

    window.dispatchEvent(new CustomEvent("nova-language-change", { detail: { language } }));
  }

  choices.forEach((button) => {
    button.addEventListener("click", () => setLanguage(button.dataset.languageChoice));
  });

  setLanguage(readLanguage() || "zh");
})();
