import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from datos import (
    ARCHIVO,
    COLUMNAS,
    CORREO_COORDINADOR,
    crear_libro,
    crear_cotizacion,
    enviar_correo,
    guardar,
    leer,
)
crear_libro()

ventana = tk.Tk()
ventana.title("Sistema de Inventario")
ventana.geometry("800x500")

pestanas = ttk.Notebook(ventana)
pestanas.pack(fill="both", expand=True)

# PESTAÑA PRODUCTOS
marco_productos = ttk.Frame(pestanas)
pestanas.add(marco_productos, text="Productos")

formulario = ttk.Frame(marco_productos)
formulario.pack(pady=10)

ttk.Label(formulario, text="Nombre:").pack(side="left", padx=4)
entrada_nombre = ttk.Entry(formulario, width=18)
entrada_nombre.pack(side="left")

ttk.Label(formulario, text="Precio:").pack(side="left", padx=4)
entrada_precio = ttk.Entry(formulario, width=10)
entrada_precio.pack(side="left")

ttk.Label(formulario, text="Existencia:").pack(side="left", padx=4)
entrada_existencia = ttk.Entry(formulario, width=10)
entrada_existencia.pack(side="left")

tabla_productos = ttk.Treeview(marco_productos, columns=COLUMNAS["productos"], show="headings")
for columna in COLUMNAS["productos"]:
    tabla_productos.heading(columna, text=columna.capitalize())
tabla_productos.pack(fill="both", expand=True, padx=10, pady=10)


def listar_productos():
    tabla_productos.delete(*tabla_productos.get_children())
    for fila in leer("productos"):
        tabla_productos.insert("", "end", values=fila)


def leer_casillas():
    """Lee y valida las casillas. Devuelve [nombre, precio, existencia] o None si hay error."""
    nombre = entrada_nombre.get().strip()
    if nombre == "":
        messagebox.showerror("Error", "Escriba el nombre del producto.")
        return None
    try:
        precio = float(entrada_precio.get())
        existencia = int(entrada_existencia.get())
    except ValueError:
        messagebox.showerror("Error", "El precio debe ser número y la existencia un número entero.")
        return None
    if precio < 0 or existencia < 0:
        messagebox.showerror("Error", "El precio y la existencia no pueden ser negativos.")
        return None
    return [nombre, precio, existencia]


def limpiar_casillas():
    entrada_nombre.delete(0, "end")
    entrada_precio.delete(0, "end")
    entrada_existencia.delete(0, "end")


def agregar_producto():
    datos = leer_casillas()
    if datos is None:
        return
    filas = leer("productos")
    for fila in filas:
        if fila[0].lower() == datos[0].lower():
            messagebox.showerror("Error", "Ya existe un producto con ese nombre.")
            return
    filas.append(datos)
    guardar("productos", filas)
    limpiar_casillas()
    listar_productos()


def mostrar_en_casillas(evento):
    """Al hacer clic en una fila de la tabla, pasa sus datos a las casillas."""
    seleccion = tabla_productos.selection()
    if not seleccion:
        return
    fila = leer("productos")[tabla_productos.index(seleccion[0])]
    limpiar_casillas()
    entrada_nombre.insert(0, fila[0])
    entrada_precio.insert(0, fila[1])
    entrada_existencia.insert(0, fila[2])


def editar_producto():
    seleccion = tabla_productos.selection()
    if not seleccion:
        messagebox.showerror("Error", "Primero seleccione un producto de la tabla.")
        return
    datos = leer_casillas()
    if datos is None:
        return
    posicion = tabla_productos.index(seleccion[0])
    filas = leer("productos")
    for i, fila in enumerate(filas):
        if i != posicion and fila[0].lower() == datos[0].lower():
            messagebox.showerror("Error", "Ya existe otro producto con ese nombre.")
            return
    filas[posicion] = datos
    guardar("productos", filas)
    limpiar_casillas()
    listar_productos()


def eliminar_producto():
    seleccion = tabla_productos.selection()
    if not seleccion:
        messagebox.showerror("Error", "Primero seleccione un producto de la tabla.")
        return
    posicion = tabla_productos.index(seleccion[0])
    filas = leer("productos")
    nombre = filas[posicion][0]
    if messagebox.askyesno("Confirmar", "¿Eliminar el producto '" + nombre + "'?"):
        filas.pop(posicion)
        guardar("productos", filas)
        limpiar_casillas()
        listar_productos()

def enviar_cotizacion():
    seleccion = tabla_productos.selection()
    if not seleccion:
        messagebox.showerror("Error", "Primero seleccione el producto de la tabla.")
        return
    nombre_producto, precio, existencia = leer("productos")[tabla_productos.index(seleccion[0])]

    cliente = simpledialog.askstring("Cotización", "Nombre del cliente:")
    if cliente is None or cliente.strip() == "":
        return
    correo = simpledialog.askstring("Cotización", "Correo del cliente:")
    if correo is None:
        return
    cliente = cliente.strip()
    correo = correo.strip()
    if "@" not in correo or "." not in correo:
        messagebox.showerror("Error", "Escriba un correo válido.")
        return

    try:
        ruta = crear_cotizacion(cliente, nombre_producto, precio)
        enviar_correo(
            correo,
            "Cotización de " + nombre_producto,
            "Estimado " + cliente + ", adjuntamos la cotización solicitada.",
            ruta,
        )
        messagebox.showinfo("Listo", "Cotización enviada a " + correo)
    except Exception as error:
        messagebox.showerror("Error", "No se pudo enviar la cotización:\n" + str(error))

tabla_productos.bind("<<TreeviewSelect>>", mostrar_en_casillas)

botones_productos = ttk.Frame(marco_productos)
botones_productos.pack()
ttk.Button(botones_productos, text="Agregar", command=agregar_producto).pack(side="left", padx=4)
ttk.Button(botones_productos, text="Editar", command=editar_producto).pack(side="left", padx=4)
ttk.Button(botones_productos, text="Eliminar", command=eliminar_producto).pack(side="left", padx=4)
ttk.Button(botones_productos, text="Enviar cotización", command=enviar_cotizacion).pack(side="left", padx=4)
listar_productos()

# PESTAÑA CLIENTES
marco_clientes = ttk.Frame(pestanas)
pestanas.add(marco_clientes, text="Clientes")

formulario_clientes = ttk.Frame(marco_clientes)
formulario_clientes.pack(pady=10)

ttk.Label(formulario_clientes, text="Nombre:").pack(side="left", padx=4)
cliente_nombre = ttk.Entry(formulario_clientes, width=18)
cliente_nombre.pack(side="left")

ttk.Label(formulario_clientes, text="NIT:").pack(side="left", padx=4)
cliente_nit = ttk.Entry(formulario_clientes, width=12)
cliente_nit.pack(side="left")

ttk.Label(formulario_clientes, text="Dirección:").pack(side="left", padx=4)
cliente_direccion = ttk.Entry(formulario_clientes, width=24)
cliente_direccion.pack(side="left")

tabla_clientes = ttk.Treeview(marco_clientes, columns=COLUMNAS["clientes"], show="headings")
for columna in COLUMNAS["clientes"]:
    tabla_clientes.heading(columna, text=columna.capitalize())
tabla_clientes.pack(fill="both", expand=True, padx=10, pady=10)


def listar_clientes():
    tabla_clientes.delete(*tabla_clientes.get_children())
    for fila in leer("clientes"):
        tabla_clientes.insert("", "end", values=fila)


def leer_casillas_cliente():
    """Devuelve [nombre, nit, direccion] o None si falta algún dato."""
    nombre = cliente_nombre.get().strip()
    nit = cliente_nit.get().strip()
    direccion = cliente_direccion.get().strip()
    if nombre == "" or nit == "" or direccion == "":
        messagebox.showerror("Error", "Complete nombre, NIT y dirección.")
        return None
    return [nombre, nit, direccion]


def limpiar_casillas_cliente():
    cliente_nombre.delete(0, "end")
    cliente_nit.delete(0, "end")
    cliente_direccion.delete(0, "end")


def cliente_repetido(datos, posicion_actual=-1):
                                                  #True si ya existe otro cliente con el mismo nombre o el mismo NIT.
    for i, fila in enumerate(leer("clientes")):
        if i == posicion_actual:
            continue
        if fila[0].lower() == datos[0].lower():
            messagebox.showerror("Error", "Ya existe un cliente con ese nombre.")
            return True
        if str(fila[1]) == datos[1]:
            messagebox.showerror("Error", "Ya existe un cliente con ese NIT.")
            return True
    return False


def agregar_cliente():
    datos = leer_casillas_cliente()
    if datos is None or cliente_repetido(datos):
        return
    filas = leer("clientes")
    filas.append(datos)
    guardar("clientes", filas)
    limpiar_casillas_cliente()
    listar_clientes()


def mostrar_cliente_en_casillas(evento):
    seleccion = tabla_clientes.selection()
    if not seleccion:
        return
    fila = leer("clientes")[tabla_clientes.index(seleccion[0])]
    limpiar_casillas_cliente()
    cliente_nombre.insert(0, fila[0])
    cliente_nit.insert(0, fila[1])
    cliente_direccion.insert(0, fila[2])


def editar_cliente():
    seleccion = tabla_clientes.selection()
    if not seleccion:
        messagebox.showerror("Error", "Primero seleccione un cliente de la tabla.")
        return
    datos = leer_casillas_cliente()
    posicion = tabla_clientes.index(seleccion[0])
    if datos is None or cliente_repetido(datos, posicion):
        return
    filas = leer("clientes")
    filas[posicion] = datos
    guardar("clientes", filas)
    limpiar_casillas_cliente()
    listar_clientes()


def eliminar_cliente():
    seleccion = tabla_clientes.selection()
    if not seleccion:
        messagebox.showerror("Error", "Primero seleccione un cliente de la tabla.")
        return
    posicion = tabla_clientes.index(seleccion[0])
    filas = leer("clientes")
    nombre = filas[posicion][0]
    if messagebox.askyesno("Confirmar", "¿Eliminar el cliente '" + nombre + "'?"):
        filas.pop(posicion)
        guardar("clientes", filas)
        limpiar_casillas_cliente()
        listar_clientes()


tabla_clientes.bind("<<TreeviewSelect>>", mostrar_cliente_en_casillas)

botones_clientes = ttk.Frame(marco_clientes)
botones_clientes.pack()
ttk.Button(botones_clientes, text="Agregar", command=agregar_cliente).pack(side="left", padx=4)
ttk.Button(botones_clientes, text="Editar", command=editar_cliente).pack(side="left", padx=4)
ttk.Button(botones_clientes, text="Eliminar", command=eliminar_cliente).pack(side="left", padx=4)

listar_clientes()

# PESTAÑA PEDIDOS
marco_pedidos = ttk.Frame(pestanas)
pestanas.add(marco_pedidos, text="Pedidos")

formulario_pedidos = ttk.Frame(marco_pedidos)
formulario_pedidos.pack(pady=10)

ttk.Label(formulario_pedidos, text="Cliente:").pack(side="left", padx=4)
combo_cliente = ttk.Combobox(formulario_pedidos, width=18, state="readonly")
combo_cliente.pack(side="left")

ttk.Label(formulario_pedidos, text="Producto:").pack(side="left", padx=4)
combo_producto = ttk.Combobox(formulario_pedidos, width=18, state="readonly")
combo_producto.pack(side="left")

ttk.Label(formulario_pedidos, text="Cantidad:").pack(side="left", padx=4)
pedido_cantidad = ttk.Entry(formulario_pedidos, width=8)
pedido_cantidad.pack(side="left")

columnas_tabla_pedidos = ["no."] + COLUMNAS["pedidos"]
tabla_pedidos = ttk.Treeview(marco_pedidos, columns=columnas_tabla_pedidos, show="headings")
for columna in columnas_tabla_pedidos:
    tabla_pedidos.heading(columna, text=columna.capitalize())
tabla_pedidos.column("no.", width=50)
tabla_pedidos.pack(fill="both", expand=True, padx=10, pady=10)


def actualizar_listas_pedidos():
    """Llena las listas desplegables con los clientes y productos actuales."""
    combo_cliente["values"] = [fila[0] for fila in leer("clientes")]
    combo_producto["values"] = [fila[0] for fila in leer("productos")]


def listar_pedidos():
    tabla_pedidos.delete(*tabla_pedidos.get_children())
    numero = 1
    for fila in leer("pedidos"):
        tabla_pedidos.insert("", "end", values=[numero] + fila)
        numero += 1


def agregar_pedido():
    cliente = combo_cliente.get()
    producto = combo_producto.get()
    if cliente == "" or producto == "":
        messagebox.showerror("Error", "Elija un cliente y un producto.")
        return
    try:
        cantidad = int(pedido_cantidad.get())
    except ValueError:
        messagebox.showerror("Error", "La cantidad debe ser un número entero.")
        return
    if cantidad <= 0:
        messagebox.showerror("Error", "La cantidad debe ser mayor que cero.")
        return

    productos = leer("productos")
    valor = None
    for fila in productos:
        if fila[0] == producto:
            if fila[2] < cantidad:
                messagebox.showerror("Error", "Existencia insuficiente. Solo hay " + str(fila[2]) + ".")
                return
            fila[2] = fila[2] - cantidad          # descontar del inventario
            valor = round(fila[1] * cantidad, 2)  # precio x cantidad
    if valor is None:
        messagebox.showerror("Error", "El producto ya no existe.")
        return

    guardar("productos", productos)
    pedidos = leer("pedidos")
    pedidos.append([cliente, producto, cantidad, valor])
    guardar("pedidos", pedidos)

    pedido_cantidad.delete(0, "end")
    listar_pedidos()
    listar_productos()


def eliminar_pedido():
    seleccion = tabla_pedidos.selection()
    if not seleccion:
        messagebox.showerror("Error", "Primero seleccione un pedido de la tabla.")
        return
    posicion = tabla_pedidos.index(seleccion[0])
    pedidos = leer("pedidos")
    pedido = pedidos[posicion]
    if messagebox.askyesno("Confirmar", "¿Eliminar el pedido número " + str(posicion + 1) + "?"):
        pedidos.pop(posicion)
        productos = leer("productos")
        for fila in productos:
            if fila[0] == pedido[1]:
                fila[2] = fila[2] + pedido[2]     # devolver la existencia
        guardar("productos", productos)
        guardar("pedidos", pedidos)
        listar_pedidos()
        listar_productos()


def al_cambiar_pestana(evento):
    actualizar_listas_pedidos()
    listar_pedidos()


pestanas.bind("<<NotebookTabChanged>>", al_cambiar_pestana)

botones_pedidos = ttk.Frame(marco_pedidos)
botones_pedidos.pack()
ttk.Button(botones_pedidos, text="Agregar pedido", command=agregar_pedido).pack(side="left", padx=4)
ttk.Button(botones_pedidos, text="Eliminar pedido", command=eliminar_pedido).pack(side="left", padx=4)

actualizar_listas_pedidos()
listar_pedidos()


# PESTAÑA INFORMES
marco_informes = ttk.Frame(pestanas)
pestanas.add(marco_informes, text="Informes")

botones_informes = ttk.Frame(marco_informes)
botones_informes.pack(pady=10)

texto_informe = tk.Text(marco_informes, height=20)
texto_informe.pack(fill="both", expand=True, padx=10, pady=10)


def mostrar_informe(titulo, lineas):
    texto_informe.delete("1.0", "end")
    texto_informe.insert("end", titulo + "\n\n")
    if len(lineas) == 0:
        texto_informe.insert("end", "(Todavía no hay ventas)")
    for linea in lineas:
        texto_informe.insert("end", linea + "\n")


def total_por_cliente():
    totales = {}
    for fila in leer("pedidos"):
        cliente = fila[0]
        valor = fila[3]
        totales[cliente] = totales.get(cliente, 0) + valor

    lineas = []
    suma_general = 0
    for cliente, total in totales.items():
        lineas.append(cliente + ": Q" + format(total, ",.2f"))
        suma_general = suma_general + total
    if len(lineas) > 0:
        lineas.append("")
        lineas.append("TOTAL GENERAL: Q" + format(suma_general, ",.2f"))
    mostrar_informe("TOTAL DE VENTA POR CLIENTE", lineas)


def total_por_producto():
    unidades = {}
    totales = {}
    for fila in leer("pedidos"):
        producto = fila[1]
        cantidad = fila[2]
        valor = fila[3]
        unidades[producto] = unidades.get(producto, 0) + cantidad
        totales[producto] = totales.get(producto, 0) + valor

    lineas = []
    for producto in totales:
        lineas.append(producto + ": " + str(unidades[producto]) + " unidades, Q" + format(totales[producto], ",.2f"))
    mostrar_informe("TOTAL DE VENTAS POR PRODUCTO", lineas)


ttk.Button(botones_informes, text="Total de venta por cliente", command=total_por_cliente).pack(side="left", padx=4)
ttk.Button(botones_informes, text="Total de ventas por producto", command=total_por_producto).pack(side="left", padx=4)


# PESTAÑA VARIOS
marco_varios = ttk.Frame(pestanas)
pestanas.add(marco_varios, text="Varios")


def crear_copia_seguridad():
    try:
        enviar_correo(
            CORREO_COORDINADOR,
            "Copia de seguridad - Inventario.xlsx",
            "Se adjunta la copia de seguridad completa del inventario.",
            ARCHIVO,
        )
        messagebox.showinfo("Listo", "Copia de seguridad enviada al coordinador.")
    except Exception as error:
        messagebox.showerror("Error", "No se pudo enviar el correo:\n" + str(error))


ttk.Button(marco_varios, text="Crear copia de seguridad de datos", command=crear_copia_seguridad).pack(pady=40)

ventana.mainloop()