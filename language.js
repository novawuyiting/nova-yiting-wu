(function () {
  const storageKey = "nova-yiting-wu.language.v1";
  const choices = document.querySelectorAll("[data-language-choice]");
  const localizedNodes = document.querySelectorAll("[data-lang]");

  if (!choices.length || !localizedNodes.length) return;

  function setLanguage(language) {
    document.documentElement.lang = language === "zh" ? "zh-Hans" : "en";
    localStorage.setItem(storageKey, language);

    localizedNodes.forEach((node) => {
      node.hidden = node.dataset.lang !== language;
    });

    choices.forEach((button) => {
      const isActive = button.dataset.languageChoice === language;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });
  }

  choices.forEach((button) => {
    button.addEventListener("click", () => setLanguage(button.dataset.languageChoice));
  });

  setLanguage(localStorage.getItem(storageKey) || "zh");
})();
