from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'agropapa_secret_key_potato_power' # Clave secreta para sesiones

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/diagnostico')
def diagnostico():
    return render_template('diagnostico.html')

@app.route('/soluciones')
def soluciones():
    return render_template('soluciones.html')

@app.route('/mercado')
def mercado():
    return render_template('mercado.html')

@app.route('/calendario')
def calendario():
    return render_template('calendario.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/bitacora')
def bitacora():
    return render_template('bitacora.html')

@app.route('/clima')
def clima():
    from scraper import get_weather_data, get_moon_phase, get_dollar_trm
    
    # Fetch Data
    weather_boyaca = get_weather_data("Tunja")
    weather_colombia = get_weather_data("Bogota")
    moon = get_moon_phase()
    dollar = get_dollar_trm()
    
    return render_template('clima.html', 
                         weather_boyaca=weather_boyaca,
                         weather_colombia=weather_colombia,
                         moon=moon,
                         dollar=dollar)

@app.route('/quienes_somos')
def quienes_somos():
    return render_template('quienes_somos.html')


# --- Login System ---
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # Simulación de registro exitoso
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Simulación de credenciales
        if username == 'administrador' and password == '123':
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas. Intenta de nuevo.', 'danger')
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', user=session['user'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))
# --------------------

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
