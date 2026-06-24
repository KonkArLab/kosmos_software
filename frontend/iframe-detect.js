(function () {
  if (window.self !== window.top) {
    document.documentElement.style.cssText += ';background:transparent!important';
    // Inject style immediately (before DOMContentLoaded) so the header never flashes
    var s = document.createElement('style');
    s.textContent = 'header{display:none!important}section{margin-top:0.5rem!important}';
    document.head.appendChild(s);
    document.addEventListener('DOMContentLoaded', function () {
      document.body.classList.add('in-iframe');
    });
  }
})();
