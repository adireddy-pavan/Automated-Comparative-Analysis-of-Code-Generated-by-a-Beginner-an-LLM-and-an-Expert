"""The Jinja2 template (HTML/CSS/JS) for the analysis dashboard.

Kept in its own module so ``webapp.py`` stays readable. The dashboard is a
single self-contained page: monochrome theme (matching the project's B/W house
style), tabbed navigation that also responds to the URL hash (so each view can be
screenshotted headlessly), an interactive metrics table, a code browser with
stdlib-highlighted source, an embedded figure gallery, and a findings tab.
"""

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Comparative Code Analysis — Dashboard</title>
<style>
  :root{
    --ink:#111; --ink2:#333; --mut:#666; --line:#cfcfcf; --line2:#e6e6e6;
    --bg:#ffffff; --panel:#fafafa; --chip:#f0f0f0; --shadow:0 1px 0 #e9e9e9;
  }
  *{box-sizing:border-box}
  body{margin:0;font-family:Georgia,'Times New Roman',serif;color:var(--ink);background:var(--bg);line-height:1.5}
  code,pre,.mono{font-family:'DejaVu Sans Mono',ui-monospace,Menlo,Consolas,monospace}
  header.top{border-bottom:3px solid #000;padding:22px 28px 16px}
  header.top h1{margin:0;font-size:23px;letter-spacing:.2px}
  header.top .sub{color:var(--ink2);font-size:14px;margin-top:4px}
  header.top .meta{color:var(--mut);font-size:12.5px;margin-top:6px}
  nav.tabs{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;gap:2px;
    background:#fff;border-bottom:1px solid var(--line);padding:0 18px}
  nav.tabs button{font:600 13px/1 Georgia,serif;background:none;border:0;border-bottom:3px solid transparent;
    padding:13px 16px;cursor:pointer;color:var(--mut)}
  nav.tabs button:hover{color:#000}
  nav.tabs button.active{color:#000;border-bottom-color:#000}
  main{padding:22px 28px 60px;max-width:1180px}
  section{display:none}
  section.active{display:block;animation:fade .2s ease}
  @keyframes fade{from{opacity:.3}to{opacity:1}}
  h2.sec{font-size:19px;border-bottom:1px solid #000;padding-bottom:6px;margin:6px 0 18px}
  h3{font-size:15px;margin:22px 0 8px}
  p.lead{color:var(--ink2);max-width:78ch}
  .banner{border:1px solid #000;background:var(--panel);padding:12px 14px;font-size:13px;margin:0 0 18px}
  .banner b{letter-spacing:.3px}
  .cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px;margin:8px 0 22px}
  .card{border:1px solid var(--line);padding:14px;background:#fff;box-shadow:var(--shadow)}
  .card .k{font-size:11px;text-transform:uppercase;letter-spacing:.8px;color:var(--mut)}
  .card .v{font-size:26px;font-weight:700;margin-top:6px;font-family:'DejaVu Sans Mono',monospace}
  .card .d{font-size:12px;color:var(--mut);margin-top:2px}
  table{border-collapse:collapse;width:100%;font-size:12.5px;margin:8px 0 16px}
  th,td{border:1px solid var(--line);padding:6px 9px;text-align:left}
  th{background:#efefef;cursor:pointer;user-select:none;white-space:nowrap}
  th.no-sort{cursor:default}
  tbody tr:nth-child(even){background:#fbfbfb}
  td.num,th.num{text-align:right;font-family:'DejaVu Sans Mono',monospace}
  .controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:6px 0 10px}
  .controls label{font-size:12px;color:var(--mut)}
  select,input[type=search]{font:13px Georgia,serif;padding:5px 8px;border:1px solid var(--line);background:#fff}
  .badge{display:inline-block;font:700 10.5px/1 'DejaVu Sans Mono',monospace;padding:3px 6px;border:1px solid #000}
  .badge.sig{background:#000;color:#fff}
  .badge.ns{background:#fff;color:#000;border-style:dashed}
  .pf{display:inline-block;font:700 10.5px/1 'DejaVu Sans Mono',monospace;padding:3px 6px;border:1px solid #000}
  .pf.pass{background:#000;color:#fff}
  .pf.fail{background:#fff;color:#000}
  .figgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:18px}
  .fig{border:1px solid var(--line);padding:10px;background:#fff}
  .fig img{width:100%;height:auto;display:block;border:1px solid var(--line2)}
  .fig .cap{font-size:12px;color:var(--mut);margin-top:8px;text-align:center}
  /* Code browser */
  .codewrap{display:grid;grid-template-columns:215px 1fr;gap:18px}
  .tasklist{border:1px solid var(--line);max-height:1400px;overflow:auto}
  .tasklist .grp{font:700 10.5px/1 Georgia,serif;text-transform:uppercase;letter-spacing:.7px;
    color:var(--mut);padding:10px 12px 4px;background:#f4f4f4;border-bottom:1px solid var(--line2)}
  .tasklist button{display:block;width:100%;text-align:left;border:0;border-bottom:1px solid var(--line2);
    background:#fff;padding:9px 12px;font:13px Georgia,serif;cursor:pointer}
  .tasklist button:hover{background:#f6f6f6}
  .tasklist button.active{background:#000;color:#fff}
  .taskpanel{display:none}
  .taskpanel.active{display:block}
  .taskhead{border:1px solid #000;background:var(--panel);padding:10px 14px;margin-bottom:12px}
  .taskhead .t{font-weight:700}
  .taskhead .dsc{font-size:13px;color:var(--ink2);margin-top:3px}
  .srcgrid{display:grid;grid-template-columns:1fr;gap:16px}
  .srccard{border:1px solid var(--line)}
  .srccard .hd{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between;
    background:#efefef;border-bottom:1px solid var(--line);padding:8px 12px}
  .srccard .hd .nm{font-weight:700;text-transform:capitalize;letter-spacing:.3px}
  .chips{display:flex;flex-wrap:wrap;gap:6px}
  .chip{font:11px/1 'DejaVu Sans Mono',monospace;background:var(--chip);border:1px solid var(--line);padding:4px 7px}
  pre.code{margin:0;background:#fcfcfc;padding:12px 14px;overflow:auto;font-size:12px;line-height:1.55;max-height:1500px}
  pre.code .ln{color:#bbb;display:inline-block;width:2.2em;text-align:right;margin-right:14px;user-select:none}
  pre.code .lc{white-space:pre}
  pre.code .k{font-weight:700;color:#000}
  pre.code .s{color:#555;font-style:italic}
  pre.code .c{color:#8a8a8a;font-style:italic}
  pre.code .n{color:#1a1a1a}
  pre.code .o{color:#000}
  .reflist{font-size:13px;padding-left:20px}
  .reflist li{margin:7px 0}
  a{color:#000}
  .foot{margin-top:30px;border-top:1px solid var(--line);padding-top:12px;color:var(--mut);font-size:12px}
  @media(max-width:760px){.codewrap{grid-template-columns:1fr}}
</style>
</head>
<body>
<header class="top">
  <h1>Comparative Code Analysis — Dashboard</h1>
  <div class="sub">{{ full_title }}</div>
  <div class="meta">Beginner vs LLM vs Expert · interactive view of the computed results (offline, self-contained)</div>
</header>

<nav class="tabs" id="tabs">
  <button data-tab="overview" class="active">Overview</button>
  <button data-tab="metrics">Metrics Explorer</button>
  <button data-tab="statistics">Statistics</button>
  <button data-tab="figures">Figures</button>
  <button data-tab="code">Code Browser</button>
  <button data-tab="findings">Findings</button>
</nav>

<main>
  <!-- OVERVIEW -->
  <section id="overview" class="active">
    <h2 class="sec">Overview</h2>
    <div class="banner"><b>Honest framing.</b> Curated benchmark of {{ kpis.n_tasks }} tasks. The beginner and
      expert solutions are single authored references typifying each source; the LLM solutions are labelled as model-generated; original service receipts are unavailable
      current-model samples ({{ kpis.llm_samples }} per task) — none are scraped from real people. Beginner
      edge-case failures on harder tasks are the intended experimental signal, demonstrating that the pipeline
      can detect such differences; they are not a claim about real beginners. Results describe this benchmark only.</div>
    <div class="cards">
      <div class="card"><div class="k">Tasks</div><div class="v">{{ kpis.n_tasks }}</div><div class="d">{{ kpis.n_rows }} (task × source × sample) rows</div></div>
      {% for s in sources %}
      <div class="card"><div class="k">{{ s }} pass rate</div>
        <div class="v">{{ '%.0f' % (kpis.pass_rates[s]*100) }}%</div>
        <div class="d">{{ kpis.pass_counts[s].pass }}/{{ kpis.pass_counts[s].total }} tasks fully pass</div></div>
      {% endfor %}
      <div class="card"><div class="k">Best maintainability</div><div class="v" style="font-size:20px">{{ kpis.best_mi }}</div><div class="d">highest median MI</div></div>
      <div class="card"><div class="k">Lowest complexity</div><div class="v" style="font-size:20px">{{ kpis.best_cc }}</div><div class="d">lowest median mean CC</div></div>
      <div class="card"><div class="k">Security findings</div>
        <div class="v" style="font-size:16px">{% for s in sources %}{{ s[0]|upper }}:{{ kpis.bandit_by_source[s] }} {% endfor %}</div>
        <div class="d">bandit total by source</div></div>
    </div>
    <h3>Overall quality profile</h3>
    <div class="fig" style="max-width:560px">
      {% for f in figures if f.name == 'radar_overall' %}<img src="{{ f.uri }}" alt="radar">{% endfor %}
      <div class="cap">Each axis normalised so further out = better.</div>
    </div>
  </section>

  <!-- METRICS -->
  <section id="metrics">
    <h2 class="sec">Metrics Explorer</h2>
    <p class="lead">Every (task × source × sample) row from <span class="mono">outputs/metrics.csv</span>. Click a column to sort; filter by source/difficulty or search a task.</p>
    <div class="controls">
      <label>Source <select id="fSource"><option value="">all</option>{% for s in sources %}<option>{{ s }}</option>{% endfor %}</select></label>
      <label>Difficulty <select id="fDiff"><option value="">all</option>{% for d in difficulties %}<option>{{ d }}</option>{% endfor %}</select></label>
      <label>Search <input type="search" id="fSearch" placeholder="task id…"></label>
      <span id="rowcount" class="mono" style="color:#666;font-size:12px"></span>
    </div>
    <table id="mtable"><thead><tr id="mhead"></tr></thead><tbody id="mbody"></tbody></table>
  </section>

  <!-- STATISTICS -->
  <section id="statistics">
    <h2 class="sec">Statistics</h2>
    <h3>Group medians &amp; Friedman matched-task omnibus test</h3>
    <table>
      <thead><tr><th class="no-sort">Metric</th>{% for s in sources %}<th class="no-sort num">median ({{ s }})</th>{% endfor %}
        <th class="no-sort num">Friedman chi2</th><th class="no-sort num">Friedman p</th><th class="no-sort">sig</th></tr></thead>
      <tbody>
      {% for m in metric_stats %}
        <tr><td>{{ m.label }}</td>
          {% for s in sources %}<td class="num">{{ '%.3f' % m.median[s] if m.median[s] is not none else 'N/A' }}</td>{% endfor %}
          <td class="num">{{ '%.3f' % m.kw_h if m.kw_h is not none else 'N/A' }}</td>
          <td class="num">{{ '%.4f' % m.kw_p if m.kw_p is not none else 'N/A' }}</td>
          <td>{% if m.kw_sig %}<span class="badge sig">SIG</span>{% elif m.kw_sig == false %}<span class="badge ns">ns</span>{% else %}N/A{% endif %}</td>
        </tr>
      {% endfor %}
      </tbody>
    </table>
    <h3>Paired Wilcoxon (Bonferroni) + rank-biserial</h3>
    <table>
      <thead><tr><th class="no-sort">Metric</th><th class="no-sort">Pair</th><th class="no-sort num">p (adj)</th>
        <th class="no-sort">sig</th><th class="no-sort num">Rank-biserial</th><th class="no-sort">effect type</th></tr></thead>
      <tbody>
      {% for m in metric_stats %}{% for p in m.pairs %}
        <tr><td>{{ m.label }}</td><td>{{ p.name }}</td>
          <td class="num">{{ '%.4f' % p.p_adj if p.p_adj is not none else 'N/A' }}</td>
          <td>{% if p.sig %}<span class="badge sig">SIG</span>{% elif p.sig == false %}<span class="badge ns">ns</span>{% else %}N/A{% endif %}</td>
          <td class="num">{{ '%.3f' % p.delta }}</td><td>{{ p.mag }}</td></tr>
      {% endfor %}{% endfor %}
      </tbody>
    </table>
    <p class="lead">Functional pass/fail across sources — Cochran Q = {{ '%.3f' % chi2.statistic if chi2.statistic is not none else 'N/A' }},
      p = {{ '%.4f' % chi2.p if chi2.p is not none else 'N/A' }},
      {% if chi2.significant %}<b>significant</b>{% else %}not significant{% endif %}.{% if chi2.note %} {{ chi2.note }}{% endif %}</p>
  </section>

  <!-- FIGURES -->
  <section id="figures">
    <h2 class="sec">Figures</h2>
    <div class="figgrid">
      {% for f in figures %}
      <div class="fig"><img src="{{ f.uri }}" alt="{{ f.name }}"><div class="cap mono">{{ f.name }}.png</div></div>
      {% endfor %}
    </div>
  </section>

  <!-- CODE BROWSER -->
  <section id="code">
    <h2 class="sec">Code Browser</h2>
    <p class="lead">The three authored styles for each task, with the static metrics each one earned. Pick a task:</p>
    <div class="codewrap">
      <div class="tasklist" id="tasklist">
        {% for d in difficulties %}
          <div class="grp">{{ d }}</div>
          {% for t in tasks if t.difficulty == d %}
            <button data-task="{{ t.id }}">{{ t.title }}</button>
          {% endfor %}
        {% endfor %}
      </div>
      <div id="taskpanels">
        {% for t in tasks %}
        <div class="taskpanel" id="task-{{ t.id }}">
          <div class="taskhead"><div class="t">{{ t.title }} <span class="mono" style="color:#666">({{ t.entry_point }})</span>
            · <span style="text-transform:capitalize">{{ t.difficulty }}</span></div>
            <div class="dsc">{{ t.description }}</div></div>
          <div class="srcgrid">
            {% for s in t.sources %}
            <div class="srccard">
              <div class="hd">
                <span class="nm">{{ s.source }}{% if s.n_samples > 1 %} <span class="mono" style="font-weight:400;color:#666;text-transform:none">(sample 1 of {{ s.n_samples }})</span>{% endif %}</span>
                <span class="chips">
                  <span class="chip">{{ s.loc }} LOC</span>
                  <span class="chip">CC {{ '%.1f' % s.mean_cc if s.mean_cc is not none else 'N/A' }}</span>
                  <span class="chip">MI {{ '%.1f' % s.mi if s.mi is not none else 'N/A' }}</span>
                  <span class="chip">pylint {{ '%.1f' % s.pylint_score if s.pylint_score is not none else 'N/A' }}</span>
                  <span class="chip">bandit {{ s.bandit_total }}</span>
                  <span class="pf {{ 'pass' if s.passed else 'fail' }}">{{ 'PASS' if s.passed else 'FAIL' }} {{ s.tests }}</span>
                </span>
              </div>
              {{ s.code_html }}
            </div>
            {% endfor %}
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
  </section>

  <!-- FINDINGS -->
  <section id="findings">
    <h2 class="sec">Findings</h2>
    <h3>RQ2 — Pass rate by difficulty</h3>
    <table>
      <thead><tr><th class="no-sort">Difficulty</th>{% for s in sources %}<th class="no-sort num">{{ s }}</th>{% endfor %}</tr></thead>
      <tbody>
      {% for d in difficulties %}
        <tr><td style="text-transform:capitalize">{{ d }}</td>
          {% for s in sources %}<td class="num">{{ by_difficulty[d][s].pass }}/{{ by_difficulty[d][s].total }}
            ({{ '%.0f' % (by_difficulty[d][s].rate*100) if by_difficulty[d][s].rate is not none else 0 }}%)</td>{% endfor %}
        </tr>
      {% endfor %}
      </tbody>
    </table>
    <h3>RQ2 — Functional pass@k (Chen et al. 2021)</h3>
    <p class="lead">Unbiased pass@k averaged over tasks. Only defined for k &le; the number of samples, so
      single-sample sources show N/A beyond pass@1; the LLM arm ({{ kpis.llm_samples }} samples per task) yields a
      descriptive multi-sample estimate (model independence unverified).</p>
    <table>
      <thead><tr><th class="no-sort">Source</th><th class="no-sort num">samples/task</th>{% for k in pass_at_k_ks %}<th class="no-sort num">pass@{{ k }}</th>{% endfor %}</tr></thead>
      <tbody>
      {% for s in sources %}
        <tr><td>{{ s }}</td><td class="num">{{ pass_at_k[s].n_samples }}</td>
          {% for k in pass_at_k_ks %}{% set v = pass_at_k[s]['k' ~ k] %}<td class="num">{{ '%.3f' % v if v is not none else 'N/A' }}</td>{% endfor %}
        </tr>
      {% endfor %}
      </tbody>
    </table>
    <h3>RQ1 — Which metrics differ significantly across the three sources?</h3>
    <div class="chips">
      {% for m in sig_summary %}
        <span class="chip">{{ m.label }}: {% if m.sig %}<b>SIG</b>{% elif m.sig == false %}ns{% else %}N/A{% endif %}</span>
      {% endfor %}
    </div>
    <h3>RQ3 — Does the LLM resemble the beginner or the expert?</h3>
    <p class="lead">Across {{ rq3.metric_count }} metrics, the LLM's median is closer to the beginner on <b>{{ rq3.beginner }}</b>,
      closer to the expert on <b>{{ rq3.expert }}</b>, tied on <b>{{ rq3.ties }}</b> →
      overall it most resembles <b>{{ rq3.verdict }}</b>.</p>
    <h3>RQ4 — Where do static metrics disagree with correctness?</h3>
    {% if rq4 %}
    <p class="lead">Concrete case in the data: task <b>{{ rq4.task_id }}</b> ({{ rq4.source }}) scores a
      maintainability index of <b>{{ rq4.mi }}</b> and pylint <b>{{ rq4.pylint }}/10</b>, yet still
      <b>fails functional tests</b> ({{ rq4.passed }}/{{ rq4.total }} passing). Healthy static scores, wrong code —
      which is why every metric here is paired with executed tests.</p>
    {% else %}
    <p class="lead">No solution combined healthy static metrics with a test failure in this run.</p>
    {% endif %}
    <h3>References</h3>
    <ol class="reflist">
      {% for r in references %}<li>{{ r.text }} <a href="{{ r.url }}">{{ r.url }}</a></li>{% endfor %}
    </ol>
    <div class="foot">Full prose report: <a href="report.html">report.html</a> ·
      Generated from <span class="mono">outputs/metrics.csv</span> and <span class="mono">outputs/stats.json</span>.</div>
  </section>
</main>

<script type="application/json" id="metricsData">{{ metrics_json }}</script>
<script>
(function(){
  // ---- Tabs (hash-aware so headless screenshots can target a view) ----
  var tabs = document.querySelectorAll('#tabs button');
  var sections = document.querySelectorAll('main > section');
  function showTab(name){
    tabs.forEach(function(b){ b.classList.toggle('active', b.dataset.tab===name); });
    sections.forEach(function(s){ s.classList.toggle('active', s.id===name); });
  }
  tabs.forEach(function(b){ b.addEventListener('click', function(){
    history.replaceState(null,'','#'+b.dataset.tab); showTab(b.dataset.tab);
  }); });
  // Hash forms: "#metrics" (a tab) or "#code:two_sum" (tab + preselected task).
  var hashParts = (location.hash||'#overview').slice(1).split(':');
  var initialTab = hashParts[0];
  if (document.getElementById(initialTab)) showTab(initialTab);

  // ---- Metrics table ----
  var DATA = JSON.parse(document.getElementById('metricsData').textContent);
  var COLS = Object.keys(DATA[0]||{});
  var NUMERIC = {sample:1,mean_cc:1,max_cc:1,mi:1,halstead_volume:1,sloc:1,comments:1,
                 pylint_score:1,pylint_issues:1,bandit_total:1,tests_passed:1,tests_total:1};
  var sortKey='task_id', sortDir=1;
  var head=document.getElementById('mhead');
  COLS.forEach(function(c){
    var th=document.createElement('th'); th.textContent=c;
    if(NUMERIC[c]) th.className='num';
    th.addEventListener('click', function(){
      if(sortKey===c){ sortDir=-sortDir; } else { sortKey=c; sortDir=1; }
      render();
    });
    head.appendChild(th);
  });
  function passCell(v){
    var on = (v===true||v==='True'||v==='true'||v===1||v==='1');
    return '<span class="pf '+(on?'pass':'fail')+'">'+(on?'PASS':'FAIL')+'</span>';
  }
  function render(){
    var fs=document.getElementById('fSource').value;
    var fd=document.getElementById('fDiff').value;
    var fq=document.getElementById('fSearch').value.toLowerCase();
    var rows=DATA.filter(function(r){
      return (!fs||r.source===fs) && (!fd||r.difficulty===fd) &&
             (!fq||String(r.task_id).toLowerCase().indexOf(fq)>=0);
    });
    rows.sort(function(a,b){
      var x=a[sortKey], y=b[sortKey];
      if(NUMERIC[sortKey]){ x=parseFloat(x); y=parseFloat(y); }
      if(x<y) return -1*sortDir; if(x>y) return 1*sortDir; return 0;
    });
    var body=document.getElementById('mbody'); body.innerHTML='';
    rows.forEach(function(r){
      var tr=document.createElement('tr');
      COLS.forEach(function(c){
        var td=document.createElement('td');
        if(c==='functional_pass'){ td.innerHTML=passCell(r[c]); }
        else { td.textContent=r[c]; if(NUMERIC[c]) td.className='num'; }
        tr.appendChild(td);
      });
      body.appendChild(tr);
    });
    document.getElementById('rowcount').textContent=rows.length+' rows';
  }
  ['fSource','fDiff','fSearch'].forEach(function(id){
    document.getElementById(id).addEventListener('input', render);
  });
  render();

  // ---- Code browser ----
  var taskBtns=document.querySelectorAll('#tasklist button');
  var panels=document.querySelectorAll('.taskpanel');
  function showTask(id){
    taskBtns.forEach(function(b){ b.classList.toggle('active', b.dataset.task===id); });
    panels.forEach(function(p){ p.classList.toggle('active', p.id==='task-'+id); });
  }
  taskBtns.forEach(function(b){ b.addEventListener('click', function(){ showTask(b.dataset.task); }); });
  var wantTask = hashParts[1];
  if(wantTask && document.getElementById('task-'+wantTask)) showTask(wantTask);
  else if(taskBtns.length) showTask(taskBtns[0].dataset.task);
})();
</script>
</body>
</html>
"""
