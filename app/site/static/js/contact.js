(() => {
  const form = document.getElementById('contact-form');
  const button = form.querySelector('button[type="submit"]');
  const status = document.getElementById('contact-status');
  const label = button.textContent;
  let submissionId = crypto.randomUUID();
  let pending = false;
  button.disabled = false;
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (pending || !form.reportValidity()) return;
    pending = true;
    button.disabled = true;
    button.textContent = form.dataset.sending;
    status.textContent = '';
    try {
      const response = await fetch(form.action, {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({...Object.fromEntries(new FormData(form)), submission_id: submissionId}),
        signal: AbortSignal.timeout(20000)
      });
      if (!response.ok) throw new Error('Submission failed');
      form.reset();
      submissionId = crypto.randomUUID();
      status.textContent = form.dataset.success;
    } catch {
      status.textContent = form.dataset.error;
    } finally {
      pending = false;
      button.disabled = false;
      button.textContent = label;
      status.focus();
    }
  });
})();
