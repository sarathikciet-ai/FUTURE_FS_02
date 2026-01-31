from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os, json, time, uuid
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXT = {'png','jpg','jpeg','gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ORDERS_FILE = 'orders.json'
if not os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE,'w') as f:
        json.dump([], f)

app = Flask(__name__, static_folder='.', static_url_path='')

def allowed(filename):
    ext = filename.rsplit('.',1)[-1].lower()
    return ext in ALLOWED_EXT

@app.route('/')
def index():
    # serve the index.html file
    return send_from_directory('.', 'index.html')

@app.route('/place_order', methods=['POST'])
def place_order():
    try:
        cust_name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        cart_json = request.form.get('cart')
        user_email = request.form.get('user_email')
        # handle file
        saved_filename = None
        if 'image' in request.files:
            f = request.files['image']
            if f and f.filename and allowed(f.filename):
                fname = secure_filename(f.filename)
                unique = f"{int(time.time())}_{uuid.uuid4().hex}_{fname}"
                path = os.path.join(UPLOAD_FOLDER, unique)
                f.save(path)
                saved_filename = unique

        order_id = str(uuid.uuid4())[:8]
        order = {
            "orderId": order_id,
            "name": cust_name,
            "phone": phone,
            "address": address,
            "cart": json.loads(cart_json) if cart_json else {},
            "image": saved_filename,
            "user_email": user_email,
            "created_at": time.time()
        }
        # append to orders.json
        with open(ORDERS_FILE,'r+') as f:
            arr = json.load(f)
            arr.append(order)
            f.seek(0)
            json.dump(arr, f, indent=2)
            f.truncate()
        return jsonify({"success": True, "orderId": order_id})
    except Exception as e:
        print("error:", e)
        return jsonify({"success": False, "error": str(e)}), 500

# serve uploaded files
@app.route('/uploads/<path:fname>')
def uploaded_file(fname):
    return send_from_directory(UPLOAD_FOLDER, fname)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
