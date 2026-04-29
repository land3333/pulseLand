from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'pulsepilot_secret_2024'
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')


# ─── Database ──────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users_data (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            age      INTEGER NOT NULL,
            activity REAL    NOT NULL,
            sleep    REAL    NOT NULL,
            gender   TEXT    NOT NULL,
            stress   INTEGER NOT NULL,
            weight   REAL    NOT NULL,
            height   REAL    NOT NULL,
            bmi      REAL    NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# ─── Helper functions ──────────────────────────────────────────────────────────

def calculate_bmi(weight: float, height: float) -> float:
    """IMC = poids / taille²"""
    if height <= 0:
        return 0.0
    return round(weight / (height ** 2), 2)


def simulate_heart_rate(age: int, activity: float, stress: int, gender: str) -> float:
    """
    Simule un rythme cardiaque au repos (bpm).
    Formule : HR = 70 - 0.12*activity + 1.5*stress - 0.15*age + gender_offset
    """
    gender_offset = 3 if gender == 'F' else 0
    hr = 70 - 0.12 * activity + 1.5 * stress - 0.15 * age + gender_offset
    return round(max(45, min(120, hr)), 1)


def linear_regression(x_vals: list, y_vals: list):
    """
    Régression linéaire simple : y = a*x + b
    Retourne (a, b) calculés sans librairie externe.
    """
    n = len(x_vals)
    if n < 2:
        return 0.0, 0.0
    sum_x  = sum(x_vals)
    sum_y  = sum(y_vals)
    sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
    sum_x2 = sum(x ** 2 for x in x_vals)
    denom  = n * sum_x2 - sum_x ** 2
    if denom == 0:
        return 0.0, round(sum_y / n, 4)
    a = (n * sum_xy - sum_x * sum_y) / denom
    b = (sum_y - a * sum_x) / n
    return round(a, 4), round(b, 4)


def predict_heart_rate(activity: float, a: float, b: float) -> float:
    return round(a * activity + b, 1)


def validate_form(data: dict) -> list:
    errors = []
    try:
        age = int(data.get('age', 0))
        if not (1 <= age <= 120):
            errors.append('Âge invalide (1–120).')
    except (ValueError, TypeError):
        errors.append('Âge doit être un entier.')
    try:
        activity = float(data.get('activity', -1))
        if not (0 <= activity <= 1440):
            errors.append('Activité invalide (0–1440 min).')
    except (ValueError, TypeError):
        errors.append('Activité doit être un nombre.')
    try:
        sleep = float(data.get('sleep', -1))
        if not (0 <= sleep <= 24):
            errors.append('Sommeil invalide (0–24 h).')
    except (ValueError, TypeError):
        errors.append('Sommeil doit être un nombre.')
    try:
        stress = int(data.get('stress', 0))
        if not (1 <= stress <= 10):
            errors.append('Stress invalide (1–10).')
    except (ValueError, TypeError):
        errors.append('Stress doit être un entier.')
    try:
        weight = float(data.get('weight', 0))
        if not (20 <= weight <= 300):
            errors.append('Poids invalide (20–300 kg).')
    except (ValueError, TypeError):
        errors.append('Poids doit être un nombre.')
    try:
        height = float(data.get('height', 0))
        if not (0.5 <= height <= 2.5):
            errors.append('Taille invalide (0.5–2.5 m).')
    except (ValueError, TypeError):
        errors.append('Taille doit être un nombre.')
    if data.get('gender') not in ('M', 'F', 'Other'):
        errors.append('Genre invalide.')
    return errors


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return 'Sous-poids'
    if bmi < 25:
        return 'Normal'
    if bmi < 30:
        return 'Surpoids'
    return 'Obésité'


# ─── Routes ────────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data   = request.form.to_dict()
        errors = validate_form(data)
        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('index.html', form_data=data)

        age      = int(data['age'])
        activity = float(data['activity'])
        sleep    = float(data['sleep'])
        gender   = data['gender']
        stress   = int(data['stress'])
        weight   = float(data['weight'])
        height   = float(data['height'])
        bmi      = calculate_bmi(weight, height)

        conn = get_db()
        conn.execute(
            'INSERT INTO users_data (age, activity, sleep, gender, stress, weight, height, bmi) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (age, activity, sleep, gender, stress, weight, height, bmi)
        )
        conn.commit()
        conn.close()

        flash('Données enregistrées avec succès !', 'success')
        return redirect(url_for('dashboard'))

    return render_template('index.html', form_data={})


@app.route('/dashboard')
def dashboard():
    conn    = get_db()
    rows    = conn.execute('SELECT * FROM users_data ORDER BY id DESC').fetchall()
    conn.close()

    records = [dict(r) for r in rows]
    for r in records:
        r['heart_rate']    = simulate_heart_rate(r['age'], r['activity'], r['stress'], r['gender'])
        r['bmi_category']  = bmi_category(r['bmi'])

    if records:
        hrs        = [r['heart_rate'] for r in records]
        activities = [r['activity']   for r in records]
        bmis       = [r['bmi']        for r in records]
        sleeps     = [r['sleep']      for r in records]

        stats = {
            'count':        len(records),
            'avg_hr':       round(sum(hrs) / len(hrs), 1),
            'avg_bmi':      round(sum(bmis) / len(bmis), 1),
            'avg_sleep':    round(sum(sleeps) / len(sleeps), 1),
            'avg_activity': round(sum(activities) / len(activities), 1),
            'min_hr':       min(hrs),
            'max_hr':       max(hrs),
        }

        a, b         = linear_regression(activities, hrs)
        pred_hr      = predict_heart_rate(stats['avg_activity'], a, b)
        regression   = {'a': a, 'b': b, 'prediction': pred_hr,
                        'at_activity': stats['avg_activity']}
    else:
        stats      = {'count': 0, 'avg_hr': 0, 'avg_bmi': 0,
                      'avg_sleep': 0, 'avg_activity': 0, 'min_hr': 0, 'max_hr': 0}
        regression = {'a': 0, 'b': 0, 'prediction': 0, 'at_activity': 0}

    return render_template('dashboard.html', records=records,
                           stats=stats, regression=regression)


@app.route('/api/chart-data')
def chart_data():
    conn  = get_db()
    rows  = conn.execute('SELECT * FROM users_data').fetchall()
    conn.close()

    records   = [dict(r) for r in rows]
    scatter   = []
    hr_values = []

    for r in records:
        hr = simulate_heart_rate(r['age'], r['activity'], r['stress'], r['gender'])
        scatter.append({'x': r['activity'], 'y': hr, 'bmi': r['bmi']})
        hr_values.append(hr)

    # Histogramme par bins de 5 bpm
    bins = {}
    for hr in hr_values:
        b = int(hr // 5) * 5
        bins[b] = bins.get(b, 0) + 1
    hist_labels = sorted(bins.keys())
    hist_data   = [bins[k] for k in hist_labels]

    # Ligne de régression
    if len(scatter) >= 2:
        xs = [p['x'] for p in scatter]
        ys = [p['y'] for p in scatter]
        a, b_val = linear_regression(xs, ys)
        x_min, x_max = min(xs), max(xs)
        reg_line = [
            {'x': x_min, 'y': round(a * x_min + b_val, 1)},
            {'x': x_max, 'y': round(a * x_max + b_val, 1)},
        ]
    else:
        reg_line = []

    return jsonify({
        'scatter':         scatter,
        'hist_labels':     [f'{l}–{l+4} bpm' for l in hist_labels],
        'hist_data':       hist_data,
        'regression_line': reg_line,
    })


@app.route('/api/delete/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    conn = get_db()
    conn.execute('DELETE FROM users_data WHERE id = ?', (record_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})


# ─── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=9000)
