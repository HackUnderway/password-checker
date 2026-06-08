from flask import Flask, render_template, request, jsonify
import hashlib
import bisect
import os

app = Flask(__name__)

# Ruta al archivo de contraseñas filtradas
PASSWORD_FILE = "/home/kali/Desktop/password-checker/db/breachcompilation.txt"  # Cambia por tu ruta real

# Cargar contraseñas en memoria de forma optimizada
# Opción 1: Para 9 GB NO se puede cargar entero. Usaremos búsqueda binaria en archivo ordenado

def is_password_breached(password):
    """
    Verifica si una contraseña está en el archivo de filtraciones.
    Usa búsqueda binaria asumiendo que el archivo está ordenado.
    """
    # Si el archivo no está ordenado, esta búsqueda no funcionará correctamente
    # Primero necesitas ordenar el archivo (ver instrucciones abajo)
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Búsqueda binaria en el archivo ordenado
    with open(PASSWORD_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        # Buscar la línea que contiene el hash
        f.seek(0, 2)  # Ir al final
        file_size = f.tell()
        
        low = 0
        high = file_size
        
        while low <= high:
            mid = (low + high) // 2
            f.seek(mid)
            
            # Ir al inicio de la línea actual
            if mid > 0:
                f.readline()
            
            line = f.readline().strip()
            if not line:
                break
                
            if line == password_hash:
                return True
            elif line < password_hash:
                low = f.tell()
            else:
                high = mid - len(line) - 1
                
    return False

# Versión SIMPLE pero más lenta (usa grep)
def is_password_breached_simple(password):
    """
    Versión simple usando grep (más lenta pero no requiere archivo ordenado)
    """
    import subprocess
    result = subprocess.run(
        f'grep -Fx "{password}" {PASSWORD_FILE}',
        shell=True,
        capture_output=True,
        text=True
    )
    return result.returncode == 0

# Versión RÁPIDA usando hash (recomendada)
def is_password_breached_fast(password):
    """
    Convierte la contraseña a SHA-256 y busca el hash.
    Ideal si conviertes el archivo a una lista de hashes.
    """
    import subprocess
    
    # Generar hash SHA-256 de la contraseña
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Buscar el hash en el archivo (asumiendo que contiene hashes, no contraseñas planas)
    result = subprocess.run(
        f'grep -Fx "{password_hash}" {PASSWORD_FILE}',
        shell=True,
        capture_output=True,
        text=True
    )
    return result.returncode == 0

@app.route('/')
def index():
    """Página principal con la interfaz"""
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_password():
    """Endpoint para verificar una contraseña"""
    password = request.form.get('password', '')
    
    if not password:
        return jsonify({'error': 'No se proporcionó contraseña'}), 400
    
    # Verificar si la contraseña está en la lista de filtradas
    is_breached = is_password_breached_simple(password)  # Usa grep
    
    return jsonify({
        'password': password,
        'breached': is_breached,
        'message': '⚠️ Esta contraseña ha sido filtrada' if is_breached else '✅ Esta contraseña parece segura'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
