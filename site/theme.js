(function () {
  'use strict';
  var key = 'moratorium-theme';
  var system = window.matchMedia('(prefers-color-scheme: dark)');
  var choice = null;
  try {
    choice = localStorage.getItem(key);
  } catch (_) {}
  if (choice !== 'light' && choice !== 'dark') choice = null;

  function apply() {
    var theme = choice || (system.matches ? 'dark' : 'light');
    document.documentElement.dataset.theme = theme;
    var button = document.getElementById('theme-toggle');
    if (button) {
      button.hidden = false;
      button.setAttribute('aria-pressed', String(theme === 'dark'));
    }
    window.dispatchEvent(new Event('themechange'));
  }

  apply();
  document.addEventListener('DOMContentLoaded', function () {
    var button = document.getElementById('theme-toggle');
    if (!button) return;
    apply();
    button.addEventListener('click', function () {
      choice = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      try {
        localStorage.setItem(key, choice);
      } catch (_) {}
      apply();
    });
  });
  system.addEventListener('change', function () {
    if (!choice) apply();
  });
  window.addEventListener('storage', function (event) {
    if (event.key !== key && event.key !== null) return;
    choice = event.newValue === 'light' || event.newValue === 'dark' ? event.newValue : null;
    apply();
  });
})();
