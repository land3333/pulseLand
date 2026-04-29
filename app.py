import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_pulsepilot')

# Base de données
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'health_data.db')

def get_db():
    """Connexion à la base SQLite"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialise la base de données"""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS health_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            activity INTEGER NOT NULL,
            sleep REAL NOT NULL,
            stress INTEGER NOT NULL,
            weight REAL NOT NULL,
            height REAL NOT NULL,
            bmi REAL NOT NULL,
            heart_rate INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Base de données initialisée")

def calculate_heart_rate(age, activity, stress):
    """Calcule la fréquence cardiaque"""
    base_hr = 208 - 0.7 * age
    hr = base_hr + (activity * 0.12) + (stress * 0.8)
    return max(50, min(180, int(round(hr))))

def calculate_bmi(weight, height):
    """Calcule l'IMC"""
    if height > 0:
        return round(weight / (height ** 2), 1)
    return 0

# Initialisation
init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            age = int(request.form['age'])
            gender = request.form['gender']
            activity = int(request.form['activity'])
            sleep = float(request.form['sleep'])
            stress = int(request.form['stress'])
            weight = float(request.form['weight'])
            height = float(request.form['height'])
            
            bmi = calculate_bmi(weight, height)
            heart_rate = calculate_heart_rate(age, activity, stress)
            
            conn = get_db()
            conn.execute('''
                INSERT INTO health_records (age, gender, activity, sleep, stress, weight, height, bmi, heart_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (age, gender, activity, sleep, stress, weight, height, bmi, heart_rate))
            conn.commit()
            conn.close()
            
            flash('Données enregistrées avec succès!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Erreur: {str(e)}', 'error')
    
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    conn = get_db()
    records = conn.execute('SELECT * FROM health_records ORDER BY created_at DESC').fetchall()
    conn.close()
    
    # Convertir en liste de dictionnaires
    records_list = [dict(record) for record in records]
    
    # Calculer les statistiques
    if records_list:
        hr_values = [r['heart_rate'] for r in records_list]
        stats = {
            'count': len(records_list),
            'avg_hr': round(sum(hr_values) / len(hr_values), 1),
            'min_hr': min(hr_values),
            'max_hr': max(hr_values),
            'avg_activity': round(sum(r['activity'] for r in records_list) / len(records_list), 1),
            'avg_sleep': round(sum(r['sleep'] for r in records_list) / len(records_list), 1),
            'avg_bmi': round(sum(r['bmi'] for r in records_list) / len(records_list), 1)
        }
    else:
        stats = {
            'count': 0, 'avg_hr': 0, 'min_hr': 0, 'max_hr': 0,
            'avg_activity': 0, 'avg_sleep': 0, 'avg_bmi': 0
        }
    
    return render_template('dashboard.html', stats=stats, records=records_list)

@app.route('/delete/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    try:
        conn = get_db()
        conn.execute('DELETE FROM health_records WHERE id = ?', (record_id,))
        conn.commit()
        conn.close()
        flash('Enregistrement supprimé', 'success')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
