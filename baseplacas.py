import pyodbc
from datetime import datetime
import pandas as pd
from sqlalchemy.engine import URL,create_engine


'''este modulo se encarga de la conexion con la base de datos y de las consultas'''

cursor = None # variable para ejecutar consultas
conex = None # variable para la conexion con la base de datos

def conexion(): # funcion para conectarse a la base de datos
    global cursor,conex
    driver = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=LAPTOP-OR5S81E4;DATABASE=base_placas;Trusted_Connection=yes;' # cadena de conexion
    cnxn = pyodbc.connect(driver, timeout=50) # conectarse a la base de datos
    conex_url = URL.create("mssql+pyodbc", query={"odbc_connect": driver} ) # crear la url de conexion
    engine = create_engine(conex_url) # crear el motor de conexion
    conex = engine.connect() # conectarse a la base de datos
    cursor = cnxn.cursor() # crear el cursor para ejecutar consultas

def comprobar(*args): # funcion para comprobar si la placa existe en la base de datos
    res = cursor.execute("exec Comprobacion ?", (args[0],)) # ejecutar la consulta
       
    return res.fetchall()[0][0]  # retornar el resultado de la consulta

def comprobacion(func): # decorador para comprobar si la placa existe en la base de datos
    global cursor
    def wrapper(*args): # funcion que se ejecuta antes de la funcion decorada
        '''Regresa una lista de tuplas con los registros de la placa'''
        res = comprobar(args[0]) # ejecutar la funcion comprobar
       
        if res: # si la placa existe
            return func(*args) # ejecutar la funcion decorada
        
        return None # si la placa no existe retornar None 
    
    return wrapper

def insertarRegistro(placa:str, estado:str): # funcion para insertar un registro en la base de datos
    global cursor
    query = "INSERT INTO registros (placa, estatus, fecha) VALUES (?, ?, ?)" # consulta para insertar un registro
    valores = (placa, estado, datetime.now()) # valores para la consulta
    cursor.execute(query, valores) # ejecutar la consulta
    cursor.commit() # guardar los cambios

def exec(query,*args):  # funcion para ejecutar consultas
    global cursor
    cursor.execute(query,*args) # ejecutar la consulta
    cursor.commit()    # guardar los cambios


def agregarConductor(placa:str,nombre:str,ocupacion:str): # funcion para agregar un conductor a la base de datos
    try:
        query = "INSERT INTO conductor (placa, nombre, ocupacion) VALUES (?, ?, ?)" # consulta para agregar un conductor
        exec(query,placa,nombre,ocupacion) # ejecutar la consulta
        print('conductor agregagdo') # imprimir mensaje de exito
    except pyodbc.IntegrityError: # si la placa ya existe
        print('conductor ya existente') # imprimir mensaje de error
        return False # retornar False
    else:
        return True # retornar True

def eliminarConductor(placa:str): # funcion para eliminar un conductor de la base de datos
    query = "DELETE FROM conductor WHERE placa = ?" # consulta para eliminar un conductor
    exec(query,placa) # ejecutar la consulta
    print('conductor eliminado') # imprimir mensaje de exito

def editarConductor(placa:str,nombre:str,ocupacion:str): # funcion para editar un conductor de la base de datos
    global cursor
    query = "UPDATE conductor SET placa=?,nombre=?,ocupacion=? WHERE placa = ?" # consulta para editar un conductor
    exec(query,placa,nombre,ocupacion,placa) # ejecutar la consulta
    print('conductor actualizado') # imprimir mensaje de exito

def refresh(): # funcion para refrescar la conexion con la base de datos
    global cursor
    '''Regresa una lista de tuplas con todos los registros'''
    cursor.execute("SELECT TOP 30 * FROM registros ORDER BY fecha DESC") # ejecutar la consulta
    rows = cursor.fetchall() # obtener los registros
    return rows # retornar los registros

def getConductor(placa:str): # funcion para obtener un conductor de la base de datos
    global cursor
    '''Regresa una lista de tuplas con los registros de la placa'''
    cursor.execute("SELECT * FROM conductor WHERE placa = ?", (placa,)) # ejecutar la consulta
    rows = cursor.fetchall() # obtener los registros
    return rows # retornar los registros

def getRegistros(): # funcion para obtener todos los registros de la base de datos
    global conex
    '''Regresa una lista de tuplas con todos los registros'''
    query = "SELECT id,registros.placa,nombre,ocupacion,estatus,fecha FROM registros,conductor WHERE registros.placa=conductor.placa ORDER BY  fecha DESC" # consulta para obtener todos los registros
    df = pd.read_sql(query,conex) # ejecutar la consulta
    # quitar espacios en blanco
    df['placa'] = df['placa'].str.strip()
    df['nombre'] = df['nombre'].str.strip()
    df['ocupacion'] = df['ocupacion'].str.strip()
    return df # retornar los registros

def getPlacas(): # funcion para obtener todas las placas de la base de datos
    global cursor
    '''Regresa una lista de tuplas con todos los registros'''
    cursor.execute("SELECT placa FROM conductor") # ejecutar la consulta
    rows = cursor.fetchall() # obtener los registros
    placas = [row[0].strip() for row in rows] # quitar espacios en blanco
    return placas  # retornar los registros


from numpy import ndarray
from cv2 import imencode

def agregarDesconocidos(img:ndarray): # funcion para agregar un desconocido a la base de datos
    global cursor
    img = imencode('.jpg', img)[1].tostring() # convertir la imagen a bytes
    query = "INSERT INTO desconocidos (foto, fecha) VALUES (?, ?)" # consulta para agregar un desconocido
    valores = (img, datetime.now()) # valores para la consulta
    cursor.execute(query, valores) # ejecutar la consulta
    cursor.commit()     # guardar los cambios

def getDesconocidos(date): # funcion para obtener los desconocidos de la base de datos
    global cursor
    query = f"SELECT id,foto,fecha FROM desconocidos WHERE fecha >= '{date} 00:00:00' and fecha <= '{date} 23:59:59' ORDER BY fecha DESC" # consulta para obtener los desconocidoss
    cursor.execute(query) # ejecutar la consulta
    rows = cursor.fetchall() # obtener los registros
    return rows # retornar los registros

conexion()


if __name__=='__main__':
    print(getRegistros())
