# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import qrcode
import json
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

DATA_FILE = 'data.json'
QR_FOLDER = 'static/qrcodes'

# Crear carpetas si no existen
os.makedirs(QR_FOLDER, exist_ok=True)

# Cargar datos
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Guardar datos
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Generar QR para un ID
def generate_qr(item_id):
    qr_path = f"{QR_FOLDER}/{item_id}.png"
    if os.path.exists(qr_path):
        return  # QR ya existe
    qr_url = url_for('delete_item', item_id=item_id, _external=True)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_path)

# Ruta principal - Listar elementos
@app.route('/')
def index():
    items = load_data()
    return render_template('index.html', items=items)

# Crear nuevo elemento
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        item_id = str(uuid.uuid4())  # ID único
        new_item = {
            'id': item_id,
            'title': title,
            'description': description,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        items = load_data()
        items.append(new_item)
        save_data(items)
        generate_qr(item_id)  # Generar QR
        flash('Elemento creado exitosamente.')
        return redirect(url_for('index'))
    return render_template('create.html')

# Actualizar elemento
@app.route('/edit/<item_id>', methods=['GET', 'POST'])
def edit(item_id):
    items = load_data()
    item = next((i for i in items if i['id'] == item_id), None)
    if not item:
        flash('Elemento no encontrado.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        item['title'] = request.form['title']
        item['description'] = request.form.get('description', '')
        save_data(items)
        flash('Elemento actualizado.')
        return redirect(url_for('index'))

    return render_template('create.html', item=item)

# Eliminar elemento (cuando se escanea el QR)
@app.route('/delete/<item_id>')
def delete_item(item_id):
    items = load_data()
    item = next((i for i in items if i['id'] == item_id), None)
    if item:
        items.remove(item)
        save_data(items)
        # Opcional: eliminar archivo QR
        qr_path = f"{QR_FOLDER}/{item_id}.png"
        if os.path.exists(qr_path):
            os.remove(qr_path)
        return "<h1>✅ Registro eliminado automáticamente.</h1><p>Este elemento ya no existe.</p>"
    else:
        return "<h1>❌ El elemento ya fue eliminado o no existe.</h1>"

# Eliminar manualmente (opcional)
@app.route('/delete_manual/<item_id>')
def delete_manual(item_id):
    items = load_data()
    item = next((i for i in items if i['id'] == item_id), None)
    if item:
        items.remove(item)
        save_data(items)
        qr_path = f"{QR_FOLDER}/{item_id}.png"
        if os.path.exists(qr_path):
            os.remove(qr_path)
        flash('Elemento eliminado manualmente.')
    else:
        flash('Elemento no encontrado.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

w = 2