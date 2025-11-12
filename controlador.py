"""
fecha: 2025/10/31
Autor: Alejandro Uzcategui, Gabriel Guedez, Hector Vargas
-
controlador de lo que hace el programa.
Con los nuevos cambios, este modulo solo sirve como puente
para iniciar la aplicacion grafica de Raylib.
"""
#========================
#import
# Conecta este modulo con el modulo modelo
import modelo

def mostrar_tui():
    """
    Esta funcion era la TUI (Menu en terminal).
    Ahora, su unico proposito es lanzar la aplicacion Raylib
    que contiene todos los menus y el juego.
    """
    # Llama a la funcion principal en el modelo que ahora
    # maneja todo (menus y juego)
    modelo.iniciar_aplicacion_raylib()