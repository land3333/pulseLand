/* ═══════════════════════════════════════════════════════
   PulsePilot — main.js  (page saisie)
   ═══════════════════════════════════════════════════════ */

// ── BMI live calculation ──────────────────────────────────
const weightInput  = document.getElementById('weight');
const heightInput  = document.getElementById('height');
const bmiValue     = document.getElementById('bmiValue');
const bmiCategory  = document.getElementById('bmiCategory');
const bmiPreview   = document.getElementById('bmiPreview');

function calcBMI() {
  const w = parseFloat(weightInput.value);
  const h = parseFloat(heightInput.value);
  if (w > 0 && h > 0) {
    const bmi = w / (h * h);
    bmiValue.textContent = bmi.toFixed(1);
    bmiPreview.classList.add('active');

    let cat = '';
    if      (bmi < 18.5) cat = 'Sous-poids';
    else if (bmi < 25)   cat = 'Normal ✓';
    else if (bmi < 30)   cat = 'Surpoids';
    else                  cat = 'Obésité';
    bmiCategory.textContent = cat;
  } else {
    bmiValue.textContent = '—';
    bmiCategory.textContent = '';
    bmiPreview.classList.remove('active');
  }
}

function resetBMI() {
  bmiValue.textContent = '—';
  bmiCategory.textContent = '';
  bmiPreview.classList.remove('active');
}

if (weightInput) weightInput.addEventListener('input', calcBMI);
if (heightInput) heightInput.addEventListener('input', calcBMI);
calcBMI();   // init on load (if form_data pre-filled)

// ── Slider ↔ number sync ─────────────────────────────────
function syncSlider(inputId, sliderId) {
  const input  = document.getElementById(inputId);
  const slider = document.getElementById(sliderId);
  if (!input || !slider) return;

  input.addEventListener('input', () => { slider.value = input.value; });
  slider.addEventListener('input', () => { input.value = slider.value; calcBMI(); });
}
syncSlider('activity', 'activitySlider');
syncSlider('sleep',    'sleepSlider');

// ── Radio card visual toggle ─────────────────────────────
document.querySelectorAll('.radio-card').forEach(card => {
  card.addEventListener('click', () => {
    card.closest('.radio-group')
        .querySelectorAll('.radio-card')
        .forEach(c => c.classList.remove('checked'));
    card.classList.add('checked');
  });
});

// ── Stress buttons ───────────────────────────────────────
document.querySelectorAll('.stress-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.stress-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  });
});

// ── Client-side validation ───────────────────────────────
const form = document.getElementById('healthForm');
if (form) {
  form.addEventListener('submit', (e) => {
    let valid = true;

    const rules = [
      { id: 'age',      errId: 'ageError',      min: 1,   max: 120,  msg: 'Âge : 1–120 ans' },
      { id: 'activity', errId: 'activityError', min: 0,   max: 1440, msg: 'Activité : 0–1440 min' },
      { id: 'sleep',    errId: 'sleepError',    min: 0,   max: 24,   msg: 'Sommeil : 0–24 h' },
      { id: 'weight',   errId: 'weightError',   min: 20,  max: 300,  msg: 'Poids : 20–300 kg' },
      { id: 'height',   errId: 'heightError',   min: 0.5, max: 2.5,  msg: 'Taille : 0.5–2.5 m' },
    ];

    rules.forEach(r => {
      const el  = document.getElementById(r.id);
      const err = document.getElementById(r.errId);
      const val = parseFloat(el.value);
      if (isNaN(val) || val < r.min || val > r.max) {
        el.classList.add('error');
        if (err) err.textContent = r.msg;
        valid = false;
      } else {
        el.classList.remove('error');
        if (err) err.textContent = '';
      }
    });

    // Stress
    const stressChecked = document.querySelector('input[name="stress"]:checked');
    const stressErr     = document.getElementById('stressError');
    if (!stressChecked) {
      if (stressErr) stressErr.textContent = 'Veuillez choisir un niveau de stress.';
      valid = false;
    } else if (stressErr) {
      stressErr.textContent = '';
    }

    // Gender
    const genderChecked = document.querySelector('input[name="gender"]:checked');
    const genderErr     = document.getElementById('genderError');
    if (!genderChecked) {
      if (genderErr) genderErr.textContent = 'Veuillez choisir un genre.';
      valid = false;
    } else if (genderErr) {
      genderErr.textContent = '';
    }

    if (!valid) {
      e.preventDefault();
      // Scroll to first error
      const firstErr = form.querySelector('.form-input.error');
      if (firstErr) firstErr.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  });
}

// ── Auto-dismiss flash messages ───────────────────────────
document.querySelectorAll('.flash').forEach(f => {
  setTimeout(() => {
    f.style.transition = 'opacity .4s';
    f.style.opacity = '0';
    setTimeout(() => f.remove(), 400);
  }, 4000);
});
