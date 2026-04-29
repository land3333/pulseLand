/* ═══════════════════════════════════════════════════════
   PulsePilot — dashboard.js
   ═══════════════════════════════════════════════════════ */

// ── Chart.js defaults ────────────────────────────────────
Chart.defaults.font.family = "'DM Sans', system-ui, sans-serif";
Chart.defaults.font.size   = 12;
Chart.defaults.color       = '#64748b';

const BLUE   = '#2563eb';
const GREEN  = '#16a34a';
const TEAL   = '#0d9488';
const BLUE_A = 'rgba(37,99,235,.15)';
const GREEN_A= 'rgba(22,163,74,.2)';

// ── Load chart data from API ─────────────────────────────
async function loadCharts() {
  const scatterCtx = document.getElementById('scatterChart');
  const histCtx    = document.getElementById('histChart');
  if (!scatterCtx || !histCtx) return;

  let data;
  try {
    const res = await fetch('/api/chart-data');
    data = await res.json();
  } catch (err) {
    console.error('Erreur chargement données:', err);
    return;
  }

  // ── Scatter: activité vs FC ───────────────────────────
  const scatterDatasets = [
    {
      label: 'Données patients',
      data: data.scatter,
      backgroundColor: data.scatter.map(p => bmiColor(p.bmi)),
      borderColor: 'transparent',
      pointRadius: 7,
      pointHoverRadius: 9,
    }
  ];

  if (data.regression_line.length === 2) {
    scatterDatasets.push({
      label: 'Régression linéaire',
      data: data.regression_line,
      type: 'line',
      borderColor: '#f97316',
      borderWidth: 2.5,
      borderDash: [6, 3],
      backgroundColor: 'transparent',
      pointRadius: 0,
      tension: 0,
    });
  }

  new Chart(scatterCtx, {
    type: 'scatter',
    data: { datasets: scatterDatasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 800, easing: 'easeOutQuart' },
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 12, padding: 16 } },
        tooltip: {
          callbacks: {
            label: ctx => {
              const p = ctx.raw;
              return `Activité: ${p.x} min | FC: ${p.y} bpm | IMC: ${p.bmi ?? '—'}`;
            }
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: 'Activité physique (min/jour)', color: '#94a3b8' },
          grid: { color: '#f1f5f9' },
        },
        y: {
          title: { display: true, text: 'Fréquence cardiaque (bpm)', color: '#94a3b8' },
          grid: { color: '#f1f5f9' },
        }
      }
    }
  });

  // ── Histogram: distribution FC ────────────────────────
  new Chart(histCtx, {
    type: 'bar',
    data: {
      labels: data.hist_labels,
      datasets: [{
        label: 'Nombre de patients',
        data: data.hist_data,
        backgroundColor: data.hist_data.map((_, i) => {
          const palette = [BLUE_A, 'rgba(13,148,136,.2)', GREEN_A,
                           'rgba(124,58,237,.15)', 'rgba(239,68,68,.15)'];
          return palette[i % palette.length];
        }),
        borderColor: data.hist_data.map((_, i) => {
          const palette = [BLUE, TEAL, GREEN, '#7c3aed', '#ef4444'];
          return palette[i % palette.length];
        }),
        borderWidth: 2,
        borderRadius: 6,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 900, easing: 'easeOutBounce' },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => `${ctx.raw} patient${ctx.raw > 1 ? 's' : ''}`
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: 'Plage FC (bpm)', color: '#94a3b8' },
          grid: { display: false },
        },
        y: {
          title: { display: true, text: 'Nombre', color: '#94a3b8' },
          grid: { color: '#f1f5f9' },
          ticks: { stepSize: 1 },
        }
      }
    }
  });
}

function bmiColor(bmi) {
  if (!bmi) return BLUE_A.replace('.15','0.7');
  if (bmi < 18.5) return 'rgba(30,64,175,.7)';
  if (bmi < 25)   return 'rgba(22,163,74,.7)';
  if (bmi < 30)   return 'rgba(217,119,6,.7)';
  return 'rgba(220,38,38,.7)';
}

// ── Delete record ─────────────────────────────────────────
async function deleteRecord(id) {
  if (!confirm(`Supprimer l'enregistrement #${id} ?`)) return;
  try {
    const res = await fetch(`/api/delete/${id}`, { method: 'DELETE' });
    if (res.ok) {
      const row = document.getElementById(`row-${id}`);
      if (row) {
        row.style.transition = 'opacity .3s, transform .3s';
        row.style.opacity = '0';
        row.style.transform = 'translateX(20px)';
        setTimeout(() => { row.remove(); location.reload(); }, 350);
      }
    }
  } catch (err) {
    alert('Erreur lors de la suppression.');
  }
}

// ── Auto-dismiss flash ────────────────────────────────────
document.querySelectorAll('.flash').forEach(f => {
  setTimeout(() => {
    f.style.transition = 'opacity .4s';
    f.style.opacity    = '0';
    setTimeout(() => f.remove(), 400);
  }, 4000);
});

loadCharts();
