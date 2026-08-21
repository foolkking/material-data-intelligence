/* UX-V1.3.1 is deliberately isolated: all data here are stable research fixtures. */
const app = document.querySelector('#app');
const CLOSURE_REVISION = 'UX-V1.3.1-final-2026-08-18';

const state = {
  route: location.hash.replace('#', '') || 'landing',
  viewer: 'table',
  research: 'complete',
  inspector: null,
  preview: null,
  auth: 'out',
  loginOpen: false,
  restoreFocusAction: null,
  conversationWidth: 36,
};

const materials = [
  ['BaTiO3', -3.41, 3.20, 6.02, '立方钙钛矿'],
  ['SrTiO3', -3.14, 3.25, 5.11, '立方钙钛矿'],
  ['CaTiO3', -3.09, 3.48, 4.01, '正交钙钛矿'],
  ['PbTiO3', -2.82, 2.95, 7.52, '四方钙钛矿'],
  ['BaZrO3', -3.23, 4.18, 6.25, '立方钙钛矿'],
  ['SrZrO3', -3.02, 4.36, 5.17, '正交钙钛矿'],
  ['CaZrO3', -2.91, 4.52, 4.11, '正交钙钛矿'],
  ['KNbO3', -2.76, 3.08, 4.64, '铁电钙钛矿'],
];

const navItems = [
  ['project', '概览'],
  ['data', '数据'],
  ['research', '研究'],
  ['reports', '报告'],
];

function go(route) {
  state.route = route;
  location.hash = route;
  state.inspector = null;
  state.preview = null;
  document.body.style.overflow = '';
  render();
}

function button(label, action, className = 'btn', title = '') {
  return `<button class="${className}" type="button" ${title ? `title="${title}" aria-label="${title}"` : ''} data-action="${action}">${label}</button>`;
}

function globalBar({ project = false, landing = false } = {}) {
  const signedIn = state.auth === 'in';
  const actions = !signedIn
    ? button('登录', 'open-login', 'btn small')
    : landing
      ? `${button('进入控制台', 'go:console', 'btn small')}<button class="avatar" type="button" title="账户菜单" aria-label="账户菜单">YL</button>`
      : `${button('⌕', 'noop', 'icon-btn', '搜索')}<button class="avatar" type="button" title="账户菜单" aria-label="账户菜单">YL</button>`;
  return `
    <header class="global-bar">
      <a class="brand" href="#${landing ? 'landing' : 'console'}" data-route="${landing ? 'landing' : 'console'}" aria-label="材料智能体平台">
        <span class="brand-mark" aria-hidden="true"></span><span>材料智能体平台</span>
      </a>
      <div class="global-context">${project ? '<span>项目</span><span aria-hidden="true">/</span><strong>Perovskite stability study</strong>' : '<span>材料数据智能与科学分析</span>'}</div>
      <div class="global-actions">${actions}</div>
    </header>`;
}

function projectNav(active) {
  return `<nav class="project-nav" aria-label="项目导航">${navItems.map(([id, label]) =>
    `<a href="#${id}" data-route="${id}" class="${active === id ? 'active' : ''}">${label}</a>`).join('')}</nav>`;
}

function plotSvg({ mini = false, interactive = false } = {}) {
  const dots = [
    ['BaTiO3', 112, 221, '#0b6b57'], ['SrTiO3', 190, 212, '#0b6b57'], ['CaTiO3', 240, 187, '#4c7668'],
    ['PbTiO3', 343, 250, '#a36a38'], ['BaZrO3', 160, 112, '#4c7668'], ['SrZrO3', 246, 89, '#315e78'],
    ['CaZrO3', 297, 73, '#315e78'], ['KNbO3', 364, 234, '#a36a38'],
  ];
  const width = mini ? 430 : 760;
  const height = mini ? 235 : 390;
  const sx = mini ? .54 : 1;
  const sy = mini ? .58 : 1;
  return `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="formation energy 与 band gap 的散点图">
    <rect width="${width}" height="${height}" fill="#ffffff"/>
    ${[80, 145, 210, 275, 340].map(y => `<line x1="72" x2="${mini ? 410 : 710}" y1="${y * sy}" y2="${y * sy}" stroke="#d9dfdc" stroke-width="1"/>`).join('')}
    ${[105, 175, 245, 315, 385].map(x => `<line x1="${x * sx}" x2="${x * sx}" y1="28" y2="${mini ? 202 : 350}" stroke="#eff2f0" stroke-width="1"/>`).join('')}
    <line x1="${72 * sx}" x2="${mini ? 410 : 710}" y1="${310 * sy}" y2="${35 * sy}" stroke="#0b6b57" stroke-width="2" stroke-dasharray="5 5" opacity=".75"/>
    <text x="${mini ? 6 : 12}" y="${mini ? 116 : 180}" transform="rotate(-90 ${mini ? 6 : 12},${mini ? 116 : 180})" fill="#59655f" font-size="${mini ? 10 : 12}">Band gap (eV)</text>
    <text x="${mini ? 173 : 330}" y="${mini ? 228 : 378}" fill="#59655f" font-size="${mini ? 10 : 12}">Formation energy (eV/atom)</text>
    ${dots.map(([name, x, y, color]) => {
      const cx = x * sx; const cy = y * sy;
      return `<g ${interactive ? `class="site-hit" tabindex="0" role="button" aria-label="检查 ${name} 数据点" data-action="inspect:scatter"` : ''}>
        <circle cx="${cx}" cy="${cy}" r="${mini ? 5 : 7}" fill="${color}" stroke="#fff" stroke-width="2"/>
        ${mini ? '' : `<text x="${cx + 10}" y="${cy - 10}" fill="#59655f" font-size="12">${name}</text>`}
      </g>`;
    }).join('')}
  </svg>`;
}

function distributionSvg() {
  return `<svg viewBox="0 0 410 190" role="img" aria-label="band gap 分布图">
    <rect width="410" height="190" fill="#fff"/>
    <line x1="38" x2="390" y1="154" y2="154" stroke="#59655f"/>
    ${[0, 1, 2, 3, 4, 5].map((v,i)=>`<text x="${36+i*66}" y="174" fill="#78837d" font-size="10">${v}</text>`).join('')}
    ${[28,45,76,118,142,160].map((h,i)=>`<rect x="${52+i*50}" y="${154-h}" width="33" height="${h}" fill="${i===3 ? '#0b6b57' : '#a9c7bb'}"/>`).join('')}
    <text x="164" y="187" fill="#59655f" font-size="11">Band gap (eV)</text>
  </svg>`;
}

function structureSvg() {
  const sites = [
    ['Ba', 320, 230, 30, '#86aa61'], ['Ti', 320, 150, 19, '#2d6f8e'], ['O', 235, 145, 14, '#d16045'],
    ['O', 405, 145, 14, '#d16045'], ['O', 320, 74, 14, '#d16045'], ['O', 320, 316, 14, '#d16045'],
    ['O', 235, 304, 14, '#d16045'], ['O', 405, 304, 14, '#d16045'],
  ];
  return `<svg viewBox="0 0 640 430" role="img" aria-label="BaTiO3 钙钛矿晶体结构">
    <rect width="640" height="430" fill="#fbfcfb"/>
    <g stroke="#9eaaa4" stroke-width="2" fill="none" opacity=".75">
      <path d="M170 90 L470 90 L470 340 L170 340 Z M235 42 L535 42 L535 292 L235 292 Z M170 90 L235 42 M470 90 L535 42 M470 340 L535 292 M170 340 L235 292"/>
      <path d="M320 150 L235 145 M320 150 L405 145 M320 150 L320 74 M320 150 L320 316 M320 150 L235 304 M320 150 L405 304"/>
    </g>
    ${sites.map(([name,x,y,r,color])=>`<g class="site-hit" tabindex="0" role="button" aria-label="检查 ${name} 位点" data-action="inspect:site"><circle cx="${x}" cy="${y}" r="${r}" fill="${color}" stroke="#fff" stroke-width="3"/><text x="${x}" y="${y+4}" text-anchor="middle" fill="#fff" font-size="${r>20?15:11}" font-weight="600">${name}</text></g>`).join('')}
  </svg>`;
}

function xrdSvg() {
  const peaks = [[85,120],[122,45],[169,152],[213,65],[266,105],[315,55],[365,84],[420,34],[465,62],[520,24]];
  return `<svg viewBox="0 0 650 370" role="img" aria-label="BaTiO3 XRD 衍射图谱">
    <rect width="650" height="370" fill="#fff"/>
    <line x1="56" x2="610" y1="310" y2="310" stroke="#59655f"/>
    <line x1="56" x2="56" y1="38" y2="310" stroke="#59655f"/>
    ${peaks.map(([x,h])=>`<path d="M${x-11} 310 C${x-5} 310 ${x-3} ${310-h} ${x} ${310-h} C${x+3} ${310-h} ${x+5} 310 ${x+11} 310" fill="none" stroke="#0b6b57" stroke-width="2.5" data-action="inspect:xrd" class="site-hit" tabindex="0" role="button" aria-label="检查衍射峰"/>`).join('')}
    <text x="292" y="348" fill="#59655f" font-size="12">2θ (degree)</text><text x="18" y="210" transform="rotate(-90 18,210)" fill="#59655f" font-size="12">Intensity (a.u.)</text>
  </svg>`;
}

function electronicSvg() {
  const bands = [[54,180,85,110,130,165,190],[58,226,168,150,190,237,219],[100,111,170,197,173,120,104],[286,260,232,188,160,184,240],[315,274,218,208,248,287,320]];
  return `<svg viewBox="0 0 650 390" role="img" aria-label="BaTiO3 电子能带结构">
    <rect width="650" height="390" fill="#fff"/>
    <line x1="52" x2="410" y1="220" y2="220" stroke="#aeb9b3" stroke-dasharray="4 4"/>
    ${[104,164,224,284,344,404].map(x=>`<line x1="${x}" x2="${x}" y1="36" y2="342" stroke="#eff2f0"/>`).join('')}
    ${bands.map(b=>`<polyline points="${b.map((y,i)=>`${54+i*58},${y}`).join(' ')}" fill="none" stroke="#0b6b57" stroke-width="2"/>`).join('')}
    <rect x="466" y="40" width="138" height="300" fill="#f7faf8" stroke="#d9dfdc"/>
    ${[65,90,116,135,149,128,110,94,72].map((w,i)=>`<rect x="${534-w/2}" y="${54+i*29}" width="${w}" height="17" fill="#78a693"/>`).join('')}
    <text x="173" y="372" fill="#59655f" font-size="12">Γ X M Γ R X</text><text x="18" y="210" transform="rotate(-90 18,210)" fill="#59655f" font-size="12">Energy (eV)</text><text x="508" y="372" fill="#59655f" font-size="12">DOS</text>
  </svg>`;
}

function appShell(content, opts = {}) {
  const classes = `app-shell ${opts.workbench ? 'workbench-shell' : ''} ${opts.landing ? 'landing' : ''}`;
  return `<div class="${classes}">${globalBar(opts)}${opts.project ? projectNav(opts.active) : ''}<main id="main-content" class="${opts.mainClass || ''}">${content}</main>${opts.controls === false ? '' : controls()}</div>`;
}

function controls() {
  return `<details class="prototype-controls">
    <summary>原型审阅控件 <span class="tertiary">仅用于设计审阅</span></summary>
    <div class="controls-body">
      <label>页面<select data-control="route">${[
        ['landing','落地页'],['console','控制台'],['projects','项目'],['project','项目概览'],['data','项目数据'],['research','项目研究'],['reports','分析报告'],['report','报告阅读']
      ].map(([v,l])=>`<option value="${v}" ${state.route===v?'selected':''}>${l}</option>`).join('')}</select></label>
      <label>数据 Viewer<select data-control="viewer">${[
        ['table','表格'],['structure','结构'],['trajectory','轨迹'],['xrd','XRD'],['electronic','电子结构'],['volumetric','体数据'],['archive','ZIP / 已检测内容'],['unsupported-file','不支持的文件']
      ].map(([v,l])=>`<option value="${v}" ${state.viewer===v?'selected':''}>${l}</option>`).join('')}</select></label>
      <label>研究状态<select data-control="research">${[
        ['idle','开始前'],['planning','准备方案'],['running-no-result','运行中，暂无结果'],['running-incremental','运行中，已有结果'],['partial','部分完成'],['complete','已完成'],['unsupported','不支持'],['clarification','需要澄清'],['failed','失败']
      ].map(([v,l])=>`<option value="${v}" ${state.research===v?'selected':''}>${l}</option>`).join('')}</select></label>
      <label>登录状态<select data-control="auth"><option value="out" ${state.auth==='out'?'selected':''}>已退出</option><option value="in" ${state.auth==='in'?'selected':''}>已登录</option></select></label>
      <div class="controls-note">隔离演示 · ${CLOSURE_REVISION}。不代表生产能力或认证方案。</div>
    </div>
  </details>`;
}

function landing() {
  const content = `
    <section class="hero">
      <div>
        <p class="eyebrow">材料数据智能</p>
        <h1>让材料数据成为可追溯的研究结论。</h1>
        <p class="hero-copy">导入真实材料数据，提出科学问题，在一个可审计的研究工作台中查看分析、图形、限制与证据。</p>
        <div class="hero-actions">${button(state.auth === 'in' ? '进入控制台' : '开始使用', state.auth === 'in' ? 'go:console' : 'open-login', 'btn primary')}${button('查看研究流程', 'scroll:workflow', 'btn')}</div>
        <div class="trust-line"><span>科学单位可见</span><span>分析过程可解释</span><span>结果有来源</span></div>
      </div>
      <div class="instrument-scene" aria-label="研究工作台预览">
          <div class="scene-bar"><span>Perovskite stability study</span><span>项目研究 / 当前分析</span></div>
        <div class="scene-body">
          <div class="scene-conversation">
            <p class="eyebrow">研究对话</p>
            <div class="scene-message">比较 formation energy 与 band gap，看看哪些化合物值得进一步检查。</div>
            <div class="scene-message assistant">已选定 <strong>materials-table</strong>，使用 8 个钙钛矿样本进行比较。</div>
          </div>
          <div class="scene-work">
            <p class="eyebrow">当前研究</p>
            <div class="evidence-spine">
              <div class="spine-step done"><span class="spine-node">✓</span><span>已确定分析数据</span></div>
              <div class="spine-step done"><span class="spine-node">✓</span><span>分析方案已准备</span></div>
              <div class="spine-step active"><span class="spine-node"></span><span>比较 formation energy 与 band gap</span></div>
              <div class="spine-step"><span class="spine-node"></span><span>生成统计摘要</span></div>
            </div>
            <div class="scene-plot"><strong>Formation energy 与 band gap</strong>${plotSvg({mini:true})}</div>
          </div>
        </div>
      </div>
    </section>
    <section id="workflow" class="landing-band"><div class="page-container">
      <div class="section-header"><div><p class="eyebrow">研究流程</p><h2>从数据到可回查的科学结果</h2></div><p>技术细节在需要时展开。</p></div>
      <div class="workflow-line">
      ${[['01','建立项目','持续保存相关数据、研究问题与结果。'],['02','理解数据','在专业查看器中确认结构、列、单位与样本。'],['03','开展研究','以自然语言提出问题，查看可理解的分析方案。'],['04','阅读结果','以图、发现、局限性与依据组织输出。']].map(([n,t,d])=>`<article class="workflow-item"><span class="workflow-number">${n}</span><h3>${t}</h3><p>${d}</p></article>`).join('')}
      </div>
      <div class="landing-proof"><div><p class="eyebrow">为材料研究而设计</p><h2>不是一个通用智能体控制台。</h2><p class="lead">主工作区为真实科学对象保留空间。结构、轨迹、谱图和表格各自以合适的查看器呈现；对话不夺走数据和结果的焦点。</p></div><figure class="publication-figure"><strong>以图为中心的结果</strong>${distributionSvg()}<figcaption class="figure-caption">图、单位、结论和限制构成一个可阅读、可复核的研究结果，而非一组仪表盘指标。</figcaption></figure></div>
    </div></section>`;
  return appShell(content, { landing: true });
}

function consolePage() {
  const content = `<div class="page"><div class="page-container">
    <section class="console-hero"><div><p class="eyebrow">控制台</p><h1>继续你的材料研究。</h1><p class="lead">从项目进入数据、研究与已有分析报告。当前工作保持在科学问题的语境里。</p></div><div class="summary-facts"><div class="fact-row"><dt>进行中的项目</dt><dd>3</dd></div><div class="fact-row"><dt>本周研究运行</dt><dd>6</dd></div><div class="fact-row"><dt>可阅读报告</dt><dd>4</dd></div></div></section>
    <section class="resume-strip"><span class="resume-label">继续研究</span><div class="resume-main"><strong>Perovskite stability study</strong><span class="muted">形成能与带隙关系 · 已产生初步结果图</span></div><div>${button('查看相关数据', 'preview:table', 'btn small')}${button('打开研究', 'go:research', 'btn primary')}</div></section>
    <section style="margin-top:48px"><div class="section-header"><div><p class="eyebrow">近期项目</p><h2>继续已有研究</h2></div>${button('查看全部项目', 'go:projects', 'btn')}</div><div class="recent-grid">
      ${projectCards().join('')}
    </div></section>
  </div></div>`;
  return appShell(content);
}

function projectCards() {
  return [
    ['Perovskite stability study','8 个组成 · 1 组结构 · 2 份报告','最近研究：形成能与带隙','project'],
    ['AIMD ionic transport','516 个原子 · 200 帧 · 轨迹','最近研究：MSD 与扩散行为','data'],
    ['Thin-film XRD comparison','12 条谱图 · 4 个样本条件','最近研究：峰位与相组成','research'],
  ].map(([title,desc,latest,route])=>`<article class="project-row"><h3><a class="data-link" href="#${route}" data-route="${route}">${title}</a></h3><p>${desc}</p><div class="project-meta"><span>${latest}</span><span>更新于 2 小时前</span></div></article>`);
}

function projectsPage() {
  const content = `<div class="page"><div class="page-container"><div class="section-header"><div><p class="eyebrow">项目</p><h1>材料研究项目</h1><p class="lead">每个项目维护一组相关数据、研究对话、运行结果和分析报告。</p></div>${button('新建项目', 'noop', 'btn primary')}</div><section class="recent-grid">${projectCards().join('')}</section><section class="hairline-section" style="margin-top:44px"><div class="section-header"><div><p class="eyebrow">归档</p><h2>已归档研究</h2></div><button class="btn" type="button">浏览归档</button></div><p class="muted">归档项目与当前活动研究分开，避免仪表盘式信息噪声。</p></section></div></div>`;
  return appShell(content);
}

function projectOverview() {
  const content = `<div class="project-page"><div class="page-container">
    <section class="project-summary"><div><p class="eyebrow">项目概览</p><h1>Perovskite stability study</h1><p class="lead">比较 A-site / B-site 取代钙钛矿的形成能、带隙与密度，识别需要进一步计算和实验验证的候选材料。</p></div><dl class="summary-facts"><div class="fact-row"><dt>数据</dt><dd><a href="#data" data-route="data" class="data-link">3 个数据集</a></dd></div><div class="fact-row"><dt>最近运行</dt><dd>今天 10:42</dd></div><div class="fact-row"><dt>分析报告</dt><dd><a href="#reports" data-route="reports" class="data-link">2 份可读</a></dd></div></dl></section>
    <section class="overview-columns"><div><p class="eyebrow">研究动态</p><h2>研究进展</h2><div class="activity-list">
      <div class="activity-row"><time>今天 10:42</time><div><strong>形成能与带隙的关系</strong><p class="muted">生成散点图、分布与限制说明。</p></div><span class="status-text ready">已完成</span></div>
      <div class="activity-row"><time>昨天 16:18</time><div><strong>BaTiO3 结构检查</strong><p class="muted">检查晶胞、Wyckoff 位点与局部配位。</p></div><span class="status-text ready">已完成</span></div>
      <div class="activity-row"><time>周一 09:15</time><div><strong>导入 materials-table</strong><p class="muted">识别化学式、形成能、带隙与密度。</p></div><span class="status-text ready">可用</span></div>
    </div></div><div><p class="eyebrow">项目数据</p><h2>数据上下文</h2><div class="mini-file-list">
      <div class="mini-file"><div><strong><a href="#data" data-route="data" class="data-link">materials-table.csv</a></strong><span>8 行 · 材料属性表</span></div>${button('查看', 'go:data', 'btn small')}</div>
      <div class="mini-file"><div><strong><button class="data-link" data-action="preview:trajectory">aimd-trajectory.xyz</button></strong><span>516 个原子 · 200 帧</span></div>${button('快速查看', 'preview:trajectory', 'btn small')}</div>
      <div class="mini-file"><div><strong><a href="#data" data-route="data" class="data-link">perovskite-calculations.zip</a></strong><span>已检测科学内容</span></div>${button('查看', 'go:data', 'btn small')}</div>
    </div></div></section>
  </div></div>`;
  return appShell(content, { project: true, active: 'project' });
}

function dataNavigator() {
  const items = [
    ['table','▦','materials-table.csv','8 个材料 · 属性'],['structure','◇','BaTiO3.cif','结构 · 5 个原子'],['trajectory','≋','aimd-trajectory.xyz','516 个原子 · 200 帧'],['xrd','⌁','thin-film.xrd','1 条衍射图谱'],['electronic','∿','BaTiO3-electronic.json','能带与 DOS'],['volumetric','▧','charge-density.cube','体数据场'],['archive','▣','perovskite-calculations.zip','4 个已检测资源'],['unsupported-file','?','instrument-notes.dat','不支持的文件'],
  ];
  return `<aside class="data-navigator" aria-label="项目数据导航器"><div class="navigator-head"><input class="search-field" aria-label="搜索数据" placeholder="搜索数据与属性" /></div><div class="navigator-section"><div class="navigator-label">项目数据</div>${items.map(([id,g,name,meta])=>`<button class="tree-item ${state.viewer===id?'active':''}" type="button" data-action="viewer:${id}"><span class="file-glyph">${g}</span><span class="tree-text"><strong>${name}</strong><span>${meta}</span></span></button>`).join('')}</div></aside>`;
}

function inspector() {
  if (!state.inspector) return '';
  const content = state.inspector === 'site' ? {
    title: 'Ti 位点', facts: [['元素','Ti'],['分数坐标','0.500, 0.500, 0.500'],['配位','O6 八面体'],['局部对称','m-3m']], evidence: 'BaTiO3.cif / 结构资源 / 位点 5', source: '结构视图选中项'
  } : state.inspector === 'xrd' ? {
    title: '衍射峰 32.1°', facts: [['2θ','32.1°'],['相对强度','100 a.u.'],['候选晶面','(110)'],['样本','Thin film A']], evidence: 'thin-film.xrd / 峰位 32.1°', source: 'XRD 视图选中项'
  } : {
    title: 'BaTiO3', facts: [['形成能','−3.41 eV/atom'],['带隙','3.20 eV'],['密度','6.02 g/cm³'],['晶体结构','立方钙钛矿']], evidence: 'materials-table.csv / 第 1 行', source: '表格或散点图选中项'
  };
  return `<aside class="inspector" aria-label="选中对象详情"><div class="inspector-head"><strong>详情</strong>${button('×', 'close-inspector', 'icon-btn', '关闭详情')}</div>
    <section class="inspector-section"><h3>${content.title}</h3><dl class="property-list">${content.facts.map(([k,v])=>`<div><dt>${k}</dt><dd>${v}</dd></div>`).join('')}</dl></section>
    <section class="inspector-section"><h3>依据</h3><p class="muted">当前对象由已选数据中的一个具体样本或结构位点定位。</p><p class="technical">${content.evidence}</p></section>
    <section class="inspector-section"><button class="disclosure" type="button" data-action="toggle-lineage">来源与过程 <span>⌄</span></button><div class="lineage">${content.source}<br />已识别科学资源<br />数据范围：当前选中数据</div></section>
  </aside>`;
}

function tableViewer() {
  return `<section class="table-view"><div class="data-tools"><input placeholder="搜索化学式或属性" aria-label="搜索数据表" /><button class="btn small" type="button">筛选</button><button class="btn small" type="button">列</button><span class="tertiary">单位随属性显示</span></div><div class="table-scroll"><table class="scientific-table"><thead><tr><th>化学式</th><th>形成能<span class="unit">eV/atom</span></th><th>带隙<span class="unit">eV</span></th><th>密度<span class="unit">g/cm³</span></th><th>结构</th></tr></thead><tbody>${materials.map((m,i)=>`<tr class="${i===0?'selected':''}" tabindex="0" role="button" data-action="inspect:table"><td><strong>${m[0]}</strong></td><td>${m[1].toFixed(2)}</td><td>${m[2].toFixed(2)}</td><td>${m[3].toFixed(2)}</td><td>${m[4]}</td></tr>`).join('')}</tbody></table></div><div class="table-status"><span>8 / 8 个样本 · materials-table.csv</span><span>已选中 BaTiO3</span></div></section>`;
}

function structureViewer() {
  return `<section class="scientific-canvas"><div class="canvas-stage">${structureSvg()}<div class="canvas-overlay"><strong>BaTiO3 · 立方钙钛矿</strong><span>选择原子位点查看局部科学上下文。</span></div></div><div class="canvas-footer"><span>晶胞：a = 4.01 Å · 5 个原子</span><span class="legend"><span style="--legend:#86aa61">Ba</span><span style="--legend:#2d6f8e">Ti</span><span style="--legend:#d16045">O</span></span></div></section>`;
}

function trajectoryViewer() {
  return `<section class="scientific-canvas"><div class="canvas-stage">${structureSvg()}<div class="canvas-overlay"><strong>AIMD 轨迹 · 第 084 / 200 帧</strong><span>516 个原子 · 300 K · 1 fs 步长</span></div></div><div class="canvas-footer"><span>当前帧：离子位置与局部配位变化</span><div>${button('‹', 'noop', 'icon-btn', '上一帧')}${button('▶', 'noop', 'icon-btn', '播放轨迹')}${button('›', 'noop', 'icon-btn', '下一帧')}</div></div></section>`;
}

function xrdViewer() { return `<section class="plot-view"><div class="plot-view-header"><div><p class="eyebrow">实验 XRD</p><h2>薄膜样本 A</h2></div></div><div class="plot-frame">${xrdSvg()}</div><p class="plot-note">选择峰位可在详情中查看对应数据来源。</p></section>`; }
function electronicViewer() { return `<section class="plot-view"><div class="plot-view-header"><div><p class="eyebrow">电子结构</p><h2>BaTiO3 · 能带与 DOS</h2></div><span class="status-text ready">已解析</span></div><div class="plot-frame">${electronicSvg()}</div><p class="plot-note">能带与 DOS 是同一科学资源的协同视图。</p></section>`; }
function volumetricViewer() { return `<section class="scientific-canvas"><div class="canvas-stage heatmap"><div class="canvas-overlay"><strong>电荷密度</strong><span>0.02 e/Å³ 等值面切片</span></div><div class="volume-bar" aria-label="体数据色阶"></div></div><div class="canvas-footer"><span>体数据场 · BaTiO3</span><span>色阶表达数值，不承担品牌装饰</span></div></section>`; }
function archiveViewer() { return `<section class="archive-view"><p class="eyebrow">已检测内容</p><h2>perovskite-calculations.zip</h2><p class="lead">压缩包中检测到多个候选科学资源。下方只显示当前已识别、可单独查看的内容。</p><div class="notice">资源之间的关联会在实际研究范围确定后说明。</div><div class="detected-list">${[['structure/CONTCAR','结构','可查看'],['electronic/vasprun.xml','电子能带与 DOS','可查看'],['analysis/formation.csv','表格属性','可查看'],['charge/CHGCAR','体数据场','需要进一步解析']].map(([f,t,s])=>`<div class="detected-row"><div><strong>${f}</strong><span>${t}</span></div><span class="status-text ${s==='可查看'?'ready':'warning'}">${s}</span><button class="btn small" type="button" data-action="viewer:${t==='结构'?'structure':t.includes('电子')?'electronic':t.includes('表格')?'table':'volumetric'}">查看</button></div>`).join('')}</div></section>`; }
function unsupportedFileViewer() { return `<section class="unsupported-file"><div class="state-symbol">?</div><p class="eyebrow">不支持的文件</p><h2>当前无法将 instrument-notes.dat 解析为科学数据。</h2><p class="lead">文件仍保留在项目数据中，但尚未识别到可用于查看或分析的结构化内容。</p><div class="notice">保留原始文件；获得格式说明后可再次尝试。</div></section>`; }

function dataPage() {
  const names = {table:'materials-table.csv',structure:'BaTiO3.cif',trajectory:'aimd-trajectory.xyz',xrd:'thin-film.xrd',electronic:'BaTiO3-electronic.json',volumetric:'charge-density.cube',archive:'perovskite-calculations.zip','unsupported-file':'instrument-notes.dat'};
  const viewerMap = {table:tableViewer,structure:structureViewer,trajectory:trajectoryViewer,xrd:xrdViewer,electronic:electronicViewer,volumetric:volumetricViewer,archive:archiveViewer,'unsupported-file':unsupportedFileViewer};
  const meta = state.viewer === 'table' ? '8 个样本 · 4 个属性' : state.viewer === 'structure' ? '5 个原子 · 1 个结构' : state.viewer === 'archive' ? '4 个已检测资源' : '项目数据';
  const content = `<div class="workbench-page">${dataNavigator()}<section class="viewer-shell"><div class="viewer-toolbar"><div class="viewer-title"><strong>${names[state.viewer]}</strong><span>${meta}</span></div><div class="toolbar-actions">${button('研究此数据', 'go:research', 'btn small')}${button('⋯', 'noop', 'icon-btn', '更多操作')}</div></div><div class="viewer-body ${state.inspector?'inspector-open':''}"><div class="viewer-main">${viewerMap[state.viewer]()}</div>${inspector()}</div></section></div>`;
  return appShell(content, { project: true, active: 'data', workbench: true });
}

function conversation(stateName) {
  const question = stateName === 'unsupported' ? '请找出预测误差最大的样本。' : '比较 formation energy 与 band gap，哪些候选材料值得进一步检查？';
  const assistant = stateName === 'unsupported' ? '我检查了当前数据。它包含 formation energy、band gap 与 density，但没有真实值和预测值列。' : '我会使用 materials-table 中的 8 个钙钛矿样本，先比较 formation energy 与 band gap，再给出分布与适用范围。';
  return `<aside class="conversation-pane"><div class="pane-head"><strong>研究对话</strong><button class="icon-btn" type="button" title="对话选项" aria-label="对话选项">⋯</button></div><div class="conversation-scroll"><div class="message user"><div class="message-role">你</div><p>${question}</p></div><div class="message assistant"><div class="message-role">研究助手</div><p>${assistant}</p>${stateName==='unsupported' ? '<p class="muted">我可以帮助你改为查看当前数据真正支持的关系。</p>' : '<p class="muted">分析会保留单位、数据范围和方法限制。</p>'}</div>${stateName==='clarification'?'<div class="message assistant"><div class="message-role">研究助手</div><p>你希望比较全部 8 个样本，还是只看 Ti-based 钙钛矿？这个选择会改变解释范围。</p></div>':''}${stateName==='failed'?'<div class="message assistant"><div class="message-role">研究助手</div><p>计算没有完成。已生成的结果仍会保留；我会说明未完成的部分和可恢复操作。</p></div>':''}</div><div class="composer"><div class="composer-box"><textarea aria-label="向此项目提问" placeholder="询问此项目中的数据…"></textarea>${button('发送', 'noop', 'btn primary')}</div><div class="composer-meta"><span>当前项目：Perovskite stability study</span></div></div></aside>`;
}

function stepsFor(stateName) {
  const base = [
    ['done','✓','已确定分析数据','materials-table · 8 个样本'],['done','✓','分析方案已准备','相关性比较与分布'],['done','✓','数据已加载','形成能、带隙、密度'],
  ];
  if (stateName === 'idle') return [['active','','等待研究问题','从项目数据开始']];
  if (stateName === 'planning') return [['done','✓','已理解问题','formation energy 与 band gap'],['active','','正在准备分析方案','确认数据范围与方法'],['','', '等待确认','不会创建运行']];
  if (stateName === 'unsupported') return [['done','✓','已检查数据要求','没有真实值与预测值列'],['failed','!','无法进行预测误差分析','没有创建分析运行']];
  if (stateName === 'clarification') return [['done','✓','已理解问题','需要缩小科学范围'],['active','','等待你的澄清','选择 Ti-based 或全部样本']];
  if (stateName === 'failed') return [...base,['done','✓','相关性分析已完成','散点图已保存'],['failed','!','统计摘要未完成','可重试此科学步骤']];
  if (stateName === 'running-no-result') return [...base,['active','','比较 formation energy 与 band gap','当前工具仍在执行'],['','','生成统计摘要','等待前一步结果']];
  if (stateName === 'running-incremental') return [...base,['done','✓','相关性分析已完成','散点图已可读取'],['active','','生成统计摘要','当前科学计算仍在进行'],['','','解释结果','将在分析完成后基于全部结果生成']];
  if (stateName === 'partial') return [...base,['done','✓','相关性分析已完成','散点图已可读取'],['failed','!','分布拟合未完成','保留已完成结果'],['','','解释结果','仅解释有依据的部分']];
  return [...base,['done','✓','相关性分析已完成','散点图与分布'],['done','✓','生成统计摘要','已保存辅助输出'],['done','✓','解释结果','包含限制']];
}

function activityPane(stateName) {
  const steps = `<div class="step-list">${stepsFor(stateName).map(([kind,mark,title,detail])=>`<div class="run-step ${kind}"><span class="step-node">${mark}</span><span>${title}${kind==='active'?'<span class="activity-pulse" aria-label="当前活动"><i></i><i></i><i></i></span>':''}<small>${detail}</small></span></div>`).join('')}</div>`;
  if (stateName === 'complete') return `<section class="activity-pane activity-complete"><div class="completion-summary"><span class="completion-check">✓</span><strong>分析完成</strong><span>· 4 个步骤</span><details><summary>查看分析过程</summary>${steps}</details></div></section>`;
  return `<aside class="activity-pane"><p class="eyebrow">分析过程</p><h3>${stateName==='unsupported'?'数据要求检查':stateName==='idle'?'开始研究':stateName==='planning'?'分析方案':'研究运行'}</h3>${steps}</aside>`;
}

function resultDocument({ partial = false } = {}) {
  return `<article class="result-document"><p class="result-kicker">科学结果</p><h1>形成能与带隙呈现弱负相关</h1><div class="result-context"><span>materials-table · 8 个组成</span><span>形成能：eV/atom</span><span>带隙：eV</span></div><figure class="result-figure"><div class="figure-frame">${plotSvg({interactive:true})}</div><figcaption class="figure-caption"><strong>图 1。</strong>在当前 8 个钙钛矿样本中，较低 formation energy 的候选并不系统性对应较大的 band gap。虚线仅表达此小样本中的线性趋势，不表示因果关系。</figcaption></figure><section class="finding-block"><div class="finding-label">主要发现</div><p>BaTiO3 与 SrTiO3 具有较低 formation energy 且 band gap 约为 3.2 eV；Zr-based 候选具有更大的 band gap，但当前数据不足以把这种关系解释为稳定性驱动。</p></section><section class="limitation-block"><h3>限制</h3><p>样本量为 8，且组成家族有限。这里的关系不能外推为全部钙钛矿的可预测规律；没有不确定性、实验条件或合成可行性字段。</p></section><div class="supporting-grid"><figure class="supporting-figure"><h3>带隙分布</h3>${distributionSvg()}<figcaption class="figure-caption">4 个样本位于 3.0–3.5 eV 区间。</figcaption></figure><div class="supporting-figure"><h3>样本表</h3><table class="scientific-table" style="min-width:0"><thead><tr><th>化学式</th><th>带隙<span class="unit">eV</span></th></tr></thead><tbody>${materials.slice(0,4).map(m=>`<tr><td>${m[0]}</td><td>${m[2].toFixed(2)}</td></tr>`).join('')}</tbody></table></div></div><div class="method-evidence"><section><p class="eyebrow">分析方法</p><h3>比较属性关系</h3><p class="muted">比较当前数据表中的 formation_energy 与 band_gap，并保留图、数值单位和输入范围。</p></section><section><p class="eyebrow">数据依据</p><h3>来源与过程</h3><p class="muted">从图或样本选择打开详情，即可查看具体数据行和输入数据资源。</p>${button('打开 BaTiO3 详情', 'inspect:scatter', 'btn small')}</section></div>${partial?'<div class="notice" style="margin-top:28px">分布拟合未完成；以上只保留已经完成且可读取的相关性分析结果。</div>':''}</article>`;
}

function workbenchContent(stateName) {
  if (stateName === 'idle') return `<section class="workbench-empty"><div><p class="eyebrow">项目研究</p><h2>从一个科学问题开始。</h2><p class="lead">当前项目包含材料属性表、BaTiO3 结构、AIMD 轨迹和已检测的计算压缩包。研究助手会在分析前说明所选数据与科学方法。</p><div class="scope-list"><span class="scope-chip">materials-table</span><span class="scope-chip">BaTiO3 结构</span><span class="scope-chip">AIMD 轨迹</span></div>${button('查看项目数据', 'go:data', 'btn')}</div></section>`;
  if (stateName === 'planning') return `<section class="live-results"><article class="plan-sheet"><div class="plan-header"><div><p class="eyebrow">分析方案</p><h2>比较 formation energy 与 band gap</h2><p class="muted">先确认所选数据、科学步骤和结果范围。</p></div><span class="status-text">等待确认</span></div><div class="plan-steps"><div class="plan-step"><div><h3>选择分析数据</h3><p>使用 materials-table 中具有 formation energy 和 band gap 的 8 个样本。</p></div></div><div class="plan-step"><div><h3>比较属性关系</h3><p>绘制散点图并计算描述性关系，用于识别候选分布而非得出因果结论。</p></div></div><div class="plan-step"><div><h3>生成可读结果</h3><p>输出主要图、说明、主要发现、限制与对应数据依据。</p></div></div></div><div class="method-note">限制：数据不包含实验条件、预测不确定性或合成可行性。</div></article></section>`;
  if (stateName === 'unsupported') return `<section class="live-results"><article class="unsupported-state"><div class="state-symbol">!</div><p class="eyebrow">无法进行预测误差分析</p><h1>当前数据没有真实值和预测值列。</h1><p class="lead">因此不能计算预测误差。这里会说明缺少什么，并保留当前数据真正支持的研究方向。</p><div class="available-list"><strong>当前可用</strong><span>形成能</span><span>带隙</span><span>密度</span></div><p class="muted">可以尝试：</p><div class="suggestions"><button class="suggestion" type="button" data-action="set-research:complete">查看带隙分布</button><button class="suggestion" type="button" data-action="set-research:complete">比较形成能与密度</button></div><details style="margin-top:28px"><summary>技术详情</summary><p class="technical">需要同时包含真实值与预测值。当前数据未提供。</p></details></article></section>`;
  if (stateName === 'clarification') return `<section class="live-results"><article class="clarification-state"><p class="eyebrow">需要澄清</p><h1>先确定要比较的数据范围。</h1><p class="lead">当前项目中包括 Ti-based 与 Zr-based 钙钛矿。两类样本放在一起会改变解释边界。</p><div class="suggestions"><button class="suggestion" type="button" data-action="set-research:planning">全部 8 个样本</button><button class="suggestion" type="button" data-action="set-research:planning">只比较 Ti-based 钙钛矿</button></div></article></section>`;
  if (stateName === 'failed') return `<section class="live-results"><article class="failed-state"><div class="state-symbol">×</div><p class="eyebrow">部分分析未完成</p><h1>统计摘要没有完成，但相关性散点图已保留。</h1><p class="lead">可以先阅读已完成的证据，或者仅重试未完成的科学步骤。输入数据和已完成结果都会保持可用。</p>${button('重试统计摘要', 'set-research:running-incremental', 'btn primary')}<div style="margin-top:36px">${resultDocument({partial:true})}</div></article></section>`;
  if (stateName === 'running-no-result') return `<section class="live-results"><article class="workbench-empty"><div><p class="eyebrow">正在执行科学分析</p><h2>比较 formation energy 与 band gap</h2><p class="lead">当前还没有可以呈现的图或表格。这里仅显示已确认的分析步骤。</p><p class="muted">完成第一个科学计算后，结果会出现在这里。</p></div></article></section>`;
  if (stateName === 'running-incremental') return `<section class="live-results"><article class="result-document"><p class="result-kicker">当前结果</p><h2>相关性分析已可读取</h2><p class="muted">下一步“生成统计摘要”仍在执行。这个散点图来自已经完成的相关性分析。</p><figure class="result-figure"><div class="figure-frame">${plotSvg({interactive:true})}</div><figcaption class="figure-caption"><strong>当前结果。</strong>formation energy 与 band gap，8 个样本。完整解释将在本次分析完成后基于所有结果生成。</figcaption></figure><div class="method-note">分析仍在继续；这里只显示已确认的科学步骤状态。</div></article></section>`;
  return `<section class="live-results">${resultDocument({partial:stateName==='partial'})}</section>`;
}

function researchPage() {
  const content = `<div class="research-page" style="--conversation:${state.conversationWidth}%">${conversation(state.research)}<div class="resize-handle" role="separator" aria-label="调整对话宽度" tabindex="0"></div><section class="dynamic-workbench"><div class="workbench-head"><div class="context"><strong>${state.research==='complete'?'形成能与带隙的关系':state.research==='unsupported'?'数据要求检查':'当前研究工作'}</strong><span>Perovskite stability study</span></div><div>${button('查看数据', 'preview:table', 'btn small')}${button('ⓘ', 'inspect:scatter', 'icon-btn', '打开详情')}</div></div><div class="run-layout ${state.research==='complete'?'complete':''}">${activityPane(state.research)}${workbenchContent(state.research)}</div></section></div>`;
  return appShell(content, { project: true, active: 'research', workbench: true });
}

function reportsPage() {
  const content = `<div class="project-page"><div class="page-container"><div class="section-header"><div><p class="eyebrow">分析报告</p><h1>项目报告</h1><p class="lead">每份报告对应一次研究运行，保留当时的数据范围、结果和方法说明。</p></div></div><section class="report-list">${[
    ['形成能与带隙的关系','8 个钙钛矿组成 · 今天完成','今天 10:42'],['BaTiO3 结构上下文','BaTiO3.cif · 昨天完成','昨天 16:18'],['AIMD 离子传输摘要','轨迹检查 · 8 月 12 日完成','8 月 12 日'],
  ].map(([t,d,date])=>`<article class="report-row"><div><h3><a href="#report" data-route="report" class="data-link">${t}</a></h3><p>${d}</p></div><span class="status-text ready">可阅读</span><span class="tertiary">${date}</span></article>`).join('')}</section></div></div>`;
  return appShell(content, { project: true, active: 'reports' });
}

function reportPage() {
  const content = `<article class="report-reader"><header><p class="eyebrow">分析报告 · Perovskite stability study</p><h1>形成能与带隙的关系</h1><div class="report-byline"><span>8 个组成</span><span>materials-table</span><span>今天 10:42 完成</span></div></header><section class="report-section"><h2>摘要</h2><p>当前 8 个钙钛矿样本显示 formation energy 与 band gap 之间存在弱负相关。BaTiO3 和 SrTiO3 处于低 formation energy、约 3.2 eV band gap 的区域；该模式仅支持作为当前数据范围内的候选筛选线索。</p></section><section class="report-section"><h2>主要结果</h2><figure class="result-figure"><div class="figure-frame">${plotSvg()}</div><figcaption class="figure-caption"><strong>图 1。</strong>Formation energy（eV/atom）与 band gap（eV）的关系。</figcaption></figure></section><section class="report-section"><h2>限制</h2><p>没有实验条件、误差或合成可行性字段；样本量为 8，限制了外推能力。报告保留运行范围与原始输入的可追溯入口。</p></section><section class="report-section"><h2>来源与过程</h2><p class="technical">materials-table.csv · 8 个选中样本 · 相关性比较结果 · 分析完成后的解释</p></section></article>`;
  return appShell(content, { project: true, active: 'reports' });
}

function preview() {
  if (!state.preview) return '';
  const p = state.preview;
  const content = p === 'structure' ? structureViewer() : p === 'table' ? tableViewer() : p === 'xrd' ? xrdViewer() : p === 'electronic' ? electronicViewer() : p === 'volumetric' ? volumetricViewer() : trajectoryViewer();
  const title = {table:'materials-table.csv',structure:'BaTiO3.cif',trajectory:'aimd-trajectory.xyz',xrd:'thin-film.xrd',electronic:'BaTiO3-electronic.json',volumetric:'charge-density.cube'}[p] || '数据预览';
  return `<div class="quick-preview-backdrop" data-action="close-preview"></div><aside class="quick-preview" aria-modal="true" role="dialog" aria-label="数据快速查看"><div class="preview-head"><div><strong>${title}</strong><span class="tertiary"> · 项目数据快速查看</span></div>${button('×', 'close-preview', 'icon-btn', '关闭快速查看')}</div><div class="preview-stage">${content}</div></aside>`;
}

function loginModal() {
  if (!state.loginOpen) return '';
  return `<div class="modal-backdrop" data-action="close-login"></div><section class="login-modal" role="dialog" aria-modal="true" aria-labelledby="login-title"><div class="modal-head"><div><p class="eyebrow">材料智能体平台</p><h2 id="login-title">登录</h2></div>${button('×', 'close-login', 'icon-btn', '关闭登录')}</div><p class="muted">使用已获授权的账户进入控制台。</p><form class="login-form" data-login-form><label>邮箱<input id="login-email" type="email" autocomplete="email" placeholder="name@example.com" /></label><label>密码<input type="password" autocomplete="current-password" placeholder="输入密码" /></label>${button('登录', 'complete-login', 'btn primary')}</form></section>`;
}

function render() {
  const pages = {landing,console:consolePage,projects:projectsPage,project:projectOverview,data:dataPage,research:researchPage,reports:reportsPage,report:reportPage};
  app.innerHTML = (pages[state.route] || landing)() + preview() + loginModal();
  bind();
  if (state.loginOpen) requestAnimationFrame(() => document.querySelector('#login-email')?.focus());
}

function bind() {
  app.querySelectorAll('[data-route]').forEach(el => el.addEventListener('click', event => { event.preventDefault(); go(el.dataset.route); }));
  app.querySelectorAll('[data-action]').forEach(el => el.addEventListener('click', event => handleAction(event, el.dataset.action)));
  app.querySelectorAll('[role="button"][data-action]').forEach(el => el.addEventListener('keydown', event => {
    if (event.key !== 'Enter' && event.key !== ' ') return;
    event.preventDefault();
    handleAction(event, el.dataset.action);
  }));
  app.querySelectorAll('[data-control]').forEach(el => el.addEventListener('change', event => {
    const { control } = event.target.dataset;
    state[control] = event.target.value;
    if (control === 'route') location.hash = state.route;
    render();
  }));
  const handle = app.querySelector('.resize-handle');
  if (handle) bindResize(handle);
}

function handleAction(event, action) {
  if (action.startsWith('go:')) return go(action.slice(3));
  if (action.startsWith('viewer:')) { state.viewer = action.slice(7); state.route = 'data'; return render(); }
  if (action.startsWith('set-research:')) { state.research = action.slice(13); state.route = 'research'; return render(); }
  if (action.startsWith('inspect:')) { state.restoreFocusAction = action; state.inspector = action.slice(8); return render(); }
  if (action.startsWith('preview:')) { state.restoreFocusAction = action; state.preview = action.slice(8); document.body.style.overflow = 'hidden'; return render(); }
  if (action === 'open-login') { state.restoreFocusAction = action; state.loginOpen = true; document.body.style.overflow = 'hidden'; return render(); }
  if (action === 'close-login') { state.loginOpen = false; document.body.style.overflow = ''; return renderAndRestoreFocus(); }
  if (action === 'complete-login') { event.preventDefault(); state.auth = 'in'; state.loginOpen = false; document.body.style.overflow = ''; return renderAndRestoreFocus(); }
  if (action === 'close-preview') { state.preview = null; document.body.style.overflow = ''; return renderAndRestoreFocus(); }
  if (action === 'close-inspector') { state.inspector = null; return renderAndRestoreFocus(); }
  if (action === 'scroll:workflow') { document.querySelector('#workflow')?.scrollIntoView({ behavior: 'smooth' }); return; }
  event.preventDefault();
}

function renderAndRestoreFocus() {
  const action = state.restoreFocusAction;
  render();
  requestAnimationFrame(() => {
    const target = action ? document.querySelector(`[data-action="${action}"]`) : null;
    target?.focus();
    state.restoreFocusAction = null;
  });
}

function bindResize(handle) {
  let pointerId = null;
  const move = event => {
    if (event.pointerId !== pointerId) return;
    const page = document.querySelector('.research-page');
    if (!page) return;
    const bounds = page.getBoundingClientRect();
    state.conversationWidth = Math.min(45, Math.max(30, ((event.clientX - bounds.left) / bounds.width) * 100));
    page.style.setProperty('--conversation', `${state.conversationWidth}%`);
  };
  handle.addEventListener('pointerdown', event => { pointerId = event.pointerId; handle.setPointerCapture(pointerId); });
  handle.addEventListener('pointermove', move);
  handle.addEventListener('pointerup', event => { if (event.pointerId === pointerId) pointerId = null; });
  handle.addEventListener('keydown', event => {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    state.conversationWidth = Math.min(45, Math.max(30, state.conversationWidth + (event.key === 'ArrowRight' ? 1 : -1)));
    document.querySelector('.research-page')?.style.setProperty('--conversation', `${state.conversationWidth}%`);
  });
}

window.addEventListener('hashchange', () => { state.route = location.hash.replace('#','') || 'landing'; state.inspector = null; state.preview = null; document.body.style.overflow = ''; render(); });
window.addEventListener('keydown', event => {
  if (state.loginOpen && event.key === 'Tab') {
    const focusable = [...document.querySelectorAll('.login-modal button, .login-modal input')].filter(node => !node.disabled);
    const current = focusable.indexOf(document.activeElement);
    if (event.shiftKey && current === 0) { event.preventDefault(); focusable.at(-1)?.focus(); }
    if (!event.shiftKey && current === focusable.length - 1) { event.preventDefault(); focusable[0]?.focus(); }
  }
  if (event.key === 'Escape' && state.loginOpen) { state.loginOpen = false; document.body.style.overflow = ''; return renderAndRestoreFocus(); }
  if (event.key === 'Escape' && (state.preview || state.inspector)) { state.preview = null; state.inspector = null; document.body.style.overflow = ''; renderAndRestoreFocus(); }
});
render();
