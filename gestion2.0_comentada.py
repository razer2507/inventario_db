import sqlite3
import tkinter as tk
from tkinter import messagebox,ttk
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
                             nombre_producto VARCHAR(50) NOT NULL,
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
        if not nombre or len(str(nombre)) > 50:
            print('NOMBRE: EXCEDE LOS 20 CARACTERES')
            return 0
        return str(nombre).lower()
            
    def validar_cantidad(self, cantidad):
        """Intenta convertir a entero y verifica que sea mayor a 0."""
        try:
            cantidad = int(cantidad)
            return cantidad if cantidad > 0 else 0
        except (ValueError, TypeError):
            print("CANTIDAD: DEBE SER UN NUMERO ENTERO MAYOR A 0")
            return 0
            
    def validar_precio(self, precio):
        """Intenta convertir a flotante y verifica que sea mayor a 0."""
        try:
            precio = float(precio)
            return precio if precio > 0 else 0
        except (ValueError, TypeError):
            print("PRECIO: DEBE SER UN NUMERO ENTERO MAYOR A 0")
            return 0
            
    def validar_categoria(self, categoria):
        """Verifica que la categoría esté dentro de la lista permitida."""
        categoria = str(categoria).lower()
        if not categoria:
            print("CATEGORIA: LA CATEGORIA DEBE ESTAR DENTRO DE LAS CATEGORIAS PERMITIDAS")
            return 0
        
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
                return True
            else:
                print('"LOGICA : DATOS INVALIDOS - REGISTRO CANCELADO"')
                return False  
        except Exception as e:
            print(f"Error en registro: {e}")
            return False

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
                        return True
                    else:
                        print('"LOGICA : EL NUEVO DATO ES INVÁLIDO"')
                        return False
                else:
                    print('"LOGICA : COLUMNA NO EXISTE"')
                    return False
            else:
                print('"LOGICA : PRODUCTO NO ENCONTRADO"')
                return False
        except Exception as e:
            print(f"Error en modificación: {e}")
            return False


# ==========================================
# CAPA DE INTERFAZ DE USUARIO (CLI)
# ==========================================


class InterfazGrafica(tk.Tk):
    def __init__(self, logica: LogicaNegocio):
        super().__init__()
        self.logica = logica  # Recibimos la lógica (Inyección de dependencias)
        self.title("Gestión de Inventario")
        self.geometry("600x400")
        
        self.crear_widgets()

    def crear_widgets(self):
        # Aquí crearíamos los labels, botones y la tabla
        tk.Label(self, text="Nombre:").pack()
        self.entrada_nombre = tk.Entry(self)
        self.entrada_nombre.pack()

        tk.Label(self, text="Cantidad:").pack()
        self.entrada_cantidad = tk.Entry(self)
        self.entrada_cantidad.pack()

        tk.Label(self, text="Precio:").pack()
        self.entrada_precio = tk.Entry(self)
        self.entrada_precio.pack()

        tk.Label(self, text="Categoria:").pack()
        self.entrada_categoria = tk.Entry(self)
        self.entrada_categoria.pack()

        
        # Botón que dispara la acción
        tk.Button(self, text="Registrar", command=self.ejecutar_registro).pack()

    def ejecutar_registro(self):
        # Extraemos los datos de la GUI y los mandamos a la lógica
        nombre = self.entrada_nombre.get()
        cantidad = self.entrada_cantidad.get()
        precio = self.entrada_precio.get()
        categoria = self.entrada_categoria.get()


        operacion = self.logica.registrar_producto(nombre,cantidad,precio,categoria)
        messagebox.showinfo("Exito","Producto registrado exitosamente")if operacion else messagebox.showerror("Error","Producto invalido")


        #Limpiamos la entrada luego de que el user presione el boton
        self.entrada_nombre.delete(0,tk.END)
        self.entrada_cantidad.delete(0,tk.END)
        self.entrada_precio.delete(0,tk.END)
        self.entrada_categoria.delete(0,tk.END)



'''
nombre_producto VARCHAR(20) NOT NULL,
cantidad_producto INTEGER NOT NULL,
precio_producto NUMERIC(10,2),
categoria_producto VARCHAR(20),
id_producto INTEGER PRIMARY KEY AUTOINCREMENT)
'''

db = GestorDb('productos.db')
logica = LogicaNegocio(db)
interfaz = InterfazGrafica(logica)
interfaz.mainloop()
