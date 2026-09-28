const dialog = document.querySelector('#photo-dialog');
const full = document.querySelector('#photo-full');
for (const button of document.querySelectorAll('.photo-open')) {
  button.addEventListener('click', () => {
    full.src = button.dataset.image;
    full.alt = button.dataset.title;
    document.querySelector('#photo-title').textContent = button.dataset.title;
    dialog.showModal();
    document.body.classList.add('dialog-open');
  });
}
document.querySelector('#photo-close').onclick = () => dialog.close();
dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
dialog.addEventListener('close', () => document.body.classList.remove('dialog-open'));
