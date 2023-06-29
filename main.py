from gui import App #  importamos nuetsra APP

try:
    App() #Ejecutamos la app
except Exception as e:
    print(e) #Imprimimos el error
finally:
    exit() #Salimos del programa
