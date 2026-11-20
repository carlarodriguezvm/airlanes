from conexion_comandos import conexion, errorConexion
import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, X, END

app = ttk.Window(themename="superhero")



app.geometry("650x450")
app.title("Inventario")
app.resizable(False, False)

def verificarConexion():
    if conexion == 0:
        ttk.Messagebox.show_error(
            title="Ups",
            message=f"No se pudo conectar a la base de datos:\n{errorConexion}",
        )
        return False
    return True

verificarConexion()

barraMenu = ttk.Menu(app) #crear barra
app.config(menu=barraMenu) #anclar barra a la ventana principal
menuNavegacion = ttk.Menu(barraMenu, tearoff=False) #crear menu
barraMenu.add_cascade(menu=menuNavegacion, label='Navegacion') #anclar menu a la barra

#crear opciones del menu para escoger frame
menuNavegacion.add_command(label="Inicio", command=lambda: cambiarVista(vistaInicio)) 
menuNavegacion.add_command(label="Categorias", command=lambda: cambiarVista(vistaCategorias))
menuNavegacion.add_command(label="Productos", command=lambda: cambiarVista(vistaProductos))

#*******************frame principal*****************
contenedorVistas = ttk.Frame(app)
contenedorVistas.pack(fill=BOTH, expand=True)

#**************frame incio*****************
vistaInicio = ttk.Frame(contenedorVistas)
vistaInicio.place(relwidth=1, relheight=1)

lblBienvenida = ttk.Label(
    vistaInicio,
    text="Bienvenido al Sistema",
    font=("Segoe UI", 22, "bold"),
    bootstyle="primary",
)
lblBienvenida.pack(pady=(40, 10))




#****************************framecategorias*************************
vistaCategorias = ttk.Frame(contenedorVistas)
vistaCategorias.place(relwidth=1, relheight=1)

lblTituloCategorias = ttk.Label(
    vistaCategorias,
    text="Categorias",
    font=("Segoe UI", 22, "bold"),
    bootstyle="primary",
)
lblTituloCategorias.place(x=0,y=0)

id_categoria = 0

contenedorSuperior = ttk.Frame(vistaCategorias, padding=20)
contenedorSuperior.place(x=0, y=45, width=400, height=120)

lblCategoria = ttk.Label(contenedorSuperior, text="Categoría:")
lblCategoria.place(x=10, y=10)

entryCategoria = ttk.Entry(contenedorSuperior)
entryCategoria.place(x=10, y=35, width=250)

btnIngresar = ttk.Button(contenedorSuperior, bootstyle="success",text="Ingresar", command=lambda: insertarDatos())
btnIngresar.place(x=270, y=34)

btnActualizar = ttk.Button(contenedorSuperior, bootstyle="warning",text="Actualizar", command=lambda: actualizarDatos())
btnActualizar.place(x=270, y=70)

btnEliminar = ttk.Button(contenedorSuperior, bootstyle="danger",text="Eliminar", command=lambda: eliminarDatos())
btnEliminar.place(x=180, y=70)

contenedorTabla = ttk.Frame(vistaCategorias, padding=20)
contenedorTabla.place(x=0, y=170, width=400, height=230)

columns = ("id", "nombre")
tree = ttk.Treeview(contenedorTabla,
columns=columns,
show="headings",
bootstyle="primary",
)
tree.heading("id", text="Id")
tree.heading("nombre", text="Nombre")

tree.column("id", width=120, anchor="w")
tree.column("nombre", width=120, anchor="w")

tree.pack(fill=BOTH, expand=True)

tree.bind('<Double-1>', lambda e:seleccionarFila())

# btnCargar = tk.Button(app, text="Mostrar Datos", command=lambda: cargarDatos())
# btnCargar.place(x=30, y=280)

def limpiarCampos():
    entryCategoria.delete(0, END)

def seleccionarFila():
    if not tree.selection():
        return
    
    item = tree.selection()[0]
    print(tree.item(item, "values"))
    limpiarCampos()
    entryCategoria.insert(0, tree.item(item,"values")[1])
    global id_categoria
    global categoria
    id_categoria = (tree.item(item, "values")[0])
    categoria = (tree.item(item, "values")[1])
    print(id_categoria)

def cargarDatos():
    if conexion == 0:
        return
    
    con = conexion 

    cursor = con.cursor()

    query = "SELECT * FROM categorias"

    cursor.execute(query)
    datos = cursor.fetchall()

    for fila in tree.get_children():
        tree.delete(fila)

    for dato in datos:
        tree.insert("", END, values=dato)
        
cargarDatos()

def insertarDatos():
    if not verificarConexion():
        return

    nombre = entryCategoria.get().strip()
    
    #lista de nombres
    existentes = [
        str(tree.item(fila, "values")[1]).strip().upper()
        for fila in tree.get_children()
    ]
    #EQUIVALENTE A LO DE ARRIBA (LO DE ARRIBA ES LIST COMPREHENSION)
    # existentes = []
    # for fila in tree.get_children():
    #     valores = tree.item(fila, "values")
    #     nombre_fila = str(valores[1]).strip().lower()
    #     existentes.append(nombre_fila)
    
    if not nombre:
        ttk.Messagebox.show_error(message='No pueden haber campos vacios o solo con espacios')
    elif nombre.upper() in existentes:
        ttk.Messagebox.show_error(message='No pueden haber categorias repetidas')
    else:
        con = conexion 
        cursor = con.cursor()
        query = "insert into categorias(nombre) values(%s)"
        valores = (nombre,)
        cursor.execute(query,valores)
        con.commit()
        
        if(cursor.rowcount > 0):
            ttk.Messagebox.show_info(message='Categoria agregada exitosamente')
        else:
            ttk.Messagebox.show_error(message='Problemas al agregar')
        limpiarCampos()
        
        cargarDatos()
    
    
    
def actualizarDatos():
    if not verificarConexion():
        return 

    global id_categoria

    nombre = entryCategoria.get().strip()

    if not id_categoria:
        ttk.Messagebox.show_info(message="Debes seleccionar una categoria.")
        return

    if not nombre:
        ttk.Messagebox.show_info(message="No pueden haber campos vacios.\nNo se modifico nada")
        id_categoria = 0
        limpiarCampos()
        return

    # Evita duplicar el nombre de OTRA categoría distinta a la seleccionada
    existentes_otras = [
        str(tree.item(fila, "values")[1]).strip().upper()
        for fila in tree.get_children()
        if str(tree.item(fila, "values")[0]) != str(id_categoria)
    ]
    
    #Version sin list comprehension
    # existentes_otras = []
    # for fila in tree.get_children():
    #     valores_fila = tree.item(fila, "values")
    #     id_fila = str(valores_fila[0])
    #     nombre_fila = str(valores_fila[1]).strip().upper()

    #     if id_fila != str(id_categoria):
    #         existentes_otras.append(nombre_fila)

    if nombre.upper() in existentes_otras:
        ttk.Messagebox.show_error(message="Ya existe otra categoria con ese nombre.")
        limpiarCampos()
        id_categoria=0
        return

    con = conexion
    cursor = con.cursor()
    query = "update categorias set nombre = %s where id = %s"
    valores = (nombre, id_categoria)
    cursor.execute(query, valores)
    con.commit()

    if cursor.rowcount > 0:
        ttk.Messagebox.show_info(message="Categoria Modificada")
        id_categoria = 0
    else:
        ttk.Messagebox.show_error(message="Problemas al modificar")

    limpiarCampos()
    cargarDatos()


def eliminarDatos():
    if not verificarConexion():
        return  

    global id_categoria

    if not id_categoria:
        ttk.Messagebox.show_error(message="Selecciona una categoría para eliminar.")
        return

    respuesta = ttk.Messagebox.show_question(
        message="¿Deseas eliminar esta categoría?",
        title="Confirmación",
        buttons=["Eliminar:danger", "Cancelar:secondary"],
    )

    if respuesta != "Eliminar":
        limpiarCampos()
        id_categoria = 0
        return

    con = conexion
    cursor = con.cursor()
    query = "delete from categorias where id = %s"
    valores = (id_categoria,)
    cursor.execute(query, valores)
    con.commit()

    if cursor.rowcount > 0:
        ttk.Messagebox.show_info(message="Categoria Eliminada")
        id_categoria = 0
        limpiarCampos()
        cargarDatos()
    else:
        ttk.Messagebox.show_error(message="Problemas al eliminar")
    

#*******************frame productos***********************
vistaProductos = ttk.Frame(contenedorVistas)
vistaProductos.place(relwidth=1, relheight=1)

lblTituloProductos = ttk.Label(
    vistaProductos,
    text="Productos",
    font=("Segoe UI", 22, "bold"),
    bootstyle="primary",
)
lblTituloProductos.pack(pady=(40, 10))

#funcion para superponer/cambiar la vista
def cambiarVista(vista):
    vista.tkraise()

cambiarVista(vistaInicio)



app.mainloop()