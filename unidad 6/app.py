from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import mysql.connector
from datetime import datetime

app = Flask(__name__)
CORS(app) 

def get_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ferreteria"
    )

class Persona:
    def __init__(self, nombre, telefono):
        self.nombre = nombre
        self.telefono = telefono

class Cliente(Persona):
    def __init__(self, idc, nombre, telefono, correo):
        super().__init__(nombre, telefono)
        self.idc = idc
        self.correo = correo

class Producto:
    def __init__(self, codigo, nombre, categoria, precio):
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio

class Venta:
    def __init__(self, folio, id_cliente, codigo, fecha, cantidad, total):
        self.folio = folio
        self.id_cliente = id_cliente
        self.codigo = codigo
        self.fecha = fecha
        self.cantidad = cantidad
        self.total = total

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = data.get('usuario', '')
    password = data.get('password', '')

    try:
        conexion = get_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT * FROM empleados WHERE usuario = %s AND password = %s",
            (usuario, password)
        )
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()

        if resultado:
            return jsonify({ "ok": True, "usuario": usuario })
        else:
            return jsonify({ "ok": False, "mensaje": "Usuario o contraseña incorrectos" }), 401

    except Exception as e:
        return jsonify({ "ok": False, "mensaje": str(e) }), 500


@app.route('/api/productos', methods=['GET'])
def get_productos():
    try:
        conexion = get_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM productos")
        filas = cursor.fetchall()
        cursor.close()
        conexion.close()

        productos = []
        for p in filas:
            productos.append({
                "codigo":    p[0],
                "nombre":    p[1],
                "categoria": p[2],
                "precio":    float(p[3]),
                "cantidad":  p[4],
                "vendidos":  p[5]
            })
        return jsonify(productos)

    except Exception as e:
        return jsonify({ "error": str(e) }), 500


@app.route('/api/productos', methods=['POST'])
def alta_producto():
    data = request.get_json()
    codigo    = data.get('codigo', '').strip()
    nombre    = data.get('nombre', '').strip()
    categoria = data.get('categoria', '').strip()
    precio    = data.get('precio')
    cantidad  = data.get('cantidad')

    if not all([codigo, nombre, categoria, precio is not None, cantidad is not None]):
        return jsonify({ "ok": False, "mensaje": "Todos los campos son obligatorios" }), 400

    try:
        conexion = get_conexion()
        cursor = conexion.cursor()

        
        cursor.execute("SELECT codigo FROM productos WHERE codigo = %s", (codigo,))
        if cursor.fetchone():
            cursor.close()
            conexion.close()
            return jsonify({ "ok": False, "mensaje": "Ya existe un producto con ese código" }), 409

        producto = Producto(codigo, nombre, categoria, float(precio))
        cursor.execute(
            "INSERT INTO productos (codigo, nombre, categoria, precio, cantidad, vendidos) VALUES (%s, %s, %s, %s, %s, %s)",
            (producto.codigo, producto.nombre, producto.categoria, producto.precio, int(cantidad), 0)
        )
        conexion.commit()
        cursor.close()
        conexion.close()
        return jsonify({ "ok": True, "mensaje": "Producto guardado" })

    except Exception as e:
        return jsonify({ "ok": False, "mensaje": str(e) }), 500


@app.route('/api/productos/<codigo>', methods=['GET'])
def get_producto(codigo):
    try:
        conexion = get_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM productos WHERE codigo = %s", (codigo,))
        p = cursor.fetchone()
        cursor.close()
        conexion.close()

        if p:
            return jsonify({
                "codigo":    p[0],
                "nombre":    p[1],
                "categoria": p[2],
                "precio":    float(p[3]),
                "cantidad":  p[4],
                "vendidos":  p[5]
            })
        else:
            return jsonify({ "error": "Producto no encontrado" }), 404

    except Exception as e:
        return jsonify({ "error": str(e) }), 500


@app.route('/api/clientes', methods=['GET'])
def get_clientes():
    try:
        conexion = get_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM clientes")
        filas = cursor.fetchall()
        cursor.close()
        conexion.close()

        clientes = []
        for c in filas:
            clientes.append({
                "id":       c[0],
                "nombre":   c[1],
                "telefono": c[2],
                "correo":   c[3]
            })
        return jsonify(clientes)

    except Exception as e:
        return jsonify({ "error": str(e) }), 500


@app.route('/api/clientes', methods=['POST'])
def registrar_cliente():
    data = request.get_json()
    idc      = data.get('id', '').strip()
    nombre   = data.get('nombre', '').strip()
    telefono = data.get('telefono', '').strip()
    correo   = data.get('correo', '').strip()

    if not all([idc, nombre, telefono, correo]):
        return jsonify({ "ok": False, "mensaje": "Todos los campos son obligatorios" }), 400

    try:
        conexion = get_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT id FROM clientes WHERE id = %s", (idc,))
        if cursor.fetchone():
            cursor.close()
            conexion.close()
            return jsonify({ "ok": False, "mensaje": "Ya existe un cliente con ese ID" }), 409

        cliente = Cliente(idc, nombre, telefono, correo)
        cursor.execute(
            "INSERT INTO clientes (id, nombre, telefono, correo) VALUES (%s, %s, %s, %s)",
            (cliente.idc, cliente.nombre, cliente.telefono, cliente.correo)
        )
        conexion.commit()
        cursor.close()
        conexion.close()
        return jsonify({ "ok": True, "mensaje": "Cliente registrado" })

    except Exception as e:
        return jsonify({ "ok": False, "mensaje": str(e) }), 500


@app.route('/api/ventas', methods=['GET'])
def get_ventas():
    try:
        conexion = get_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM ventas ORDER BY folio DESC")
        filas = cursor.fetchall()
        cursor.close()
        conexion.close()

        ventas = []
        for v in filas:
            ventas.append({
                "folio":    v[0],
                "cliente":  v[1],
                "producto": v[2],
                "fecha":    str(v[3]),
                "cantidad": v[4],
                "total":    float(v[5])
            })
        return jsonify(ventas)

    except Exception as e:
        return jsonify({ "error": str(e) }), 500


@app.route('/api/ventas', methods=['POST'])
def registrar_venta():
    data = request.get_json()
    id_cliente = data.get('id_cliente', '').strip()
    codigo     = data.get('codigo', '').strip()
    cantidad   = data.get('cantidad')

    if not all([id_cliente, codigo, cantidad]):
        return jsonify({ "ok": False, "mensaje": "Todos los campos son obligatorios" }), 400

    try:
        cantidad = int(cantidad)
        conexion = get_conexion()
        cursor = conexion.cursor()

        # Verificar producto y stock
        cursor.execute(
            "SELECT precio, cantidad, vendidos FROM productos WHERE codigo = %s",
            (codigo,)
        )
        prod = cursor.fetchone()
        if not prod:
            cursor.close()
            conexion.close()
            return jsonify({ "ok": False, "mensaje": "Producto no encontrado" }), 404

        precio, stock, vendidos = prod
        disponibles = stock - vendidos

        if cantidad > disponibles:
            cursor.close()
            conexion.close()
            return jsonify({
                "ok": False,
                "mensaje": f"Stock insuficiente. Disponibles: {disponibles}"
            }), 409

        total = float(precio) * cantidad
        fecha = datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            "UPDATE productos SET vendidos = vendidos + %s WHERE codigo = %s",
            (cantidad, codigo)
        )
        cursor.execute(
            "INSERT INTO ventas (id_cliente, codigo_producto, fecha, cantidad, total) VALUES (%s, %s, %s, %s, %s)",
            (id_cliente, codigo, fecha, cantidad, total)
        )
        conexion.commit()

        folio = cursor.lastrowid
        cursor.close()
        conexion.close()

        venta = Venta(folio, id_cliente, codigo, fecha, cantidad, total)
        return jsonify({
            "ok": True,
            "mensaje": "Venta registrada",
            "folio": venta.folio,
            "total": venta.total
        })

    except Exception as e:
        return jsonify({ "ok": False, "mensaje": str(e) }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conexion = get_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT COUNT(*) FROM productos")
        total_productos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM clientes")
        total_clientes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM ventas")
        row = cursor.fetchone()
        total_ventas = row[0]
        total_ingresos = float(row[1])

        cursor.close()
        conexion.close()

        return jsonify({
            "productos": total_productos,
            "clientes":  total_clientes,
            "ventas":    total_ventas,
            "ingresos":  total_ingresos
        })

    except Exception as e:
        return jsonify({ "error": str(e) }), 500
    
@app.route('/')
def index():
    return send_from_directory('.', 'ferreteria_flask.html')


if __name__ == '__main__':
    app.run(debug=True, port=8080)
