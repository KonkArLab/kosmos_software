(function () {
  if (window.self !== window.top) {
    // Fond transparent immédiatement pour éviter le flash blanc
    document.documentElement.style.cssText += ';background:transparent!important';
    document.addEventListener('DOMContentLoaded', function () {
      document.body.classList.add('in-iframe');
    });
  }
})();
