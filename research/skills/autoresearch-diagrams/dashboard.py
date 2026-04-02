#!/usr/bin/env python3
"""
Autoresearch Dashboard — Live visualization of diagram prompt optimization.

Reads results.jsonl and serves a live-updating dashboard at http://localhost:8501.

Usage:
    python3 diagram_autoresearch_dashboard.py
    python3 diagram_autoresearch_dashboard.py --port 8501
"""

import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent / "data"
RESULTS_FILE = BASE_DIR / "results.jsonl"
STATE_FILE = BASE_DIR / "state.json"
PROMPT_FILE = BASE_DIR / "prompt.txt"
BEST_PROMPT_FILE = BASE_DIR / "best_prompt.txt"
DIAGRAMS_DIR = BASE_DIR / "diagrams"

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Diagram Autoresearch</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #faf9f7; color: #2d2a26; padding: 32px; max-width: 1200px; margin: 0 auto; }

  .header { display: flex; align-items: center; gap: 16px; margin-bottom: 32px; }
  .header h1 { font-size: 28px; font-weight: 700; color: #2d2a26; }
  .badge { background: #c0392b; color: white; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 4px; letter-spacing: 1px; }
  .subtitle { color: #8a8580; font-size: 14px; margin-top: 4px; }

  .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; }
  .stat-card { background: white; border-radius: 12px; padding: 20px 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
  .stat-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #8a8580; margin-bottom: 8px; }
  .stat-value { font-size: 36px; font-weight: 700; }
  .stat-value.green { color: #27ae60; }
  .stat-value.orange { color: #c0784a; }
  .stat-value.neutral { color: #2d2a26; }

  .chart-container { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 32px; }
  .chart-container canvas { width: 100% !important; height: 300px !important; }

  .criteria-charts { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 32px; }
  .criteria-chart { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
  .criteria-chart h3 { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #8a8580; margin-bottom: 12px; }
  .criteria-chart canvas { width: 100% !important; height: 160px !important; }

  .table-container { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 32px; }
  .table-container h3 { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #8a8580; margin-bottom: 16px; }
  table { width: 100%; border-collapse: collapse; }
  th { text-align: left; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #8a8580; padding: 8px 12px; border-bottom: 1px solid #eee; }
  td { padding: 10px 12px; border-bottom: 1px solid #f5f4f2; font-size: 14px; }
  .status-keep { color: #27ae60; font-weight: 600; }
  .status-discard { color: #8a8580; }

  .prompt-container { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
  .prompt-container h3 { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #8a8580; margin-bottom: 12px; }
  .prompt-text { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 13px; line-height: 1.6; color: #4a4540; white-space: pre-wrap; word-break: break-word; background: #faf9f7; padding: 16px; border-radius: 8px; max-height: 300px; overflow-y: auto; }

  @media (max-width: 768px) {
    .stats { grid-template-columns: repeat(2, 1fr); }
    .criteria-charts { grid-template-columns: 1fr; }
    body { padding: 16px; }
  }
</style>
</head>
<body>

<div class="header">
  <div>
    <div style="display:flex;align-items:center;gap:12px;">
      <h1>Autoresearch</h1>
      <span class="badge" id="live-badge">LIVE</span>
    </div>
    <div class="subtitle" id="subtitle">Diagram prompt optimization — refreshes every 15s</div>
  </div>
</div>

<div class="stats">
  <div class="stat-card">
    <div class="stat-label">Current Best</div>
    <div class="stat-value orange" id="stat-best">—</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Baseline</div>
    <div class="stat-value neutral" id="stat-baseline">—</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Improvement</div>
    <div class="stat-value green" id="stat-improvement">—</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Runs / Kept</div>
    <div class="stat-value neutral" id="stat-runs">—</div>
  </div>
</div>

<div class="chart-container">
  <canvas id="mainChart"></canvas>
</div>

<div class="criteria-charts">
  <div class="criteria-chart">
    <h3>Legible & Grammatical</h3>
    <canvas id="legChart"></canvas>
  </div>
  <div class="criteria-chart">
    <h3>Pastel Colors</h3>
    <canvas id="pastelChart"></canvas>
  </div>
  <div class="criteria-chart">
    <h3>Linear Layout</h3>
    <canvas id="linearChart"></canvas>
  </div>
  <div class="criteria-chart">
    <h3>No Numbers</h3>
    <canvas id="numbersChart"></canvas>
  </div>
</div>

<div class="table-container">
  <h3>Run History</h3>
  <table>
    <thead>
      <tr><th>Run</th><th>Status</th><th>Score</th><th>Legible</th><th>Pastel</th><th>Linear</th><th>No Nums</th><th>Time</th></tr>
    </thead>
    <tbody id="run-table"></tbody>
  </table>
</div>

<div class="prompt-container">
  <h3>Current Best Prompt</h3>
  <div class="prompt-text" id="best-prompt">Loading...</div>
</div>

<script>
const ORANGE = '#c0784a';
const ORANGE_LIGHT = 'rgba(192, 120, 74, 0.15)';
const GREEN = '#27ae60';
const GREEN_LIGHT = 'rgba(39, 174, 96, 0.15)';

const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 11 }, color: '#8a8580' } },
    y: { grid: { color: '#f0efed' }, ticks: { font: { size: 11 }, color: '#8a8580' } }
  }
};

let mainChart, legChart, pastelChart, linearChart, numbersChart;

function createChart(canvasId, label, maxY, color, colorLight) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label,
        data: [],
        borderColor: color,
        backgroundColor: colorLight,
        fill: true,
        tension: 0.3,
        pointRadius: 5,
        pointBackgroundColor: [],
        pointBorderColor: color,
        pointBorderWidth: 2,
      }]
    },
    options: {
      ...chartDefaults,
      scales: {
        ...chartDefaults.scales,
        y: { ...chartDefaults.scales.y, min: 0, max: maxY, ticks: { ...chartDefaults.scales.y.ticks, stepSize: maxY <= 10 ? 1 : 5 } }
      }
    }
  });
}

function initCharts() {
  mainChart = createChart('mainChart', 'Score', 40, ORANGE, ORANGE_LIGHT);
  legChart = createChart('legChart', 'Legible', 10, '#8e44ad', 'rgba(142,68,173,0.12)');
  pastelChart = createChart('pastelChart', 'Pastel', 10, '#2980b9', 'rgba(41,128,185,0.12)');
  linearChart = createChart('linearChart', 'Linear', 10, '#27ae60', 'rgba(39,174,96,0.12)');
  numbersChart = createChart('numbersChart', 'No Numbers', 10, '#d35400', 'rgba(211,84,0,0.12)');
}

function updateChart(chart, labels, data, bestScore) {
  chart.data.labels = labels;
  chart.data.datasets[0].data = data;
  // Color dots: orange for new best at that point, gray for discard
  let runningBest = -1;
  const colors = data.map(v => {
    if (v > runningBest) { runningBest = v; return ORANGE; }
    return '#c4c0bb';
  });
  chart.data.datasets[0].pointBackgroundColor = colors;
  chart.update('none');
}

function updateCriterionChart(chart, labels, data) {
  chart.data.labels = labels;
  chart.data.datasets[0].data = data;
  let runningBest = -1;
  const colors = data.map(v => {
    if (v > runningBest) { runningBest = v; return chart.data.datasets[0].borderColor; }
    return '#c4c0bb';
  });
  chart.data.datasets[0].pointBackgroundColor = colors;
  chart.update('none');
}

async function fetchData() {
  try {
    const res = await fetch('/api/data');
    const data = await res.json();
    return data;
  } catch (e) {
    console.error('Fetch error:', e);
    return null;
  }
}

function formatTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

async function refresh() {
  const data = await fetchData();
  if (!data || !data.runs || data.runs.length === 0) return;

  const runs = data.runs;
  const labels = runs.map(r => r.run);
  const scores = runs.map(r => r.score);
  const baseline = scores[0];
  const best = Math.max(...scores);

  // Stats
  document.getElementById('stat-best').textContent = best + '/40';
  document.getElementById('stat-baseline').textContent = baseline + '/40';
  const improvement = baseline > 0 ? ((best - baseline) / baseline * 100).toFixed(1) : '—';
  const improvEl = document.getElementById('stat-improvement');
  improvEl.textContent = improvement === '—' ? '—' : (improvement > 0 ? '+' : '') + improvement + '%';
  improvEl.className = 'stat-value ' + (improvement > 0 ? 'green' : improvement < 0 ? 'orange' : 'neutral');

  // Count "kept" runs (new best at that point)
  let kept = 0, runningBest = -1;
  scores.forEach(s => { if (s > runningBest) { kept++; runningBest = s; } });
  document.getElementById('stat-runs').textContent = runs.length + ' / ' + kept;

  // Main chart
  updateChart(mainChart, labels, scores, best);

  // Criteria charts
  updateCriterionChart(legChart, labels, runs.map(r => r.criteria?.legible ?? 0));
  updateCriterionChart(pastelChart, labels, runs.map(r => r.criteria?.pastel ?? 0));
  updateCriterionChart(linearChart, labels, runs.map(r => r.criteria?.linear ?? 0));
  updateCriterionChart(numbersChart, labels, runs.map(r => r.criteria?.no_numbers ?? 0));

  // Table (most recent first)
  const tbody = document.getElementById('run-table');
  let runningBest2 = -1;
  const statuses = scores.map(s => { if (s > runningBest2) { runningBest2 = s; return 'keep'; } return 'discard'; });
  const rows = runs.map((r, idx) => {
    const st = statuses[idx];
    return `<tr>
      <td>${r.run}</td>
      <td class="status-${st}">${st}</td>
      <td><strong>${r.score}/40</strong></td>
      <td>${r.criteria?.legible ?? '?'}/10</td>
      <td>${r.criteria?.pastel ?? '?'}/10</td>
      <td>${r.criteria?.linear ?? '?'}/10</td>
      <td>${r.criteria?.no_numbers ?? '?'}/10</td>
      <td>${formatTime(r.timestamp)}</td>
    </tr>`;
  }).reverse();
  tbody.innerHTML = rows.join('');

  // Best prompt
  if (data.best_prompt) {
    document.getElementById('best-prompt').textContent = data.best_prompt;
  }

  // Update subtitle
  const lastRun = runs[runs.length - 1];
  document.getElementById('subtitle').textContent =
    `Diagram prompt optimization — ${runs.length} runs — last: ${formatTime(lastRun?.timestamp)}`;
}

initCharts();
refresh();
setInterval(refresh, 15000);
</script>
</body>
</html>"""


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode())

        elif parsed.path == "/api/data":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            runs = []
            if RESULTS_FILE.exists():
                for line in RESULTS_FILE.read_text().strip().split("\n"):
                    if line.strip():
                        try:
                            runs.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass

            best_prompt = ""
            if BEST_PROMPT_FILE.exists():
                best_prompt = BEST_PROMPT_FILE.read_text().strip()

            data = {"runs": runs, "best_prompt": best_prompt}
            self.wfile.write(json.dumps(data).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress request logs


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Autoresearch Dashboard")
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()

    server = HTTPServer(("0.0.0.0", args.port), DashboardHandler)
    print(f"Dashboard running at http://localhost:{args.port}")
    print(f"Reading from: {RESULTS_FILE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutdown.")


if __name__ == "__main__":
    main()
