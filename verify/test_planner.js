// Tests for build/planner_core.js. Usage: node verify/test_planner.js <planner-data.json>
const fs = require('fs'), path = require('path');
const P = require(path.join(__dirname, '..', 'build', 'planner_core.js'));
const data = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const nums = data.map(t => t.num);
let failed = 0, passed = 0;
function ok(cond, msg) { if (cond) passed++; else { failed++; console.log('FAIL', msg); } }
function base(over) { return P.merge(P.defaultSettings('2026-11-02', nums), over || {}); }   // 2026-11-02 is a Monday
function allTasks(plan) { return plan.days.flatMap(d => d.tasks.map(t => Object.assign({date: d.date}, t))); }

// 1. default plan: structure and invariants
const AMPLE = {topics: nums.filter(n => n <= '09'), weeks: 52, weekdayHours: 3, weekendHours: 5};
let plan = P.generate(data, base(AMPLE), {});
ok(plan.stats.fits && plan.mode.depth === 'standard' && plan.mode.secondary === 'full' && plan.mode.reviews === 2, 'an ample plan keeps full depth: ' + JSON.stringify(plan.mode));
ok(!plan.error, 'default plan builds');
ok(plan.stats.tasks > 300, 'default plan has many tasks: ' + plan.stats.tasks);
let violations = 0, restViolations = 0, order = true, prev = '';
plan.days.forEach(d => {
  if (d.minutes > d.cap + 10) violations++;
  if (d.rest && d.tasks.length) restViolations++;
  if (d.date <= prev) order = false; prev = d.date;
  if (!d.rest && P.parseISO(d.date).getDay() === 0 && d.cap === 0) restViolations++;
});
ok(violations === 0, 'no day exceeds its capacity (+10 min overflow): ' + violations);
ok(restViolations === 0, 'nothing is scheduled on rest days');
ok(order, 'days are strictly increasing');
ok(plan.days.every(d => !d.rest || P.parseISO(d.date).getDay() === 0), 'only Sundays are rest days with the default settings');
console.log('  default: ' + P.fmtMin(plan.stats.totalMin) + ', finish ' + plan.stats.finish + ', fits=' + plan.stats.fits + ', mode=' + plan.mode.depth + '/' + plan.mode.secondary + ', notes=' + plan.stats.notes.length);

// 2. reviews come after the learning of their pattern
const tasks = allTasks(plan), lastOf = {};
tasks.forEach(t => { if (t.last) lastOf[t.topicNum + '-' + t.pn] = t.date; });
let badReview = 0, reviews = 0;
tasks.filter(t => t.kind === 'review').forEach(t => {
  reviews++;
  const l = lastOf[t.topicNum + '-' + t.pn];
  if (!l || P.diffDays(P.parseISO(l), P.parseISO(t.date)) < 3) badReview++;
});
ok(reviews > 50, 'spaced reviews are scheduled: ' + reviews);
ok(badReview === 0, 'every review is at least 3 days after its pattern: ' + badReview);
ok(new Set(tasks.map(t => t.id)).size === tasks.length, 'task ids are unique');

// 3. weekly checkpoints and the final mock
ok(tasks.filter(t => t.kind === 'checkpoint').length >= 8, 'weekly checkpoints exist: ' + tasks.filter(t => t.kind === 'checkpoint').length);
ok(tasks.filter(t => t.kind === 'mock').length === 1, 'exactly one final mock');
const noCk = P.generate(data, base(Object.assign({}, AMPLE, {checkpoints: false})), {});
ok(allTasks(noCk).every(t => t.kind !== 'checkpoint' && t.kind !== 'mock'), 'checkpoints can be switched off');

// 4. too little time: trimmed or honest about the shortfall
const tight = P.generate(data, base({weeks: 2}), {});
ok(!tight.error && (!tight.stats.fits ? tight.stats.shortfallDays > 0 : true), 'tight plan reports shortfall when it does not fit');
ok(tight.stats.notes.length > 0, 'tight plan explains what was trimmed');
ok(tight.stats.totalMin < tight.stats.requestedMin, 'tight plan contains less work than was requested');
const mid = P.generate(data, base({weeks: 8, depth: 'deep'}), {});
ok(mid.stats.notes.some(n => /depth reduced|secondary/i.test(n)) || mid.stats.fits, 'deep plan in 8 weeks is trimmed or fits');

// 5. a small selection fits easily
const trees = P.generate(data, base({topics: ['09'], weeks: 4}), {});
ok(trees.stats.fits && trees.stats.topics === 1, 'one topic in four weeks fits');
ok(trees.stats.spareDays >= 0, 'spare days are reported');
ok(allTasks(trees).filter(t => t.topicNum).every(t => t.topicNum === '09'), 'only the selected topic appears');

// 6. skip solved problems
const topic9 = data.find(t => t.num === '09');
const progress = {}; let marked = 0;
topic9.patterns.forEach(p => p.problems.slice(0, 2).forEach(pr => { progress[topic9.id + '-' + pr[0]] = 1; marked++; }));
const skipped = P.generate(data, base({topics: ['09'], weeks: 6}), progress);
ok(skipped.stats.skippedSolved > 0, 'solved problems are skipped: ' + skipped.stats.skippedSolved);
ok(skipped.stats.problems < P.generate(data, base({topics: ['09'], weeks: 6}), {}).stats.problems, 'skipping reduces the problem count');
const keep = P.generate(data, base({topics: ['09'], weeks: 6, skipSolved: false}), progress);
ok(keep.stats.skippedSolved === 0, 'skip can be switched off');

// 7. depth ordering with plenty of time
const mins = d => P.generate(data, base({topics: ['09', '12'], weeks: 40, weekdayHours: 3, depth: d}), {}).stats.totalMin;
const [l, s, dp] = ['light', 'standard', 'deep'].map(mins);
ok(l < s && s <= dp, 'deeper plans take longer: ' + [l, s, dp].join(' < '));
const beginner = P.generate(data, base({topics: ['09'], weeks: 30, level: 'beginner'}), {}).stats.totalMin;
const advanced = P.generate(data, base({topics: ['09'], weeks: 30, level: 'advanced'}), {}).stats.totalMin;
ok(beginner > advanced, 'beginners need more time than advanced learners');

// 8. error cases
ok(P.generate(data, base({topics: []}), {}).error, 'no topics is an error');
ok(P.generate(data, base({weekdayHours: 0, weekendHours: 0}), {}).error, 'no study time is an error');
const allDone = {}; data.forEach(t => t.patterns.forEach(p => p.problems.forEach(pr => allDone[t.id + '-' + pr[0]] = 1)));
ok(P.generate(data, base({topics: ['09']}), allDone).stats.problems === 0, 'when every problem is solved only learning items remain');

// 9. tiny daily time still makes progress through splitting
const tiny = P.generate(data, base({topics: ['02'], weeks: 52, weekdayHours: 0.5, weekendHours: 0.5, restDay: 'none'}), {});
ok(!tiny.error && tiny.days.every(d => d.minutes <= d.cap + 10), 'tiny days respect their capacity');
ok(allTasks(tiny).some(t => / \(part 2\)$/.test(t.title)), 'long tasks are split across days');

// 9b. starting on a rest day does not create an empty first week
const sun = P.generate(data, base({startDate: '2026-11-01', topics: ['09'], weeks: 8}), {});
ok(sun.weeks[0].minutes > 0 && sun.weeks[0].days.some(d => d.tasks.length), 'first week has work even when the start date is a rest day');
ok(sun.weeks.every((w, i) => w.n === i + 1), 'weeks are numbered consecutively');

// 10. weekends only and no rest day
const we = P.generate(data, base({topics: ['09'], weeks: 12, weekdayHours: 0, weekendHours: 3, restDay: 'none'}), {});
ok(allTasks(we).every(t => [0, 6].indexOf(P.parseISO(t.date).getDay()) >= 0), 'weekends-only plan uses only Saturday and Sunday');

// 11. sanitize
const clean = P.sanitize({topics: ['9', '09', '99', 'x'], weeks: 500, weekdayHours: -3, level: 'wizard', depth: 'deep', restDay: 'mon', startDate: 'tomorrow'}, nums);
ok(JSON.stringify(clean.topics) === '["09"]' && clean.weeks === 52 && clean.weekdayHours === 0 && !clean.level && clean.depth === 'deep' && !clean.restDay && !clean.startDate, 'sanitize clamps and drops invalid values: ' + JSON.stringify(clean));

// 12. offline assistant
const a = P.offlineIntent('I have 6 weeks, 2 hours per day, only graphs and dp', base(), nums, '2026-11-02');
ok(a.patch && a.patch.weeks === 6 && a.patch.weekdayHours === 2 && JSON.stringify(a.patch.topics) === '["12","13","15","16"]', 'offline parser: ' + JSON.stringify(a.patch));
const b = P.offlineIntent('make it lighter and I am a beginner', base(), nums, '2026-11-02');
ok(b.patch.depth === 'light' && b.patch.level === 'beginner', 'offline parser: depth and level');
const c = P.offlineIntent('skip tries and add design', base({topics: ['01', '11']}), nums, '2026-11-02');
ok(c.patch && c.patch.topics.indexOf('11') < 0, 'offline parser: skip removes a topic');
const d = P.offlineIntent('I fell behind', base(), nums, '2026-11-09');
ok(d.patch.startDate === '2026-11-09', 'offline parser: restart from today');
ok(P.offlineIntent('hello there', base(), nums, '2026-11-02').patch === null, 'offline parser: no change for chit-chat');
const e = P.offlineIntent('weekends only, 3 hours on weekends', base(), nums, '2026-11-02');
ok(e.patch.weekdayHours === 0 && e.patch.weekendHours === 3, 'offline parser: weekends only: ' + JSON.stringify(e.patch));

// 13. model reply parsing
const r1 = P.parseAgentReply('Sure, here is a lighter plan.\n<settings>{"depth":"light","weeks":8,"topics":["09","12","99"]}</settings>', nums);
ok(r1.text === 'Sure, here is a lighter plan.' && r1.patch.depth === 'light' && r1.patch.weeks === 8 && JSON.stringify(r1.patch.topics) === '["09","12"]', 'reply parser applies valid keys only');
ok(P.parseAgentReply('Fine.\n<settin', nums).text === 'Fine.', 'a partial tag is hidden while streaming');
ok(P.parseAgentReply('Fine.\n<settings>{"depth":', nums).text === 'Fine.' && P.parseAgentReply('x<settings>not json</settings>', nums).patch === null, 'broken settings are ignored');
ok(P.parseAgentReply('No change needed.', nums).patch === null, 'no settings block means no patch');

// 14. exports
const ics = P.toICS(plan, '20261102T000000Z');
const events = (ics.match(/BEGIN:VEVENT/g) || []).length;
ok(events === plan.days.filter(x => !x.rest && x.tasks.length).length && ics.startsWith('BEGIN:VCALENDAR') && ics.indexOf('\r\n') > 0, 'calendar export has one event per study day');
ok(/Week 1 /.test(P.toText(plan)) && P.toText(plan).indexOf('[ ]') > 0, 'text export has weeks and checkboxes');

console.log('planner tests: passed ' + passed + ', failed ' + failed);
process.exit(failed ? 1 : 0);
