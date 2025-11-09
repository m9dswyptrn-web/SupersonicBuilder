(function(){
  const backdrop = document.querySelector('.lightbox-backdrop');
  const stage = document.querySelector('.lightbox-stage');
  const captionEl = document.querySelector('.lightbox-caption');
  function open(src, caption){
    const img = new Image();
    img.onload = function(){
      stage.innerHTML = "";
      stage.appendChild(img);
      captionEl.textContent = caption || "";
      backdrop.classList.add('active');
    };
    img.src = src;
  }
  function close(){ backdrop.classList.remove('active'); stage.innerHTML=""; captionEl.textContent=""; }
  document.addEventListener('click', function(e){
    const t = e.target.closest('[data-lightbox-src]');
    if(t){ e.preventDefault(); open(t.getAttribute('data-lightbox-src'), t.getAttribute('data-caption')); }
    if(e.target.classList.contains('lightbox-backdrop') || e.target.classList.contains('lightbox-close')) close();
  });
  document.addEventListener('keydown', function(e){ if(e.key==='Escape') close(); });
})();