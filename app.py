import requests
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
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    user_message = request.json.get('message', '')
    if not user_message:
        return {'reply': '¿Qué pasó sumercé? No me escribiste nada.'}, 400

    api_key = "sk-be96ee07747f4e5999d55d7c8df95e0f"
    
    system_prompt = "Eres RICARDO la papa sabia. Solo hablas de consejos para sembrar papa y de sus variedades. Si te preguntan por cualquier otra cosa (por ejemplo, maíz), debes decir que solo hablas de papas y sus variedades únicamente. Debes hablar con el acento de Colombia, como paisa. Saluda usando expresiones como 'como esta sumerce' y usa palabras típicas de la región agrícola colombiana en tus respuestas."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        reply_content = response.json()['choices'][0]['message']['content']
        return {'reply': reply_content}
    except Exception as e:
        print(f"Error llamando a Deepseek API: {e}")
        return {'reply': 'Uy sumercé, me disculpa pero la mente me dio vueltas y no me pude conectar. Se nos cayó la señal del cultivo, inténtalo de nuevo más lueguito.'}, 500


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
