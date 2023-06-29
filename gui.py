import tkinter as tk
import baseplacas as base
import cv2
from PIL import Image, ImageTk
import reconocimiento as rec
import baseplacas as base
import tkinter.ttk as ttk
from numpy import ndarray,frombuffer
from pygrabber.dshow_graph import FilterGraph
from typing import Literal
from datetime import datetime

#-----------------------------
# Componentes


class Screen(ttk.Frame): # pantalla donde se visualiza la camara
    def __init__(self, master:tk.Tk,camara:int,title:str):
        super().__init__(master)

        ttk.Label(self, text=title).pack() # titulo de la pantalla

        self.lista = ttk.Combobox(self, values=FilterGraph().get_input_devices(), state='readonly') # combobox para seleccionar la camara
        self.lista.current(camara) # seleccionamos la camara
        self.index_cam = camara # guardamos el indice de la camara seleccionada
        self.lista.pack(pady=5) # colocamos el combobox en la pantalla

        self.camara =  cv2.VideoCapture(self.lista.current(),cv2.CAP_DSHOW) # inicializamos la camara
        self.placa = None # placa del conductor detectado
        self.desconocido = None # placa de conductor  desconocido detectado

        self.picture = ttk.Label(self) # pantalla donde se visualiza la imagen de la camara
        img= cv2.imread("no-cam.png") # imagen de ejemplo
        self.updateScreen(img) # actualizamos la imagen de la camara en la pantalla
        self.picture.pack() # colocamos la pantalla en la pantalla

        self.pack(pady=5)   # colocamos la pantalla en su contenededor


    def Cv2toTk(self, img:ndarray)->ImageTk.PhotoImage:
        '''Convierte una imagen de OpenCV a una imagen de Tkinter'''
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # convertimos la imagen de BGR a RGB
        img = cv2.resize(img, (400, 200)) # redimensionamos la imagen
        img = ImageTk.PhotoImage(image=Image.fromarray(img)) # convertimos la imagen a una imagen compatible con Tkinter
        return img # regresamos la imagen
    
    def updateScreen(self,cv2img:ndarray) -> None:
        tkimg = self.Cv2toTk(cv2img) # convertimos la imagen de OpenCV a una imagen de Tkinter
        self.picture.configure(image=tkimg) # actualizamos la imagen de la pantalla
        self.picture.image = tkimg # actualizamos la imagen de la pantalla

    def cambiarCamara(self,otra_cam:int):
        """"Funcion para cambair fuente de video de la camara"""
        if self.lista.current() == otra_cam: # si la camara seleccionada es la misma que la otra camara salimos de la funcion
            self.lista.current(self.index_cam) # regresamos la camara anteriuormente seleccionada 
            return False
        
        # si la camara seleccionada es diferente a la otra camara
        self.camara.release() # liberamos la camara
        self.camara =  cv2.VideoCapture(self.lista.current(),cv2.CAP_DSHOW) # inicializamos la camara
        self.index_cam = self.lista.current() # guardamos el indice de la camara seleccionada
        return True

class Tabla(ttk.Treeview): # tabal par aver datos
    def __init__(self, master,headers,func):
        self.getValues = func # funcion para obtener los datos de la tabla

        self.scrollbar = ttk.Scrollbar(master,orient=tk.VERTICAL) # scrollbar para la tabla
        super().__init__(master, # inicializamos la tabla
                         columns=[str(i) for i in range(len(headers))], #añadimos columnas
                         yscrollcommand=self.scrollbar.set) 
        self.scrollbar.config(command=self.yview) # configuramos el scrollbar

        # configuramos la tabla
        self.column("#0", width=0, minwidth=0) #

        #le ponemos nombres a las columnas
        for i,text in enumerate(headers):
            self.heading(str(i), text=text)

        self.refresh() # actualizamos la tabla


    def refresh(self):
        """Actualiza los datos de la tabla"""
        self.delete(*self.get_children()) # borramos los datos de la tabla
        rows = self.getValues() # obtenemos los datos de la bd
        # insertamos los datos en la tabla
        for row in rows: 
            values = [value for value in row]
            self.insert("", "end", values=values)



#-----------------------------
# Paneles


class Camaras(ttk.Frame): # panel para visualizar las camaras
    def __init__(self, master:tk.Tk):
        super().__init__(master)

        # -- Camara de afuera --
        self.afuera = Screen(self,0,"Camara afuera") # pantalla de la camara de afuera
        self.afuera.lista.bind("<<ComboboxSelected>>", # evento que cambia la camara de afuera
                                 lambda e: self.afuera.cambiarCamara( #funcion que cambia la camara de afuera
                                            self.adentro.lista.current()
                                            ))

        # -- Camara de adentro --
        self.adentro = Screen(self,1,"Camara adentro") # pantalla de la camara de adentro
        self.adentro.lista.bind("<<ComboboxSelected>>",  # evento que cambia la camara de adentro
                                  lambda e: self.adentro.cambiarCamara( #funcion que cambia la camara de adentro
                                            self.afuera.lista.current()
                                            ))
        
        self.fg = FilterGraph() # objeto para obtener las camaras conectadas

    def get_Afuera(self): # funcion para obtener la imagen de la camara de afuera
        return self.afuera.camara.read()
    
    def get_Adentro(self): # funcion para obtener la imagen de la camara de adentro
        return self.adentro.camara.read()
    
    def camaras_realese(self):  # funcion para liberar las camaras
        self.afuera.camara.release()
        self.adentro.camara.release()

    def updateCamaras(self): # funcion para actualizar las camaras
        cams = self.fg.get_input_devices() # obtenemos las camaras conectadas

        anterior = self.afuera.lista.get() # guardamos la camara seleccionada
        self.afuera.lista.config(values=cams) # actualizamos las camaras
        self.afuera.index_cam = self.afuera.lista.current() # guardamos el indice de la camara seleccionada
        if anterior not in cams: # si la camara seleccionada no esta conectada
            self.afuera.index_cam = 0 if self.adentro.index_cam != 0 else 1 # seleccionamos la otra camara
            self.afuera.lista.current(self.afuera.index_cam) #

        #mismo procedimiento para la camara de adentro
        anterior = self.adentro.lista.get()
        self.adentro.index_cam = self.adentro.lista.current()
        self.adentro.lista.config(values=cams)
        if anterior not in cams: 
            self.adentro.index_cam = 0 if self.afuera.index_cam != 0 else 1
            self.adentro.lista.current(self.adentro.index_cam)

            

class Botones(ttk.Frame): # panel para los botones
    def __init__(self, master:tk.Tk):
        self.master = master
        super().__init__(master)

        self.actual = None # ventana enmergente actual (solo puede haber una)

        # -- Botones --
        self.agregar = ttk.Button(self, text="Agregar", command=self.Agregar)
        self.agregar.grid(column=0, row=0,padx=5,pady=5,ipadx=10,ipady=10)

        self.eliminar = ttk.Button(self, text="Eliminar", command=self.Eliminar)
        self.eliminar.grid(column=1, row=0,padx=5,pady=5,ipadx=10,ipady=10)

        self.editar = ttk.Button(self, text="Editar", command=self.Editar)
        self.editar.grid(column=0, row=1,padx=5,pady=5,ipadx=10,ipady=10)

        self.buscar = ttk.Button(self, text="Buscar", command=self.Buscar)
        self.buscar.grid(column=1, row=1,padx=5,pady=5,ipadx=10,ipady=10)

        self.desconocidos = ttk.Button(self, text="Desconocidos", command=self.Desconocidos)
        self.desconocidos.grid(column=2, row=0,padx=5,pady=5,ipadx=10,ipady=10)
        self.descConteo = 0 # conteo de desconocidos detectados
        self.descLabel = ttk.Label(self,foreground='red') # label para mostrar el conteo de desconocidos
        self.descLabel.grid(column=2, row=1,padx=5,pady=5,ipadx=10,ipady=10) 

    def destruccion(self): # funcion cuando destruir la ventana emergente
        self.actual = None

    def updateDesconocidos(self): # funcion para actualizar el conteo de desconocidos
        self.descConteo+=1
        self.descLabel.config(text=f'Hay {self.descConteo} desconocidos detetctados hoy')

    def Cambio(func): # decorador para cambiar la ventana emergente
        def wrapper(self):
            
            if self.actual is not None:  # si hay una ventana emergente abierta
                self.actual.focus_set() # enfocamos la ventana actual
                return 

            #si no
            ventana = func(self) # instanciamos la ventana
            self.actual = ventana # guardamos la ventana
            ventana.bind("<Destroy>", lambda e: self.destruccion()) # evento para cuando se destruya la ventana

        return wrapper
    
    # funcion para todos los tipos de ventanas emergentes
    @Cambio
    def Agregar(self):
        return Agregar(self.master)

    @Cambio 
    def Eliminar(self):
        return Eliminar(self.master)
    
    @Cambio
    def Editar(self):
        return Editar(self.master)

    @Cambio
    def Buscar(self):
        return Buscar(self.master)
    
    @Cambio
    def Desconocidos(self):
        return Desconocidos(self.master)

class Info(ttk.Frame): # Panel para mostrar la informacion del ultimo conductor detectado
    def __init__(self, master:tk.Tk):
        super().__init__(master)

        ttk.Label(self, text="Ultimo en registrarse: ", font='Roboto 15').pack()
        self.nombre = ttk.Label(self, text="Nombre: ",font='Roboto 10') # label para mostrar el nombre del conductor
        self.nombre.pack()
        self.placa = ttk.Label(self, text="Placa: ",font='Roboto 10') # label para mostrar la placa del conductor
        self.placa.pack()
        self.ocupacion = ttk.Label(self, text="Ocupacion: ",font='Roboto 10') # label para mostrar la ocupacion del conductor
        self.ocupacion.pack()
        self.estado = ttk.Label(self, text="Estado: ",font='Roboto 10') # label para mostrar el estado del conductor
        self.estado.pack()


    def setInfo(self, placa:str,estado:str,nombre:str='???',ocupacion:str='???'): # funcion para actualizar la informacion del conductor
        # Quitamos los espacios al principio y al final de los datos
        self.nombre["text"] = "Nombre: " + nombre.strip()
        self.placa["text"] = "Placa: " + placa.strip()
        self.ocupacion["text"] = "Ocupacion: " + ocupacion.strip()
        self.estado["text"] = "Estado: " + estado.strip()


#-----------------------------
# Ventanas


class Ventana(tk.Toplevel): # ventana emergente base
    def __init__(self,master,widget,title='Registro'):
        super().__init__(master)
        self.title(title) # titulo de la ventana
        self.wm_resizable(False,False) # no se puede cambiar el tamaño de la ventana

        # creamos el contenedor de la ventana
        self.content = ttk.Frame(self)
        self.content.columnconfigure(0,weight=1)
        self.content.columnconfigure(1,weight=1)

        self.advertencia = ttk.Label(self,text='',foreground='red') # label para mostrar advertencias
        self.campos = {} # diccionario para guardar los campos de la ventana

        # placa
        label = ttk.Label(self.content,text='Placa')
        label.grid(column=0,row=0,padx=10,pady=15)
        self.placa = widget(self.content) # widget para ingresar la placa
        self.placa.grid(column=1,row=0,padx=10,pady=10)
        self.campos['Placa'] = (label,self.placa) # guardamos el campo en el diccionario
        
        # botones
        self.botones = ttk.Frame(self.content) # contenedor para los botones
        self.aceptar = ttk.Button(self.botones,text='Aceptar',command=self.Aceptar) # boton para aceptar 
        self.cancelar = ttk.Button(self.botones,text='Cancelar',command=self.Cancelar) # boton para cancelar
        self.aceptar.pack(side=tk.LEFT,padx=10,pady=10)
        self.cancelar.pack(side=tk.LEFT,padx=10,pady=10)

        self.content.pack()
        self.focus_set()  # enfocamos la ventana
        self.placa.focus_set() # enfocamos el campo de la placa
        self.bind("<Destroy>", lambda e: self.Cancelar()) # evento para cuando se destruya la ventana

   
    def Advertir(self,text): # funcion para mostrar advertencias
        self.advertencia.forget() # borramos la advertencia anterior
        self.advertencia.config(text=text) # actualizamos la advertencia
        self.advertencia.pack(before=self.content) # colocamos la advertencia en la ventana

    def Incompletos(self): # funcion para verificar si hay campos incompletos
        incompletos = False # variable para saber si hay campos incompletos
        for campo in self.campos: # recorremos los campos
           
            if len(self.campos[campo][1].get()) == 0: # si el campo esta vacio
                self.campos[campo][0].config(foreground='red') # cambiamos el color del label del campo a rojo
                incompletos = True # hay campos incompletos
            else:
                self.campos[campo][0].config(foreground='black') # cambiamos el color del label del campoa negro

        if incompletos: self.Advertir('Llene todos los campos')  #si hay campos incompletos mostramos una advertencia

        return incompletos #retornamos el resultado
    
    def Cancelar(self): # funcion para cancelar la ejecucion
        self.destroy() # se destruye la ventaan emergente
  
    def Aceptar(self): # funcion para cuando se acepte la solicitud
        pass # se define hasta la declaracion de las vetanas

class Agregar(Ventana): # ventana para agregar conductores nuevos
    def __init__(self,master):
        super().__init__(master,ttk.Entry,'Agregar conductor') # se llama al contructor base

        # Nombre
        label = ttk.Label(self.content,text='Nombre') # label nombre
        label.grid(column=0,row=1,padx=10,pady=15)
        self.nombre = ttk.Entry(self.content) # entrada del nombre
        self.nombre.grid(column=1,row=1,padx=10,pady=15)
        self.campos['Nombre'] = (label,self.nombre) # agregamos el campo al diccionario
        
        # Ocupacion
        label = ttk.Label(self.content,text='Ocupacion') # label nombre
        label.grid(column=0,row=2,padx=10,pady=15)
        self.ocupacion = ttk.Combobox(self.content, # entrada del nombre
                                      values=('Estudiante','Trabajador'), # valores de la ocupacion
                                      state='readonly') # no se puede escribir
        self.ocupacion.grid(column=1,row=2,padx=10,pady=10)
        self.campos['Ocupacion'] = (label,self.ocupacion) # agregamos el campo al diccionario

        self.botones.grid(column=0,row=3,columnspan=2,padx=10,pady=10)
    
    def Aceptar(self):

        if self.Incompletos(): return # si hay campos incompletos salimos de la funcion
        
        susccess = base.agregarConductor(self.placa.get(),self.nombre.get(),self.ocupacion.get()) # agregamos el conductor a la base de datos
        if not susccess:  # si no se pudo agregar el conductor
            self.Advertir('Conductor ya existente') # mostramos una advertencia
            return # salimos de la funcion
        
        self.destroy() # destruimos la ventana emergente

class Seleccion(Ventana): # ventana para seleccionar un conductor
    def __init__(self,master,title='Register'):
        super().__init__(master,ttk.Combobox,title)
        self.placa.config(state='readonly') # no se puede escribir en la entrada de la placa
        values = base.getPlacas() # obtenemos las placas de la base de datos
        values.insert(0,'') # agregamos un valor vacio
        self.placa['values'] = values # agregamos las placas a la entrada de la placa
        

    def getValue(self): # funcion para obtener el valor de la placa
        return self.placa.get()

class Eliminar(Seleccion): # ventana para eliminar un conductor
    def __init__(self,master): 
        super().__init__(master,'Eliminar conductor')
        self.botones.grid(column=0,row=1,columnspan=2,padx=10,pady=10) 


    def Aceptar(self): # funcion para cuando se acepte la solicitud
        if self.Incompletos(): return # si hay campos incompletos salimos de la funcion

        base.eliminarConductor(self.getValue()) # eliminamos el conductor de la base de datos
        self.destroy() # destruimos la ventana emergente

class Editar(Seleccion):
    def __init__(self,master):
        super().__init__(master,'Editar conductor')

        label = ttk.Label(self.content,text='Nombre') # label nombre
        label.grid(column=0,row=1,padx=10,pady=15) 
        self.nombre = ttk.Entry(self.content,state='disable') # entrada del nombre
        self.nombre.grid(column=1,row=1,padx=10,pady=10)
        self.campos['Nombre'] = (label,self.nombre) # agregamos el campo al diccionario

        label = ttk.Label(self.content,text='Ocupacion') # label nombre
        label.grid(column=0,row=2,padx=10,pady=15)
        self.ocupacion = ttk.Combobox(self.content, # entrada del nombre
                                      values=('Estudiante','Trabajador'), # valores de la ocupacion
                                      state='disable') # no se puede escribir
        self.ocupacion.grid(column=1,row=2,padx=10,pady=10)
        self.campos['Ocupacion'] = (label,self.ocupacion) # agregamos el campo al diccionario

        self.buscar = ttk.Button(self.content,text='Buscar',command=self.Buscar) # boton para buscar el conductor
        self.buscar.pack(side=tk.LEFT,padx=10,pady=10,before=self.aceptar)

        self.aceptar.config(state='disable') # deshabilitamos el boton de aceptar
        self.botones.grid(column=0,row=3,columnspan=2,padx=10,pady=10)


    def Buscar(self): # funcion para buscar el conductor
        if  len(self.placa.get())==0:  # si no se ha ingresado una placa
            self.Advertir('Llene todos los campos') # mostramos una advertencia
            # borramos los datos y deshabilitamos los campos
            self.nombre.delete(0,tk.END)
            self.ocupacion.set('')
            self.aceptar.config(state='disable')
            self.nombre.config(state='disable')
            self.ocupacion.config(state='disable')
        else: # si se ha ingresado una placa
            self.advertencia.forget() # borramos la advertencia
            # obtenemos los datos del conductor,los colocamos en los campos y habilitamos los campos
            res = base.getConductor(self.getValue())
            self.aceptar.config(state='enable')
            self.nombre.config(state='enable')
            self.nombre.delete(0,tk.END)
            self.nombre.insert(0,res[0][1].strip())
            self.ocupacion.config(state='readonly')
            self.ocupacion.set(res[0][2].strip())

    def Aceptar(self):
        if self.Incompletos(): return # si hay campos incompletos salimos de la funcion

        base.editarConductor(self.getValue(),self.nombre.get(),self.ocupacion.get()) # editamos el conductor de la base de datos
        self.destroy() # destruimos la ventana emergente

class Buscar(Seleccion): # ventana para buscar un conductor
    def __init__(self,master):
        super().__init__(master,'Buscar conductor')

        label = ttk.Label(self.content,text='Ocupacion') # label nombre
        label.grid(column=0,row=1,padx=10,pady=15)
        self.ocupacion = ttk.Combobox(self.content, # entrada del nombre
                                        values=('','Estudiante','Trabajador'), # valores de la ocupacion
                                        state='readonly') # no se puede escribir
        self.ocupacion.grid(column=1,row=1,padx=10,pady=10)

        #estatus
        label = ttk.Label(self.content,text='Estatus') # label nombre
        label.grid(column=0,row=2,padx=10,pady=15)
        self.estatus = ttk.Combobox(self.content, # entrada del nombre
                                        values=('','entro','salio'),    # valores de la ocupacion
                                        state='readonly') # no se puede escribir
        self.estatus.grid(column=1,row=2,padx=10,pady=10)
        
        #fecha
        label = ttk.Label(self.content,text='Fecha') # label nombre
        label.grid(column=0,row=3,padx=10,pady=15)
        self.fecha = ttk.Frame(self.content) # contenedor para la fecha 

        #año
        ttk.Label(self.fecha,text='Año').grid(column=0,row=0,padx=5,pady=5) # label para el año
        self.y = ttk.Spinbox(self.fecha,from_=0,to=99999,increment=1,width=5) # entrada para el año
        self.y.grid(column=0,row=1,padx=5)

        #mes
        ttk.Label(self.fecha,text='Mes').grid(column=1,row=0,padx=5,pady=5) # label para el mes
        self.m = ttk.Spinbox(self.fecha,from_=0,to=12,increment=1,width=2) # entrada para el mes
        self.m.grid(column=1,row=1,padx=5)

        #dia
        ttk.Label(self.fecha,text='Dia').grid(column=2,row=0,padx=5,pady=5) # label para el dia
        self.d = ttk.Spinbox(self.fecha,from_=0,to=31,increment=1,width=2) # entrada para el dia
        self.d.grid(column=2,row=1,padx=5)

        self.fecha.grid(column=1,row=3,padx=10,pady=10)
        
        self.botones.grid(column=0,row=4,columnspan=2,padx=10,pady=10)

        self.registros = Tabla(self,('id','placa','nombre','ocupacion','estatus','fecha'),self.filtrar) # tabla para mostrar los registros
        self.registros.scrollbar.pack(side=tk.RIGHT,fill=tk.Y) # scrollbar para la tabla


        self.registros.pack(padx=10,pady=10)

    def filtrar(self): # funcion para filtrar los registros
        datos = base.getRegistros() # obtenemos los registros de la base de datos
        
        # si hay valores en los campos de la ventana los usamos para filtrar los registros
        filtrado = False
        if len(self.placa.get()):
            datos = datos[datos['placa'] == self.placa.get()]
            filtrado = True

        if len(self.ocupacion.get()):
            datos = datos[datos['ocupacion'] == self.ocupacion.get()]
            filtrado = True

        if len(self.estatus.get()):
            datos = datos[datos['estatus'] == self.estatus.get()]
            filtrado = True

        if len(self.y.get()) and int(self.y.get()) != 0:
            datos = datos[datos['fecha'].dt.year == int(self.y.get())]
            filtrado = True

        if len(self.m.get()) and int(self.m.get()) != 0:
            datos = datos[datos['fecha'].dt.month == int(self.m.get())]
            filtrado = True

        if len(self.d.get()) and int(self.d.get()) != 0:
            datos = datos[datos['fecha'].dt.day == int(self.d.get())]
            filtrado = True

        return datos.values.tolist() if filtrado else [] # retornamos los registros filtrados o ningun registro si no se ha filtrado nada
    
    def Update(self): # funcion para actualizar los registros
        self.registros.refresh()

    def Aceptar(self): # funcion para cuando se acepte la solicitud
        self.Update() # actualizamos los registros
        self.advertencia.forget() # borramos la advertencia

class Desconocidos(tk.Toplevel): # ventana para mostrar los conductores desconocidos

    def __init__(self,master):
        super().__init__(master)
        self.title('Conductores desconocidos') # titulo de la ventana
        self.wm_resizable(False,False)  # no se puede cambiar el tamaño de la ventana

        fecha = datetime.now() # fecha actual
        self.fecha = ttk.Frame(self) # contenedor para la fecha
        ttk.Label(self.fecha,text='Fecha').grid(column=0,row=0,padx=5,pady=5,rowspan=2)

        #año
        ttk.Label(self.fecha,text='Año').grid(column=1,row=0,padx=5,pady=5) 
        self.y = ttk.Spinbox(self.fecha,from_=0,to=99999,increment=1,width=5)
        self.y.set(fecha.year) # año actual
        self.y.grid(column=1,row=1,padx=5)

        #mes
        ttk.Label(self.fecha,text='Mes').grid(column=2,row=0,padx=5,pady=5)
        self.m = ttk.Spinbox(self.fecha,from_=0,to=12,increment=1,width=2)
        self.m.set(fecha.month) # mes actual
        self.m.grid(column=2,row=1,padx=5)

        #dia
        ttk.Label(self.fecha,text='Dia').grid(column=3,row=0,padx=5,pady=5)
        self.d = ttk.Spinbox(self.fecha,from_=0,to=31,increment=1,width=2)
        self.d.set(fecha.day) # dia actual
        self.d.grid(column=3,row=1,padx=5)
        self.fecha.pack(padx=10,pady=10)

        # filtramos los datos cuando se actualice el valor de la fecha
        self.y.bind("<ButtonRelease-1>", lambda e: self.Update())
        self.m.bind("<ButtonRelease-1>", lambda e: self.Update())
        self.d.bind("<ButtonRelease-1>", lambda e: self.Update())

        self.fotos = ttk.Frame(self) # contenedor para las fotos
        self.fotos.columnconfigure(0,weight=1) 
        self.fotos.columnconfigure(1,weight=1)
        self.Update() # actualizamos las fotos
        self.fotos.pack(padx=10,pady=10)

    def Cv2toTk(self, img:ndarray)->ImageTk.PhotoImage: # funcion para convertir una imagen de OpenCV a una imagen de Tkinter
        '''Convierte una imagen de OpenCV a una imagen de Tkinter'''
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # convertimos la imagen de BGR a RGB
        img = cv2.resize(img, (200, 200)) # redimensionamos la imagen
        img = ImageTk.PhotoImage(image=Image.fromarray(img)) # convertimos la imagen a una imagen compatible con Tkinter
        return img # regresamos la imagen

    def Update(self): # funcion para actualizar las fotos
        for i in self.fotos.winfo_children(): # borramos las fotos anteriores 
            i.destroy()

        fecha = f"{self.y.get()}-{self.m.get()}-{self.d.get()}" # fecha seleccionada
        fotos = base.getDesconocidos(fecha) # obtenemos las fotos de la base de datos de esa fecha

        row,colunms = 0,0
        for _,foto,_ in fotos: # recorremos las fotos
            img = frombuffer(foto,dtype='uint8') # convertimos la foto a un array de bytes
            img = cv2.imdecode(img,cv2.IMREAD_COLOR) # convertimos la foto a una imagen de OpenCV
            img = self.Cv2toTk(img) # convertimos la imagen de OpenCV a una imagen de Tkinter
            # colocamos la imagen en la ventana
            label  = ttk.Label(self.fotos,image=img)
            label.image = img
            label.grid(column=colunms,row=row,padx=5,pady=5)

            # cambiamos la posicion de la siguiente imagen
            colunms += 1
            if colunms > 2:
                colunms = 0
                row += 1

# App principal del programa
class App(tk.Tk):
    def __init__(self): 
        super().__init__()

        #COnfiguramos la ventana
        self.title("Reconocimiento de placas") #titulo
        self.resizable(False,False) # no se puede cambaia el tamaño

        #Creamos el contenedor principal
        #Aqui estaran las diferentes secciones de nuestra app
        self.container = ttk.Frame(self)

        # seccion donde visualizamos las camaras
        self.camaras = Camaras(self.container)
        self.camaras.grid(column=0, row=0,padx=10,pady=10) # aqui colacamos las secciones en el contenedor en forma de grilla

        # seccion donde visualizamos los registros desde la base de datos
        self.table = Tabla(self.container,('id','placa','estatus','fecha'),base.refresh)
        self.table.scrollbar.grid(column=2,row=0,sticky='ns')
        self.table.grid(column=1,row=0,padx=10,pady=10,sticky='ns')

        # seccion donde visualizamos la informacion del ultimo conductor conductor detectado
        self.info = Info(self.container)
        self.info.grid(column=0, row=1,padx=10,pady=10)

        # seccion donde visualizamos los botones para agregar, eliminar, editar y buscar conductores
        self.botones = Botones(self.container)
        self.botones.grid(column=1, row=1,padx=10,pady=10)

        self.container.pack(expand=True, fill=tk.BOTH)#colocamos el contenedor principal en la ventana

        self.loop = True # variable para controlar el loop principal de la app
        self.bind("<Destroy>", self.exit) # si se cierra la ventana se ejecuta la funcion exit
        self.update() # loop principal de la app
    
    def exit(self,e):
        """ detenemos el loop y apagamos las camaras """
        self.loop = False
        self.camaras.camaras_realese()
    
    def evaluacion(self,screen:Screen, contraria:Screen,status: Literal['entro','salio']):

        """"Evaluamos y detetcamos las placas en la imagen"""
        ret, frame = screen.camara.read() # leemos la imagen de la camara
        if not  ret: return # si no se pudo leer la imagen salimos de la funcion

        screen.updateScreen(frame) # actualizamos la imagen de la camara en la pantalla

        placa,deteccion = rec.deteccion(frame.copy()) # evaluamos la imagen de la camara
        if deteccion is None: return # si no se detecto algo en la imagen salimos de la funcion

        screen.updateScreen(deteccion) # actualizamos la imagen de la camara en la pantalla con la deteccion
        if not placa: return # si no se detecto una placa salimos de la funcion
        
        placa = placa.replace(" ","") # quitamos los espacios de la placa
        placa = placa[:9] # solo tomamos los primeros 9 caracteres de la placa
        
        existe = base.comprobar(placa) # comprobamos si la placa existe en la base de datos
        if not existe: 
            if contraria.desconocido == placa and contraria.desconocido is not None: # si la placa detectada es igual a la placa desconocida de la pantalla contraria
                contraria.desconocido = None # reiniciamos la placa desconocida de la pantalla contraria
                self.botones.updateDesconocidos() # actualizamos el contador de desconocidos
                base.agregarDesconocidos(frame) # agregamos el conductor desconocido a la base de datos
                print('**conductor desconocido**',placa,'\n')
            else:
                screen.desconocido = placa # guardamos la placa del conductor desconocido
            return # si no existe salimos de la funcion

        if contraria.placa != placa: # si la placa detectada es diferente a la placa de la pantalla contraria
            # significa que unicamente a pasado por una camara
            # guardamos la placa del lado que estamos observando (adelante o afuera)
            screen.placa = placa
            print('**conductor autorizado**',screen.placa,'\n')
            return
        
        # si la placa detectada es igual a la placa de la pantalla contraria
        # significa que el conductor paso por las dos camaras y podmeos deducir si entro o salio
        print("Pase de conductor registrado",placa,'\n')
        conductor = base.getConductor(placa)  # obtenemos los datos del conductor
        self.insertarRegistro(placa,status) # insertamos el registro en la base de datos
        _, nombre, ocupacion = conductor[0] # obtenemos el nombre y la ocupacion del conductor
        self.info.setInfo(placa,nombre,ocupacion,status) # actualizamos la informacion del conductor en la pantalla
        contraria.placa = None # reiniciamos la placa almacenada de la pantalla contraria
 

    def insertarRegistro(self,placa:str,estatus:str): 
        base.insertarRegistro(placa,estatus) # insertamos el registro en la base de datos
        self.table.refresh() # actualizamos la tabla de registros

    def update(self):
        
            self.table.refresh() # actualizamos la tabla de registros
            while self.loop: # loop principal de la app
                
                # evaluamos la imagen que capta cada camara, si detetcta placas y si estan registradas

                #Aqui evalaamos la camara de afuera
                self.evaluacion(self.camaras.afuera,self.camaras.adentro,'salio')

                #Aqui evalaamos la camara de adentro
                self.evaluacion(self.camaras.adentro,self.camaras.afuera,'entro')

                self.camaras.updateCamaras() # actualizamos las camaras
                super().update() # actualizamos la ventana
                 
                if 0xFF == ord('q'): # si se presiona la tecla q se cierra la app
                        break


