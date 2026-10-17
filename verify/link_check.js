// Paste into the browser console on any https://leetcode.com page (LeetCode blocks scripts, but not its own page).
// Replace DATA with the contents of verify/compact_slugs.txt, then run. It returns only the problems that need attention.
(async function () {
  const DATA = "PASTE compact_slugs.txt HERE";
  const probs = DATA.split("|").map(x => { const p = x.split(":"); return { n: p[0], slug: p[1], d: p[2] }; });
  const issues = []; let ok = 0; const B = 20;
  for (let i = 0; i < probs.length; i += B) {
    const batch = probs.slice(i, i + B);
    const q = "query{" + batch.map((p, k) => `q${k}:question(titleSlug:"${p.slug}"){questionFrontendId title difficulty isPaidOnly}`).join(" ") + "}";
    let res = null;
    for (let a = 0; a < 3 && !res; a++) {
      try { const r = await fetch("/graphql", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ query: q }) }); if (r.status === 200) res = await r.json(); else await new Promise(z => setTimeout(z, 1500)); }
      catch (e) { await new Promise(z => setTimeout(z, 1500)); }
    }
    batch.forEach((p, k) => {
      const d = res && res.data && res.data["q" + k];
      if (!d) { issues.push(`${p.n} ${p.slug}: NOT FOUND`); return; }
      const df = { Easy: "E", Medium: "M", Hard: "H" }[d.difficulty], m = [];
      if (String(d.questionFrontendId) !== p.n) m.push("number is " + d.questionFrontendId);
      if (df !== p.d) m.push("difficulty is " + df);
      if (d.isPaidOnly) m.push("PREMIUM");
      if (m.length) issues.push(`${p.n} ${p.slug} (${d.title}): ${m.join(", ")}`); else ok++;
    });
  }
  return JSON.stringify({ checked: probs.length, ok, issues });
})();
