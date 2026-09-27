(() => {
  const story = document.querySelector('.villa-story');
  if (!story) return;
  const stage = story.querySelector('.model-stage');
  const intro = story.querySelector('.story-intro');
  const caption = story.querySelector('.story-caption');
  const progressBar = story.querySelector('.story-progress span');
  const explore = document.querySelector('#explore-model');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let frame = 0, exploring = false, previousCaption = -1;
  const clamp = value => Math.max(0, Math.min(1, value));
  function update() {
    frame = 0;
    const rect = story.getBoundingClientRect();
    const progress = reduced.matches ? 0 : clamp(-rect.top / Math.max(1, story.offsetHeight - stage.offsetHeight));
    progressBar.style.transform = `scaleX(${progress})`;
    intro.style.opacity = String(clamp(1 - progress * 4));
    intro.style.transform = reduced.matches ? 'none' : `translateY(${-progress * 65}px)`;
    const captionIndex = progress < .63 ? 0 : 1;
    if (captionIndex !== previousCaption) {
      caption.innerHTML = captionIndex === 0
        ? '<span>01 / SEIS CHALÉS BASIC</span><p>Seu espaço.<br><em>Seu tempo.</em></p>'
        : '<span>02 / NATUREZA E CONVIVÊNCIA</span><p>Jardins que conectam.<br><em>Um lugar em comum.</em></p>';
      previousCaption = captionIndex;
    }
    caption.style.opacity = reduced.matches ? '0' : String(clamp((progress - .25) * 6) * clamp((1.06 - progress) * 7));
    caption.style.transform = `translateY(${(1 - clamp((progress - .25) * 6)) * 20}px)`;
    if (!exploring) window.dispatchEvent(new CustomEvent('villa:scroll', { detail: { progress } }));
  }
  const schedule = () => { if (!frame) frame = requestAnimationFrame(update); };
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule, { passive: true });
  window.addEventListener('villa:ready', schedule);
  reduced.addEventListener('change', schedule);
  explore.addEventListener('click', () => {
    exploring = !exploring;
    story.classList.toggle('exploring', exploring);
    document.body.classList.toggle('is-exploring', exploring);
    explore.setAttribute('aria-pressed', String(exploring));
    explore.innerHTML = exploring ? 'Continuar a leitura <span>↓</span>' : 'Explorar a maquete <span>↗</span>';
    window.dispatchEvent(new CustomEvent('villa:explore', { detail: { enabled: exploring } }));
    if (!exploring) document.querySelector('#conceito').scrollIntoView({ behavior: reduced.matches ? 'instant' : 'smooth' });
    schedule();
  });
  // Sections remain readable if JS or an optional animation API is unavailable.
  if ('IntersectionObserver' in window && !reduced.matches) {
    document.documentElement.classList.add('motion-ready');
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) if (entry.isIntersecting) {
        entry.target.classList.remove('awaiting-reveal'); observer.unobserve(entry.target);
      }
    }, { threshold: 0, rootMargin: '0px 0px -35px 0px' });
    document.querySelectorAll('[data-reveal]').forEach(section => {
      if (section.getBoundingClientRect().top >= innerHeight) section.classList.add('awaiting-reveal');
      observer.observe(section);
    });
  }
  schedule();
})();
