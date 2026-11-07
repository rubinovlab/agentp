// Copy buttons for code blocks. They share one accessible status region (#copy-status)
// and keep their size when the label changes.
document.querySelectorAll('.code').forEach(function (block) {
  var button = document.createElement('button');
  button.type = 'button';
  button.className = 'copy';
  button.textContent = 'Copy';
  var label = block.querySelector('.code-header span').textContent;
  button.setAttribute('aria-label', 'Copy ' + label.toLowerCase() + ' code');
  button.addEventListener('click', async function () {
    var status = document.getElementById('copy-status');
    button.disabled = true;
    try {
      await navigator.clipboard.writeText(block.querySelector('pre').textContent);
      button.textContent = 'Copied';
      status.textContent = 'Code copied.';
    } catch (error) {
      button.textContent = 'Retry';
      status.textContent = 'Could not copy. Select the code and copy it manually, or try again.';
      block.querySelector('pre').focus();
    } finally {
      button.disabled = false;
      setTimeout(function () { button.textContent = 'Copy'; }, 2000);
    }
  });
  block.querySelector('.code-header').appendChild(button);
});

// Sidebar: mark the section of the current page that is at the top of the window.
(function () {
  var links = document.querySelectorAll('.sidebar .sub a');
  var sections = document.querySelectorAll('main section');
  if (!links.length || !('IntersectionObserver' in window)) return;
  var byId = {};
  links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
  var visible = {};
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { visible[e.target.id] = e.isIntersecting; });
    var current = null;
    sections.forEach(function (s) { if (!current && visible[s.id]) current = s; });
    links.forEach(function (a) { a.classList.remove('active'); });
    if (current && byId[current.id]) byId[current.id].classList.add('active');
  }, { rootMargin: '0px 0px -65% 0px' });
  sections.forEach(function (s) { observer.observe(s); });
})();
