function prefersDark() {
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
}
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('sb-theme', theme);
}
function toggleTheme() {
  const cur = localStorage.getItem('sb-theme') || (prefersDark() ? 'dark':'light');
  applyTheme(cur === 'dark' ? 'light' : 'dark');
}
function initTheme() {
  const saved = localStorage.getItem('sb-theme');
  if (saved) applyTheme(saved); else applyTheme(prefersDark() ? 'dark':'light');
  const btn = document.getElementById('themeToggle');
  if (btn) btn.addEventListener('click', toggleTheme);
}

async function j(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url}: ${res.status}`);
  return res.json();
}
function el(tag, attrs={}, text='') {
  const e = document.createElement(tag);
  Object.entries(attrs).forEach(([k,v]) => (e[k]=v));
  if (text) e.appendChild(document.createTextNode(text));
  return e;
}
function fmtTime(ts) { try { return new Date(ts*1000).toLocaleString(); } catch { return ts; } }
function fillList(ul, items, base) {
  ul.innerHTML='';
  if (!items || !items.length) { ul.appendChild(el('li',{},'— none —')); return; }
  for (const r of items.slice(0, 25)) {
    const li = el('li');
    const a = el('a', {href: `${base}/${r}`, target:'_blank', rel:'noopener', className:'item'}, r);
    li.appendChild(a); ul.appendChild(li);
  }
}
function renderThumbs(container, items) {
  container.innerHTML='';
  for (const r of items.slice(0, 12)) {
    const card = el('div', {className:'thumb'});
    const img = el('img', {src: `/assets/${r}`, alt: r});
    const nm = el('div', {className:'name'}, r);
    card.appendChild(img); card.appendChild(nm);
    container.appendChild(card);
  }
}
async function init() {
  initTheme();
  document.getElementById('year').textContent = new Date().getFullYear();
  try {
    const status = await j('/status');
    document.getElementById('ver').textContent = status.version;
    document.getElementById('sha').textContent = status.commit;
    document.getElementById('time').textContent = fmtTime(status.server_time);
    document.getElementById('pdfCount').textContent = status.counts.pdfs;
    document.getElementById('assetCount').textContent = status.counts.assets;
  } catch (e) { console.error(e); }
  try {
    const pdfs = await j('/pdfs');
    fillList(document.getElementById('pdfList'), pdfs.files, '/pdfs');
  } catch(e){ console.error(e); }
  try {
    const assets = await j('/assets');
    fillList(document.getElementById('assetList'), assets.files, '/assets');
    renderThumbs(document.getElementById('thumbs'), assets.files);
  } catch(e){ console.error(e); }
}
init();
