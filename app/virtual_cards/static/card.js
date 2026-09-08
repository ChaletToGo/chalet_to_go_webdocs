const shareButton = document.querySelector('.share');
const status = document.querySelector('.status');
shareButton.hidden = false;
shareButton.addEventListener('click', async () => {
  const url = new URL(window.location.href);
  url.search = '';
  url.hash = '';
  status.textContent = '';
  if (navigator.share) {
    try {
      await navigator.share({title: document.title, url: url.href});
      return;
    } catch (error) {
      if (error.name === 'AbortError') return;
    }
  }
  try {
    await navigator.clipboard.writeText(url.href);
    status.textContent = document.body.dataset.copied;
  } catch {
    const fallback = document.querySelector('.copy-fallback');
    const input = fallback.querySelector('input');
    fallback.hidden = false;
    input.value = url.href;
    input.focus();
    input.select();
    status.textContent = document.body.dataset.copyHelp;
  }
});
