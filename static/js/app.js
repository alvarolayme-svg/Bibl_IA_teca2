document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('[data-menu-toggle]');
  const sidebar = document.querySelector('#sidebar');

  if (toggle && sidebar) {
    toggle.addEventListener('click', () => {
      sidebar.classList.toggle('is-open');
    });
  }

  window.setTimeout(() => {
    document.querySelectorAll('.message').forEach((message) => {
      message.classList.add('message-hide');
    });
  }, 5000);
});
