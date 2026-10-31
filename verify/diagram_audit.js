// Run in the browser console on any page served from this site (e.g. python -m http.server 8765).
// Lists static diagrams whose text spills out of its box, free text that overlaps a box, or boxes outside the canvas.
(async () => {
  const root = location.href.replace(/systems\/[^/]*$/, '').replace(/[^/]*$/, '');
  const hub = new DOMParser().parseFromString(await (await fetch(root + 'systems.html')).text(), 'text/html');
  const names = [...new Set([...hub.querySelectorAll('a[href]')].map(a => a.getAttribute('href').replace(/^.*\//, '')))].filter(n => /^S\d+_.*\.html$/.test(n));
  const bad = []; let n = 0;
  for (const name of names) {
    const html = await (await fetch(root + 'systems/' + name)).text();
    const doc = new DOMParser().parseFromString(html, 'text/html');
    for (const f of doc.querySelectorAll('svg.dg')) {
      n++;
      const host = document.createElement('div');
      host.style.cssText = 'position:absolute;left:0;top:0;width:760px;visibility:hidden';
      host.innerHTML = f.outerHTML; document.body.appendChild(host);
      const svg = host.querySelector('svg'), rects = [...svg.querySelectorAll('rect.dg-box')], vb = svg.viewBox.baseVal;
      const g = r => ['x', 'y', 'width', 'height'].map(k => +r.getAttribute(k));
      for (const t of svg.querySelectorAll('text')) {
        const b = t.getBBox(), cx = b.x + b.width / 2, cy = b.y + b.height / 2;
        const home = rects.find(r => { const [x, y, w, h] = g(r); return cx >= x && cx <= x + w && cy >= y && cy <= y + h; });
        if (home) { const [x, y, w, h] = g(home); if (b.x < x + 2 || b.x + b.width > x + w - 2 || b.y < y || b.y + b.height > y + h) bad.push({ name, spills: t.textContent }); }
        else for (const r of rects) { const [x, y, w, h] = g(r); if (!(b.x + b.width < x || b.x > x + w || b.y + b.height < y || b.y > y + h)) bad.push({ name, overlaps: t.textContent }); }
      }
      for (const r of rects) { const [x, y, w, h] = g(r); if (y < 0 || x < 0 || y + h > vb.height || x + w > vb.width) bad.push({ name, outsideCanvas: svg.getAttribute('aria-label') }); }
      host.remove();
    }
  }
  return { figures: n, problems: bad };
})()
