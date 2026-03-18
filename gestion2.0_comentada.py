import sqlite3
#comit1
# ==========================================
# CAPA DE BASE DE DATOS (DATA ACCESS LAYER)
# ==========================================
class GestorDb():
    """Se encarga exclusivamente de las operaciones SQL (CRUD)."""
    
    def __init__(self, nombre_db):
        # Establece conexión y activa las llaves foráneas para mantener integridad
        self.conexion = sqlite3.connect(nombre_db)
        self.cursor = self.conexion.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")

    def crear_tabla(self):
        """Define la estructura de la tabla 'productos' si no existe."""
        query1 = '''CREATE TABLE IF NOT EXISTS productos (
                             nombre_producto VARCHAR(20) NOT NULL,
                             cantidad_producto INTEGER NOT NULL,
                             precio_producto NUMERIC(10,2),
                             categoria_producto VARCHAR(20),
                             id_producto INTEGER PRIMARY KEY AUTOINCREMENT)'''
        self.cursor.execute(query1)
        self.conexion.commit()
        print('"DB : PRODUCTOS INICIALIZADA"')

    def producto_insertar_datos(self, filas: tuple):
        """Inserta una nueva fila de producto en la tabla."""
        query = f'''INSERT INTO productos(nombre_producto,cantidad_producto,precio_producto,categoria_producto) VALUES(?,?,?,?)'''
        self.cursor.execute(query, filas)
        self.conexion.commit()
        print('"DB : DATOS INSERTADOS"')

    def producto_obtener_datos(self):
        """Recupera todos los registros de la tabla productos."""
        query = f'''SELECT * FROM productos'''
        self.cursor.execute(query)
        datos = self.cursor.fetchall()
        print('"DB : DATOS OBTENIDOS"')
        return datos

    def producto_modificar_datos(self, id_fila, dato_objetivo: str, dato_nuevo: str):
        """Actualiza un campo específico de un producto usando su ID."""
        # Nota: dato_objetivo se inyecta con f-string porque los nombres de columna no aceptan ?
        query = f'''UPDATE productos SET {dato_objetivo}=? WHERE id_producto=?'''
        self.cursor.execute(query, (dato_nuevo, id_fila))
        self.conexion.commit()
        print('"DB : DATOS MODIFICADOS"')

    def producto_obtener_dato_id(self, id_fila):
        """Busca y retorna un producto específico por su ID."""
        query = f'''SELECT * FROM productos WHERE id_producto=?'''
        self.cursor.execute(query, (id_fila,))
        datos = self.cursor.fetchone()
        print('"DB : DATOS OBTENIDOS POR ID"')  
        return datos

    def obtener_columnas_actuales(self, tabla):
        """Devuelve la estructura (columnas) de una tabla específica."""
        query = (f'''PRAGMA table_info({tabla});''')
        self.cursor.execute(query)
        columnas = self.cursor.fetchall()
        return columnas if columnas else None


# ==========================================
# CAPA DE LÓGICA DE NEGOCIO (BUSINESS LOGIC)
# ==========================================
class LogicaNegocio():
    """Contiene las reglas de validación y procesos antes de tocar la DB."""
    
    def __init__(self, base_datos: GestorDb):
        # Recibe la instancia de la base de datos (Inyección de dependencias)
        self.base_datos = base_datos
        self.categorias = ['alimentos', 'cuidado personal', 'medicina']

    # --- Métodos de validación individuales ---
    
    def validar_nombres(self, nombre):
        """Valida que el nombre no esté vacío y no supere 20 caracteres."""
        if not nombre or len(str(nombre)) > 20:
            return 0
        return str(nombre).lower()
            
    def validar_cantidad(self, cantidad):
        """Intenta convertir a entero y verifica que sea mayor a 0."""
        try:
            cantidad = int(cantidad)
            return cantidad if cantidad > 0 else 0
        except (ValueError, TypeError):
            return 0
            
    def validar_precio(self, precio):
        """Intenta convertir a flotante y verifica que sea mayor a 0."""
        try:
            precio = float(precio)
            return precio if precio > 0 else 0
        except (ValueError, TypeError):
            return 0
            
    def validar_categoria(self, categoria):
        """Verifica que la categoría esté dentro de la lista permitida."""
        if not categoria:
            return 0
        categoria = str(categoria).lower()
        return categoria if categoria in self.categorias else 0
            
    def registrar_producto(self, nombre, cantidad, precio, categoria):
        """Orquesta la validación masiva antes de insertar un nuevo producto."""
        try:
            # Ejecutamos las validaciones
            n = self.validar_nombres(nombre)
            cant = self.validar_cantidad(cantidad)
            p = self.validar_precio(precio)
            cat = self.validar_categoria(categoria)

            # Si todos son distintos de 0 (True), se procede
            if all([n, cant, p, cat]):
                fila = (n, cant, p, cat)
                self.base_datos.producto_insertar_datos(fila)
                print('"LOGICA : DATOS VALIDADOS Y ENVIADOS"')
            else:
                print('"LOGICA : DATOS INVALIDOS - REGISTRO CANCELADO"')  
        except Exception as e:
            print(f"Error en registro: {e}")

    def modificar_producto(self, id_producto, dato_objetivo, dato_nuevo):
        """Busca un producto y valida el nuevo dato antes de actualizarlo."""
        busqueda = self.base_datos.producto_obtener_dato_id(id_producto)
        try:
            if busqueda:
                # Diccionario de Despacho: Mapea la columna con su función validadora
                mapeo_validaciones = {
                    'nombre_producto': self.validar_nombres,
                    'cantidad_producto': self.validar_cantidad,
                    'precio_producto': self.validar_precio,
                    'categoria_producto': self.validar_categoria
                }
                
                # Seleccionamos y ejecutamos la validación correspondiente
                if dato_objetivo in mapeo_validaciones:
                    validacion = mapeo_validaciones[dato_objetivo](dato_nuevo)
                    
                    if validacion:
                        self.base_datos.producto_modificar_datos(id_producto, dato_objetivo, validacion)
                    else:
                        print('"LOGICA : EL NUEVO DATO ES INVÁLIDO"')
                else:
                    print('"LOGICA : COLUMNA NO EXISTE"')
            else:
                print('"LOGICA : PRODUCTO NO ENCONTRADO"')
        except Exception as e:
            print(f"Error en modificación: {e}")


# ==========================================
# CAPA DE INTERFAZ DE USUARIO (CLI)
# ==========================================

# Inicialización de objetos
db = GestorDb('productos.db')
db.crear_tabla() # Aseguramos que la tabla exista al arrancar
logica = LogicaNegocio(db)

while True:
    print("\n--- MENÚ DE INVENTARIO ---")
    opciones = ['1-Registrar productos', '2-Ver productos', '3-Modificar productos', '4-Salir']
    [print(i) for i in opciones]
    
    try:
        op = int(input(": ")) - 1
    except ValueError:
        continue

    if op == 0:
        logica.registrar_producto(
            nombre=input("Nombre: "),
            cantidad=input("Cantidad: "), # Se pasa como string, la lógica lo convierte
            precio=input("Precio: "),
            categoria=input("Categoría: ")
        )
    elif op == 1:
        # Llamada correcta a la función con paréntesis
        datos = db.producto_obtener_datos()
        for fila in datos:
            print(f"ID: {fila[4]} | Nombre: {fila[0]} | Stock: {fila[1]} | Precio: ${fila[2]} | Cat: {fila[3]}")
    elif op == 2:
        # Mostramos las columnas para ayudar al usuario
        print("Columnas disponibles:", [col[1] for col in db.obtener_columnas_actuales('productos')])
        logica.modificar_producto(
            id_producto=input("ID del producto: "),
            dato_objetivo=input("Nombre de la columna a cambiar: "),
            dato_nuevo=input("Nuevo valor: ")
        )
    elif op == 3:
        break
