'use strict';
(() => {
  if (!('IntersectionObserver' in window) || !Element.prototype.animate) return;
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  const selector = '.page-head,.stat,.hero,.card,.post,.menu-item,.person,.notification,.auth-story>h1,.auth-story>p,.auth-form>div,#modalContent>.notice,#modalContent>.post-body,.exercise,.exercise-builder-row,.review-note,.field,.review-card,.step-pane>h2,.field-group,.delivery-note';
  const revealed = new WeakSet(), pending = new Set(), running = new Map();
  let scheduled = false;
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      const el = entry.target;
      observer.unobserve(el); pending.delete(el); revealed.add(el);
      if (preference.matches || el.contains(document.activeElement)) continue;
      // Uma entrada por elemento. Sem esconder novamente ao subir a página.
      const animation = el.animate([
        { opacity:0, transform:'translateY(12px)' },
        { opacity:1, transform:'translateY(0)' }
      ], { duration:520, easing:'cubic-bezier(.22,1,.36,1)' });
      running.set(el, animation);
      const clear = () => running.delete(el);
      animation.onfinish = clear; animation.oncancel = clear;
    }
  }, { threshold:0, rootMargin:'0px 0px -12px 0px' });
  function scan() {
    scheduled = false;
    for (const el of pending) if (!el.isConnected) { observer.unobserve(el); pending.delete(el); }
    for (const [el, animation] of running) if (!el.isConnected) animation.cancel();
    document.querySelectorAll(selector).forEach(el => {
      if (revealed.has(el) || pending.has(el)) return;
      // Se o cartão entra inteiro, seus filhos não recebem outra animação.
      if (el.parentElement?.closest(selector)) return;
      if (preference.matches) { revealed.add(el); return; }
      pending.add(el); observer.observe(el);
    });
  }
  function schedule() { if (!scheduled) { scheduled = true; requestAnimationFrame(scan); } }
  new MutationObserver(mutations => { if (mutations.some(m => m.addedNodes.length || m.removedNodes.length)) schedule(); }).observe(document.body, { childList:true, subtree:true });
  preference.addEventListener('change', () => {
    if (preference.matches) {
      for (const animation of running.values()) animation.cancel();
      for (const el of pending) { observer.unobserve(el); revealed.add(el); }
      pending.clear();
    } else schedule();
  });
  document.addEventListener('focusin', event => {
    for (const [el, animation] of running) if (el.contains(event.target)) animation.finish();
  });
  window.addEventListener('beforeprint', () => { for (const animation of running.values()) animation.cancel(); });
  scan();
})();

// Amortece os passos grandes da roda do mouse; gestos finos continuam nativos.
(() => {
  const mouse = matchMedia('(hover: hover) and (pointer: fine)');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let frame = 0, scroller = null, destination = 0, lastTime = 0;
  function stop() { cancelAnimationFrame(frame); frame = 0; scroller = null; }
  function tick(time) {
    if (!scroller?.isConnected || (scroller.tagName === 'DIALOG' && !scroller.open)) return stop();
    const elapsed = Math.min(40, time - lastTime || 16); lastTime = time;
    const gap = destination - scroller.scrollTop;
    if (Math.abs(gap) <= 1) { scroller.scrollTop = destination; return stop(); }
    scroller.scrollTop += gap * (1 - Math.exp(-elapsed / 45));
    frame = requestAnimationFrame(tick);
  }
  function findScroller(target) {
    for (let el = target; el && el !== document.body; el = el.parentElement) {
      if (/(auto|scroll)/.test(getComputedStyle(el).overflowY) && el.scrollHeight > el.clientHeight + 1) return el;
    }
    if (document.querySelector('dialog[open]')) return null;
    return document.scrollingElement;
  }
  document.addEventListener('wheel', event => {
    if (!mouse.matches || !event.cancelable || event.defaultPrevented || event.ctrlKey || event.metaKey || event.shiftKey || Math.abs(event.deltaX) > Math.abs(event.deltaY)) return stop();
    if (!(event.target instanceof Element) || event.target.closest('input,select,textarea,[contenteditable=true]')) return stop();
    // Deltas pequenos são comuns no trackpad: preserve sua precisão e inércia.
    if (event.deltaMode === 0 && Math.abs(event.deltaY) < 50) return stop();
    const el = findScroller(event.target);
    if (!el) return;
    const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? el.clientHeight : 1;
    const delta = Math.max(-96, Math.min(96, event.deltaY * unit * 0.55));
    const max = el.scrollHeight - el.clientHeight;
    if (!delta || max <= 0) return;
    const base = scroller === el ? destination : el.scrollTop;
    const next = Math.max(0, Math.min(max, base + delta));
    if (next === el.scrollTop && !frame) return;
    event.preventDefault();
    if (scroller !== el) { stop(); scroller = el; }
    destination = Math.max(el.scrollTop - 240, Math.min(el.scrollTop + 240, next));
    if (reduced.matches) { el.scrollTop = destination; stop(); return; }
    if (!frame) { lastTime = performance.now(); frame = requestAnimationFrame(tick); }
  }, { passive:false });
  for (const name of ['pointerdown','touchstart','keydown']) document.addEventListener(name, stop, { passive:true, capture:true });
  reduced.addEventListener('change', stop);
  window.addEventListener('blur', stop);
})();

