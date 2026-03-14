import sqlite3



#---------BASE DE DATOS----------#


class GestorDb():
    def __init__(self,nombre_db):
        self.conexion = sqlite3.connect(nombre_db)
        self.cursor = self.conexion.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")

        

    def crear_tabla(self):
        query1 = '''CREATE TABLE IF NOT EXISTS productos (
                             nombre_producto VARCHAR(20) NOT NULL,
                             cantidad_producto INTEGER NOT NULL,
                             precio_producto NUMERIC(10,2),
                             categoria_producto VARCHAR(20),
                             id_producto INTEGER PRIMARY KEY AUTOINCREMENT)'''
        
        self.cursor.execute(query1)
        self.conexion.commit()
        print('"DB : PRODUCTOS INCIALIZADA"')

    def producto_insertar_datos(self,filas:tuple):
        query = f'''INSERT INTO productos(nombre_producto,cantidad_producto,precio_producto,categoria_producto) VALUES(?,?,?,?)'''
        self.cursor.execute(query,filas)
        self.conexion.commit()
        print('"DB : DATOS INSERTADOS"')

    def producto_obtener_datos(self):
        query = f'''SELECT *FROM productos'''
        self.cursor.execute(query)
        datos = self.cursor.fetchall()
        print('"DB : DATOS OBTENIDOS"')
        return datos

    def producto_modificar_datos(self,id_fila,dato_objetivo:str,dato_nuevo:str):
        query = f'''UPDATE productos SET {dato_objetivo}=? WHERE id_producto=?'''
        self.cursor.execute(query,(dato_nuevo,id_fila))
        self.conexion.commit()
        print('"DB : DATOS MODIFICADOS"')

    def producto_eliminar_datos(self,id_fila):
        query = f'''DELETE FROM productos WHERE id_producto=?'''
        self.cursor.execute(query,(id_fila,))
        self.conexion.commit()
        print('"DB : DATOS ELIMINADOS"')  
    
    def producto_obtener_dato_id(self,id_fila):
        query = f'''SELECT *FROM productos WHERE id_producto=?'''
        self.cursor.execute(query,(id_fila,))
        datos = self.cursor.fetchone()
        print('"DB : DATOS OBTENIDOS POR ID"')  
        return datos

    def obtener_columnas_actuales(self,tabla):
        query= (f'''PRAGMA table_info({tabla});''')
        self.cursor.execute(query)
        columnas = self.cursor.fetchall()
        return columnas if columnas else None








#---------LOGICA----------#


class LogicaNegocio():
    def __init__(self,base_datos:GestorDb):
        self.base_datos = base_datos
        self.categorias = ['alimentos','cuidado personal','medicina']

    def validar_nombres(self,nombre):
            if not nombre:
                return 0
            if len(nombre) > 20:
                return 0
            return nombre.lower()
            
    def validar_cantidad(self,cantidad:str):
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                return 0
            return cantidad
        except ValueError:
            return 0
            
    def validar_precio(self,precio):
        if precio <= 0:
            return 0
        return precio
            
    def validar_categoria(self,categoria):
            categoria = categoria.lower()
            if categoria not in self.categorias:
                return 0
            if not categoria:
                return 0
            return categoria
            
    def registrar_producto(self,nombre,cantidad,precio,categoria):
        try:
            def validar_nombre(nombre):
                if not nombre:
                    return 0
                if len(nombre) > 20:
                    return 0
                return nombre.lower()
            
            def validar_cantidad(cantidad):
                if cantidad <= 0:
                    return 0
                return cantidad
            
            def validar_precio(precio):
                if precio <= 0:
                    return 0
                return precio
            
            def validar_categoria(categoria):
                categoria = categoria.lower()
                if categoria not in self.categorias:
                    return 0
                if not categoria:
                    return 0
                return categoria
            
            nombre_bool = validar_nombre(nombre)
            cantidad_bool = validar_cantidad(cantidad)
            precio_bool = validar_precio(precio)
            categoria_bool = validar_categoria(categoria)

            if all([nombre_bool,cantidad_bool,precio_bool,categoria_bool]):
                fila = (nombre,cantidad,precio,categoria)
                self.base_datos.producto_insertar_datos(fila)
                print('"LOGICA : DATOS VALIDADOS Y ENVIADOS *DB*"')
            else:
                print('"LOGICA : DATOS INVALIDOS-CANCELADO')  
        except ValueError as e:
            print(e)
        except TypeError as e:
            print(e)

    def modificar_producto(self,id_producto,dato_objetivo,dato_nuevo):
        busqueda = self.base_datos.producto_obtener_dato_id(id_producto)
        try:
            if busqueda:
                mapeo_datos = {'nombre_producto':self.validar_nombres,# segun el dato objetivo, vas a seleccionar la funcion que valida al dato correspondiente
                            'cantidad_producto':self.validar_cantidad,
                            'precio_producto':self.validar_precio,
                            'categoria_producto':self.validar_categoria}
                validacion = mapeo_datos[dato_objetivo](dato_nuevo)#nombre_producto(nombre) = True or False

                if validacion:
                    self.base_datos.producto_modificar_datos(id_producto,dato_objetivo,dato_nuevo)
                else:
                    print('"LOGICA : DATOS INVALIDOS-CANCELADO')  
            
            else:
                return 'producto no encontrado'
    
        except Exception as e:
            print(e)




#---------INTERFAZ----------#

base_datos = GestorDb('productos.db')
logica = LogicaNegocio(base_datos)
while True:
    opciones = ['1-Registrar productos','2-Ver productos','3-Modificar productos']
    [print(i) for i in opciones]
    op = int(input(": "))-1
    if op == 0:
        logica.registrar_producto(
            nombre=input("Escriba el nombre del producto: "),
            cantidad=int(input("Escriba la cantidad del producto: ")),
            precio=float(input("Escriba el precio del producto: ")),
            categoria=input("Escriba la categoria del producto: ")
        )
    if op == 1:
        datos = base_datos.producto_obtener_datos()
        for fila in datos:
            print(len(fila))
            for dato in fila:
                print(dato)
            print("-----")
    if op == 2:
        print(base_datos.obtener_columnas_actuales('productos.db'))
        logica.modificar_producto(
            id_producto=input("Esciba el id del producto a modificar\n:"),
            dato_objetivo=input('Escriba el dato a modificar\n:'),
            dato_nuevo=input("Escriba el dato nuevo\n:")
        )


