/* ──────────────────────────────────────────────
   Report generation: PDF (print) and TXT
   ────────────────────────────────────────────── */

function downloadAsTXT() {
    closeModal('downloadModal');
    window.open(API + '/api/report/' + SESSION_ID, '_blank');
}

async function downloadAsPDF() {
    closeModal('downloadModal');

    // Collect all data
    const moodLog = JSON.parse(localStorage.getItem('moodLog') || '[]');
    const sleepLog = JSON.parse(localStorage.getItem('sleepLog') || '[]');
    const activities = JSON.parse(localStorage.getItem('activities') || '[]');
    const phqHist = JSON.parse(localStorage.getItem('phqHistory') || '[]');
    const gadHist = JSON.parse(localStorage.getItem('gadHistory') || '[]');

    let thoughts = [];
    try {
        const res = await fetch(API + '/api/thoughts/' + SESSION_ID).then(r => r.json());
        thoughts = res.thought_records || [];
    } catch (_) { }

    // Stats
    const avgMood = moodLog.length
        ? (moodLog.slice(-14).reduce((a, e) => a + e.score, 0) / Math.min(moodLog.length, 14)).toFixed(1)
        : null;
    const avgSleep = sleepLog.length
        ? (sleepLog.slice(-7).reduce((a, e) => a + parseFloat(e.durHrs || e.hours || 0), 0) / Math.min(sleepLog.length, 7)).toFixed(1)
        : null;
    const doneActs = activities.filter(a => a.done).length;
    const lastPHQ = phqHist.length ? phqHist[phqHist.length - 1] : null;
    const lastGAD = gadHist.length ? gadHist[gadHist.length - 1] : null;

    // Build mood chart data (last 14 entries)
    const moodRecent = [...moodLog].sort((a, b) => new Date(a.date) - new Date(b.date)).slice(-14);
    const moodLabels = moodRecent.map(e => {
        const d = new Date(e.date);
        return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
    });
    const moodScores = moodRecent.map(e => e.score);

    // Sleep chart data (last 7 entries)
    const sleepRecent = [...sleepLog].sort((a, b) => new Date(a.isoDate || 0) - new Date(b.isoDate || 0)).slice(-7);
    const sleepLabels = sleepRecent.map(e => {
        const d = new Date(e.isoDate || Date.now());
        return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
    });
    const sleepHours = sleepRecent.map(e => parseFloat(e.durHrs || e.hours || 0));
    const sleepQuality = sleepRecent.map(e => parseFloat(e.quality || 0));

    // Thought records (last 10)
    const thoughtsHTML = thoughts.slice(-10).reverse().map(r => {
        const d = new Date(r.timestamp);
        const dateStr = d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' }) +
            ' · ' + d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
        return `
            <div class="thought-card">
                <div class="thought-date">${dateStr}</div>
                ${r.situation ? `<div class="field"><span class="label">Ситуация</span><span class="value">${r.situation}</span></div>` : ''}
                ${r.thought ? `<div class="field"><span class="label">Мысль</span><span class="value">${r.thought}</span></div>` : ''}
                ${r.emotion ? `<div class="field"><span class="label">Эмоция</span><span class="value">${r.emotion}${r.intensity ? ' · ' + r.intensity + '/10' : ''}</span></div>` : ''}
                ${r.rational_response ? `<div class="field"><span class="label">Рациональный ответ</span><span class="value">${r.rational_response}</span></div>` : ''}
                ${r.distortion ? `<div class="distortion-tag">${r.distortion}</div>` : ''}
            </div>`;
    }).join('');

    // PHQ/GAD history rows
    const testRows = [...phqHist.map(e => ({ ...e, type: 'PHQ-9' })),
    ...gadHist.map(e => ({ ...e, type: 'GAD-7' }))]
        .sort((a, b) => new Date(b.date) - new Date(a.date))
        .slice(0, 10)
        .map(e => {
            const d = new Date(e.date);
            const dateStr = d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
            return `<tr><td>${e.type}</td><td>${dateStr}</td><td><strong>${e.score}</strong></td><td>${e.interpretation || '—'}</td></tr>`;
        }).join('');

    // Activities
    const actRows = activities.slice(-15).map(a =>
        `<tr><td>${a.text || a.activity_text || '—'}</td><td>${a.done ? '✓ Выполнено' : '○ В плане'}</td></tr>`
    ).join('');

    const now = new Date();
    const reportDate = now.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });

    const html = `<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>КПТ-выписка · ${reportDate}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"><\/script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8f7f5; color: #1a1a2e; font-size: 13px; }
  .page { max-width: 820px; margin: 0 auto; padding: 40px 48px; }

  /* Header */
  .report-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 36px; padding-bottom: 20px; border-bottom: 2px solid #797298; }
  .report-title { font-size: 26px; font-weight: 700; color: #1a1a2e; }
  .report-subtitle { font-size: 13px; color: #888; margin-top: 4px; }
  .report-date { text-align: right; font-size: 12px; color: #888; }
  .report-badge { background: #797298; color: #fff; font-size: 11px; padding: 3px 10px; border-radius: 20px; display: inline-block; margin-top: 6px; }

  /* Stats */
  .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 36px; }
  .stat-card { background: #fff; border-radius: 12px; padding: 16px; border-left: 3px solid #797298; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
  .stat-val { font-size: 24px; font-weight: 700; color: #1a1a2e; }
  .stat-label { font-size: 11px; color: #888; margin-top: 3px; }

  /* Sections */
  .section { background: #fff; border-radius: 14px; padding: 24px; margin-bottom: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
  .section-title { font-size: 14px; font-weight: 700; color: #1a1a2e; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; padding-bottom: 10px; border-bottom: 1px solid #f0eef8; }
  .section-title::before { content: ''; display: inline-block; width: 4px; height: 16px; background: #797298; border-radius: 2px; }

  /* Thought cards */
  .thought-card { border: 1px solid #f0eef8; border-radius: 10px; padding: 14px 16px; margin-bottom: 12px; }
  .thought-card:last-child { margin-bottom: 0; }
  .thought-date { font-size: 11px; color: #888; margin-bottom: 10px; }
  .field { display: flex; gap: 8px; margin-bottom: 7px; font-size: 13px; }
  .label { min-width: 130px; font-weight: 600; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; color: #aaa; padding-top: 2px; }
  .value { flex: 1; line-height: 1.55; color: #1a1a2e; }
  .distortion-tag { display: inline-block; background: #f0eef8; color: #797298; border-radius: 20px; padding: 3px 10px; font-size: 11px; margin-top: 6px; }

  /* Tables */
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th { text-align: left; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; color: #aaa; font-weight: 700; padding: 0 0 10px; border-bottom: 1px solid #f0eef8; }
  td { padding: 8px 0; border-bottom: 1px solid #f8f7f5; vertical-align: top; }
  tr:last-child td { border-bottom: none; }

  /* Charts */
  .chart-wrap { position: relative; height: 160px; margin-top: 8px; }

  /* Empty */
  .empty { color: #aaa; font-size: 13px; text-align: center; padding: 20px 0; }

  /* Footer */
  .report-footer { margin-top: 36px; padding-top: 16px; border-top: 1px solid #eee; font-size: 11px; color: #bbb; text-align: center; }

  /* Print */
  @media print {
    body { background: #fff; }
    .page { padding: 20px 30px; }
    .no-print { display: none !important; }
    .section { box-shadow: none; border: 1px solid #eee; page-break-inside: avoid; }
    .thought-card { page-break-inside: avoid; }
  }
</style>
</head>
<body>
<div class="page">

  <!-- Header -->
  <div class="report-header">
    <div>
      <div class="report-title">КПТ-выписка</div>
      <div class="report-subtitle">Дневник мыслей · Настроение · Сон · Активности</div>
    </div>
    <div class="report-date">
      <div>${reportDate}</div>
      <div class="report-badge">Автоматический отчёт</div>
    </div>
  </div>

  <!-- Stats -->
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-val">${avgMood ?? '—'}</div>
      <div class="stat-label">Среднее настроение (14 д.)</div>
    </div>
    <div class="stat-card" style="border-left-color:#38bdf8;">
      <div class="stat-val">${avgSleep ? avgSleep + 'ч' : '—'}</div>
      <div class="stat-label">Среднее время сна (7 д.)</div>
    </div>
    <div class="stat-card" style="border-left-color:#10b981;">
      <div class="stat-val">${doneActs}</div>
      <div class="stat-label">Активностей выполнено</div>
    </div>
    <div class="stat-card" style="border-left-color:${lastPHQ ? '#f59e0b' : '#ccc'};">
      <div class="stat-val">${lastPHQ ? lastPHQ.score : '—'}</div>
      <div class="stat-label">PHQ-9 (последний)</div>
    </div>
  </div>

  <!-- Mood Chart -->
  ${moodScores.length >= 2 ? `
  <div class="section">
    <div class="section-title">Настроение — последние ${moodScores.length} записей</div>
    <div class="chart-wrap"><canvas id="moodChart"></canvas></div>
  </div>` : ''}

  <!-- Sleep Chart -->
  ${sleepHours.length >= 2 ? `
  <div class="section">
    <div class="section-title">Сон — последние ${sleepHours.length} дней</div>
    <div class="chart-wrap"><canvas id="sleepChart"></canvas></div>
  </div>` : ''}

  <!-- Thought diary -->
  <div class="section">
    <div class="section-title">Дневник мыслей (последние ${Math.min(thoughts.length, 10)} записей)</div>
    ${thoughtsHTML || '<div class="empty">Записей нет</div>'}
  </div>

  <!-- Tests -->
  ${testRows ? `
  <div class="section">
    <div class="section-title">Результаты тестов</div>
    <table>
      <thead><tr><th>Тест</th><th>Дата</th><th>Балл</th><th>Интерпретация</th></tr></thead>
      <tbody>${testRows}</tbody>
    </table>
  </div>` : ''}

  <!-- Activities -->
  ${actRows ? `
  <div class="section">
    <div class="section-title">Активности</div>
    <table>
      <thead><tr><th>Задача</th><th>Статус</th></tr></thead>
      <tbody>${actRows}</tbody>
    </table>
  </div>` : ''}

  <div class="report-footer">
    Сформировано КПТ-ассистентом · Не является медицинским заключением
  </div>

  <!-- Print button (hidden in print) -->
  <div class="no-print" style="text-align:center;margin-top:28px;">
    <button onclick="window.print()" style="background:#797298;color:#fff;border:none;border-radius:24px;padding:12px 32px;font-size:14px;cursor:pointer;font-family:inherit;">
      ↓ Сохранить как PDF
    </button>
    <p style="color:#aaa;font-size:11px;margin-top:8px;">Выберите «Сохранить как PDF» в диалоге печати</p>
  </div>
</div>

<script>
const MOOD_LABELS  = ${JSON.stringify(moodLabels)};
const MOOD_SCORES  = ${JSON.stringify(moodScores)};
const SLEEP_LABELS  = ${JSON.stringify(sleepLabels)};
const SLEEP_HOURS   = ${JSON.stringify(sleepHours)};
const SLEEP_QUALITY = ${JSON.stringify(sleepQuality)};

window.addEventListener('load', () => {
  if (MOOD_SCORES.length >= 2) {
    new Chart(document.getElementById('moodChart'), {
      type: 'line',
      data: {
        labels: MOOD_LABELS,
        datasets: [{
          label: 'Настроение',
          data: MOOD_SCORES,
          borderColor: '#797298',
          backgroundColor: 'rgba(121,114,152,0.12)',
          borderWidth: 2,
          pointRadius: 3,
          pointBackgroundColor: '#797298',
          tension: 0.4,
          fill: true,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { min: 0, max: 10, grid: { color: '#f0eef8' }, ticks: { font: { size: 11 } } },
          x: { grid: { display: false }, ticks: { font: { size: 11 } } }
        }
      }
    });
  }
  if (SLEEP_HOURS.length >= 2) {
    new Chart(document.getElementById('sleepChart'), {
      type: 'bar',
      data: {
        labels: SLEEP_LABELS,
        datasets: [
          { label: 'Часы сна', data: SLEEP_HOURS, backgroundColor: 'rgba(56,189,248,0.7)', borderRadius: 6, yAxisID: 'y' },
          { label: 'Качество', data: SLEEP_QUALITY, type: 'line', borderColor: '#f59e0b', pointBackgroundColor: '#f59e0b', borderWidth: 2, pointRadius: 3, tension: 0.4, yAxisID: 'y2' }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: 'top', labels: { font: { size: 11 }, boxWidth: 12 } } },
        scales: {
          y:  { min: 0, max: 12, grid: { color: '#f0eef8' }, ticks: { font: { size: 11 } }, title: { display: true, text: 'Часы', font: { size: 10 } } },
          y2: { min: 0, max: 10, position: 'right', grid: { display: false }, ticks: { font: { size: 11 } }, title: { display: true, text: 'Качество', font: { size: 10 } } },
          x: { grid: { display: false }, ticks: { font: { size: 11 } } }
        }
      }
    });
  }
});
<\/script>
</body>
</html>`;

    const win = window.open('', '_blank');
    win.document.write(html);
    win.document.close();
}

window.downloadAsPDF = downloadAsPDF;
window.downloadAsTXT = downloadAsTXT;
