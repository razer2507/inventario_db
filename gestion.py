import sqlite3
import os 
import time
import tkinter as tk
from tkinter import messagebox,ttk


##CONEXION A DB 
def conexion():
    conexion = sqlite3.connect("productos.db")
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
                             nombre_producto VARCHAR(20) NOT NULL,
                             cantidad_producto INTEGER NOT NULL,
                             precio_producto NUMERIC(10,2),
                             categoria_producto VARCHAR(20),
                             id_producto INTEGER PRIMARY KEY AUTOINCREMENT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS ventas(
                   id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                   id_producto INTEGER,
                   FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
                   nombre_venta_cliente VARCHAR(20) NOT NULL,
                   cantidad_venta INTEGER NOT NULL,
                   ganancia_bruta_venta NUMERIC(10,2)
                   )''')
    conexion.commit()
    return conexion


#INTERFAZ

def registrar_producto_gui(db):
    cursor = db.cursor()
    #Creamos subventana
    ventana_registro = tk.Toplevel()
    ventana_registro.title("Registrar Productos")
    ventana_registro.geometry("300x400")
    

    #Mostramos el id proximo del producto a registrar
    cursor.execute("SELECT seq FROM sqlite_sequence WHERE name='productos'")
    resultado = cursor.fetchone()
    if resultado:
        ultimo_id = resultado[0]
        tk.Label(ventana_registro,text=f"PRODUCTO ID #{ultimo_id+1}").pack(pady=5)
    else:
        tk.Label(ventana_registro,text=f"PRODUCTO ID #{1}").pack(pady=5)



    #Campo: Nombre
    tk.Label(ventana_registro,text="Nombre del producto:").pack(pady=5)
    input_nombre = tk.Entry(ventana_registro)
    input_nombre.pack(pady=5)

    #Campo: Cantidad
    tk.Label(ventana_registro,text="Stock del producto:").pack(pady=5)
    input_cantidad = tk.Entry(ventana_registro)
    input_cantidad.pack(pady=5)

    #Campo: Precio
    tk.Label(ventana_registro,text="Precio del producto:").pack(pady=5)
    input_precio = tk.Entry(ventana_registro)
    input_precio.pack(pady=5)

    #Campo: Categoria
    tk.Label(ventana_registro,text="Categoria del producto:").pack(pady=5)
    input_categoria = tk.Entry(ventana_registro)
    input_categoria.pack(pady=5)


    
    #Guardar los datos usando.get()
    def guardar():
        try:
            nombre = input_nombre.get()
            cantidad = int(input_cantidad.get())
            precio = float(input_precio.get())
            categoria = input_categoria.get()

            if not nombre or not cantidad or not precio or not categoria:
                messagebox.showerror("ERROR: TODOS LOS CAMPOS SON OBLIGATORIOS")
                return 
            cursor.execute("INSERT INTO productos(nombre_producto,cantidad_producto,precio_producto,categoria_producto)VALUES(?,?,?,?)",(nombre,cantidad,precio,categoria))
            db.commit()
            messagebox.showinfo("GUARDADO EXITOSO")
            ventana_registro.destroy()

        except ValueError:
            messagebox.showerror("ERROR: ingrese un numero positivo valido")

    tk.Button(ventana_registro, text="Guardar Producto",command=guardar).pack(pady=20)


def ver_producto_gui(db):
    cursor = db.cursor()
    cursor.execute("SELECT id_producto,nombre_producto,precio_producto,cantidad_producto FROM productos")
    filas = cursor.fetchall()
   


    
    
    ventana = tk.Toplevel()
    frame_busqueda = tk.Frame(ventana)
    frame_busqueda.pack(pady=10)

    tk.Label(frame_busqueda, text="Buscar por nombre:").pack(side=tk.LEFT)
    input_busqueda = tk.Entry(frame_busqueda)
    input_busqueda.pack(side=tk.LEFT, padx=5)
    def buscar_productos():
        texto_entrada = input_busqueda.get()
        cursor.execute("SELECT id_producto,nombre_producto,precio_producto,cantidad_producto FROM PRODUCTOS WHERE nombre_producto LIKE ?",(f'%{texto_entrada}%',))
        filas = cursor.fetchall()
        for i in tabla.get_children():
            tabla.delete(i)
        for producto in filas:
            tabla.insert("",tk.END,values=producto)
        


    boton_buscar = tk.Button(ventana,text="BUSCAR",command=buscar_productos)
    boton_buscar.pack()


    ventana.title("VISUALIZAR PRODUCTOS")
    ventana.geometry("300x400")
    tabla = ttk.Treeview(ventana, columns=("id", "nombre", "precio", "cantidad"), show="headings")
    tabla.heading("id",text="ID")
    tabla.heading("nombre",text="NOMBRE")
    tabla.heading("precio",text="PRECIO")
    tabla.heading("cantidad",text="CANTIDAD")
    tabla.column("id",width=50,anchor="center")
    tabla.column("nombre",width=200,anchor="w")
    tabla.column("precio",width=100,anchor="e")
    tabla.column("cantidad",width=80,anchor='center')
    for producto in filas:
        tabla.insert("",tk.END,values=producto)
    
   

    


    tabla.pack(pady=20)

def eliminar_producto_gui(db):
    ventana = tk.Toplevel()
    ventana.title("VISUALIZAR PRODUCTOS")
    ventana.geometry("300x400")

    cursor = db.cursor()

    tk.Label(ventana,text="Id del producto:").pack(pady=5)
    input_id = tk.Entry(ventana)
    input_id.pack(pady=5)
    
    def confirmar_eliminacion():
        try:
            id_buscar = int(input_id.get())
            cursor.execute("SELECT id_producto FROM productos WHERE id_producto=?",(id_buscar,))
            consulta = cursor.fetchone()
            if consulta != None:
                cursor.execute("DELETE FROM productos WHERE id_producto=?",(id_buscar,))
                db.commit()
                messagebox.showinfo("EXITO","EL PRODUCTO HA SIDO BORRADO EXITOSAMENTE")
                ventana.destroy()
            else:
                messagebox.showerror("ERROR","ID NO ENCONTRADO EN LA BASE DE DATOS")

        except ValueError:
            messagebox.showerror(f"ERROR","EL ID DEBE SER UN NUMERO ENTERO POSITIVO")

    tk.Button(ventana,text="ELIMINAR",command=confirmar_eliminacion).pack()

def modificar_producto(db):
    cursor = db.cursor()


    ventana = tk.Toplevel()
    ventana.title("MODIFICAR PRODUCTOS")
    ventana.geometry("400x300")
    tk.Label(ventana,text="Id del producto:").pack(pady=5)
    input_id = tk.Entry(ventana)
    input_id.pack(pady=5)

    def confimar_modificacion():
        try:
            id = int(input_id.get())
            cursor.execute("SELECT nombre_producto,cantidad_producto,precio_producto,categoria_producto FROM productos WHERE id_producto=?",(id,))
            consulta = cursor.fetchone()
            if consulta != None:

                tk.Label(ventana,text="NOMBRE DEL PRODUCTO").pack(pady=5)
                input_nombre = tk.Entry(ventana)
                input_nombre.insert(0,consulta[0])
                input_nombre.pack(pady=5)
                
                tk.Label(ventana,text="CANTIDAD DEL PRODUCTO").pack(pady=5)
                input_cantidad = tk.Entry(ventana)
                input_cantidad.insert(0,consulta[1])
                input_cantidad.pack(pady=5)
                
                tk.Label(ventana,text="PRECIO DEL PRODUCTO").pack(pady=5)
                input_precio = tk.Entry(ventana)
                input_precio.insert(0,consulta[2])
                input_precio.pack(pady=5)
               

                tk.Label(ventana,text="CATEGORIA DEL PRODUCTO").pack(pady=5)
                input_categoria = tk.Entry(ventana)
                input_categoria.insert(0,consulta[3])
                input_categoria.pack(pady=5)
               

                def guardar_cambios():
                    nombre = input_nombre.get()
                    cantidad = int(input_cantidad.get())
                    precio = float(input_precio.get())
                    categoria = input_categoria.get()

                    cursor.execute('''UPDATE productos SET 
                               nombre_producto=?,
                               cantidad_producto=?,
                               precio_producto=?,
                               categoria_producto=?
                               WHERE id_producto=?''',
                               (nombre,
                                cantidad,
                                precio,
                                categoria,id))
                
                    messagebox.showinfo("EXITO","MODIFICACION EXITOSA")
                    db.commit()
                    ventana.destroy()
                tk.Button(ventana,text="CONFIRMAR",command=guardar_cambios).pack()   
            else:
                messagebox.showerror("ERROR","ID INVALIDO")
                ventana.destroy()

        except ValueError:
            messagebox.showerror("ERROR","EL ID DEBE SER UN NUMERO ENTERO POSITIVO")
            ventana.destroy()



    tk.Button(ventana,text="MODIFICAR",command=confimar_modificacion).pack()


  
def ventana_principal():
    db = conexion()
    root = tk.Tk()
    root.title("Gestion de inventario CRUD 1.0")
    root.geometry("400x300")


    #Titulo
    label_titulo = tk.Label(root, text="GESTION DE INVENTARIO CRUD 1.0",font=("Arial",16,"bold"))
    label_titulo.pack(pady=20)
    
    #Botonesss
    boton_registrar = tk.Button(root,text="Registrar nuevo producto",width=25,
                                command=lambda:registrar_producto_gui(db))
    boton_registrar.pack(pady=10)
    
    boton_visualizar = tk.Button(root,text="Ver productos",width=25,
                                 command=lambda:ver_producto_gui(db))
    boton_visualizar.pack(pady=10)

    boton_eliminar = tk.Button(root,text="Eliminar productos",width=25,
                               command=lambda:eliminar_producto_gui(db))
    boton_eliminar.pack(pady=10)

    boton_modificar = tk.Button(root,text="Modificar productos",width=25,
                                command=lambda:modificar_producto(db))
    boton_modificar.pack(pady=10)

    boton_salir = tk.Button(root,text="Salir",width=25,command=root.quit)
    boton_salir.pack(pady=10)

    

    root.mainloop()


ventana_principal()

