import sqlite3
import os 
import time
import tkinter as tk
from tkinter import messagebox
def clear():
    os.system('cls') if os.name == 'nt' else os.system('clear')


def conexion():
    conexion = sqlite3.connect("productos.db")
    cursor = conexion.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
                             nombre_producto VARCHAR(20) NOT NULL,
                             cantidad_producto INTEGER NOT NULL,
                             precio_producto NUMERIC(10,2),
                             categoria_producto VARCHAR(20),
                             id_producto INTEGER PRIMARY KEY AUTOINCREMENT)''')
    conexion.commit()
    return conexion

def getchar():
    input("PRESIONE ENTER PARA CONTINUAR")

def registrar_producto(conexion):
    clear()
    cursor = conexion.cursor()
    while True:
        try:
            clear()
            print("CONTROL+C PARA SALIR")
            nombre_producto = input("Escriba el nombre del producto\n:")
            cantidad_producto = int(input("Escriba el stock del producto\n:"))
            precio_producto = float(input("Escriba el precio del producto\n:"))
            categoria_producto = input("Escriba la categoria del producto\n:")
            clear()
            
            print(f"---PRODUCTO---\nNOMBRE:{nombre_producto}\nCANTIDAD:{cantidad_producto}\nPRECIO:{precio_producto}\nCATEGORIA:{categoria_producto}\n-----------")
            confirmacion = input("Desea agregar el producto?(s/n)")
            if confirmacion.lower() == 's':
                cursor.execute('''INSERT INTO productos(nombre_producto,cantidad_producto,precio_producto,categoria_producto) VALUES(?,?,?,?)''',(nombre_producto,cantidad_producto,precio_producto,categoria_producto))
                conexion.commit()
                print("PRODUCTO AGREGADO CON EXITO")
                input("PRESIONE ENTER PARA CONTINUAR")
                break

            else:
                conexion.rollback()#limpia la operacion del cursor.execute()
                continue

        except ValueError:
            print("ERROR: DATO INVALIDO")
        except KeyboardInterrupt:
            break

def ver_producto(conexion):
    clear()
    cursor = conexion.cursor()
    cursor.execute('''SELECT *FROM productos''')
    filas = cursor.fetchall()

    header = f"{'ID':<5} | {'NOMBRE':<20} | {'CANT':<8} | {'PRECIO':<12} | {'CATEGORÍA':<15}"
    
    print("\n" + header)
    print("-" * len(header)) 
    for i in filas:
        print(f"{i[4]:<5} | {i[0]:<20.20} | {i[1]:<8} | ${i[2]:<11.2f} | {i[3]:<15}")
    
    print("-" * len(header) + "\n")

    input("PRESIONE ENTER PARA SALIR")
    clear()

def editar_producto(conexion):
    clear()
    cursor = conexion.cursor()
    while True:
        try:
            ver_producto(conexion)
            cursor.execute('''SELECT id_producto FROM productos''')
            ids = list(map(lambda a: a[0],cursor.fetchall()))
            id = int(input("Escriba el id del producto a modificar(CTRL+C PARA SALIR)\n:"))
            if id in ids:
                clear()
                cursor.execute('''SELECT *FROM productos WHERE id_producto=?''',(id,))
                datos = cursor.fetchall()
                modificacion = int(input(f"PRODUCTO ENCONTRADO\n1-Nombre: {datos[0][0]}\n2-Cantidad: {datos[0][1]}\n3-Precio: {datos[0][2]}\n4-Categoria: {datos[0][3]}\nEscriba el dato a modificar(CTRL+C PARA SALIR): "))
                match modificacion:
                    case 1:
                        clear()
                        nuevo_nombre = input("Escriba el nuevo nombre\n:")
                        cursor.execute("UPDATE productos SET nombre_producto=? WHERE id_producto=?",(nuevo_nombre,id))
                        getchar()
                        clear()
                    case 2:
                        clear()
                        nueva_cantidad = int(input("Escriba la nueva cantidad"))
                        cursor.execute("UPDATE productos SET cantidad_producto=? WHERE id_producto=?",(nueva_cantidad,id))
                        getchar()
                        clear() 
                    case 3:
                        clear()
                        nuevo_precio = int(input("Escriba el nuevo precio\n:"))
                        cursor.execute("UPDATE productos SET precio_producto=? WHERE id_producto=?",(nuevo_precio,id))
                        getchar() 
                        clear()     
                    case 4:
                        clear()
                        nueva_categoria = input("Escriba la nueva categoria \n:")
                        cursor.execute("UPDATE productos SET categoria_producto=? WHERE id_producto=?",(nueva_categoria,id)) 
                        getchar() 
                        clear()
                conexion.commit()   
                clear()

            else:
                clear()
                print(f"ID INVALIDO:\nRANGO VALIDO {ids[0]} - {len(ids)+1}")
                input("PRESIONE ENTER PARA REINTENTAR(CTRL+C PARA SALIR)")
                clear()
        except ValueError:
            clear()
            print("ERROR:INGRESE UN NUMERO ENTERO POSITIVO")
            input("PRESIONE ENTER PARA CONTINUAR")
        except KeyboardInterrupt:
            clear()
            break

def eliminar_producto(conexion):
    clear()
    cursor = conexion.cursor()
    
    while True:
        try:
            ver_producto(conexion)
            cursor.execute('''SELECT id_producto FROM productos''')
            ids = list(map(lambda a: a[0],cursor.fetchall()))
            id = int(input("Escriba el id del producto a eliminar(CTRL+C PARA SALIR)\n:"))
            clear()
            if id in ids:
                cursor.execute('''SELECT *FROM productos WHERE id_producto=?''',(id,))
                datos = cursor.fetchall()
                modificacion = input(f"PRODUCTO ENCONTRADO\n1-Nombre: {datos[0][0]}\n2-Cantidad: {datos[0][1]}\n3-Precio: {datos[0][2]}\n4-Categoria: {datos[0][3]}\nConfirma que quiere eliminar?(s/n) (CTRL+C PARA SALIR): ")
                if modificacion.lower() == 's':
                    clear()
                    cursor.execute("DELETE FROM productos WHERE id_producto=?",(id,))
                    print("ELIMINADO CORRECTAMENTE")
                    conexion.commit()
                    getchar()
                    clear()
                else:
                    continue
            else:
                clear()
                print(f"ID INVALIDO:\nRANGO VALIDO {ids[0]} - {len(ids)+1}")
                input("PRESIONE ENTER PARA REINTENTAR(CTRL+C PARA SALIR)")
                clear()
        except ValueError:
            clear()
            print("ERROR:INGRESE UN NUMERO ENTERO POSITIVO")
            input("PRESIONE ENTER PARA CONTINUAR")
            clear()
        except KeyboardInterrupt:
            clear()
            break





#INTERFAZ

def registrar_producto_gui(db):
    cursor = db.cursor()
    #Creamos subventana
    ventana_registro = tk.Toplevel()
    ventana_registro.title("Registrar Productos")
    ventana_registro.geometry("300x400")
    

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
    boton_salir = tk.Button(root,text="Salir",width=25,command=root.quit)
    boton_salir.pack(pady=10)



    root.mainloop()


ventana_principal()

