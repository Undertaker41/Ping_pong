"""
fecha: 2025/10/31
Autor: Alejandro Uzcategui, Gabriel Guedez, Hector Vargas
-
descripcion: maneja la interfaz de usuario y la presentacion de los datos

ping_pong/vista.py (Ya no se usa)
Este archivo ya no es necesario, ya que todas las funciones de "vista" (mostrar menús, limpiar pantalla, etc.) ahora se manejan con Raylib dentro de modelo.py.
"""

"""
#========================
#import
import os

def mostrar_titulo(titulo):
    """
    Imprime un titulo simple.
    """
    print(f"\n--- {titulo} ---")

def mostrar_menu(items):
    """
    Imprime los items de un menu (recibe una tupla o lista).
    """
    # Usamos map para aplicar la funcion print a cada item
    list(map(print, items))
    print() # Deja un espacio

# --- NUEVA FUNCION ---
def mostrar_lista(items):
    """
    Imprime los items de una lista, uno por linea.
    Util para mostrar el historial.
    """
    list(map(print, items))
    print() # Deja un espacio

def pedir_opcion():
    """
    Solicita una opcion al usuario y la retorna.
    """
    return input(">>> ")

def limpiar_pantalla():
    """
    Limpia la consola, compatible con Windows, Linux y Mac.
    """
    # 'clear' funciona en Linux/Mac, 'cls' en Windows
    os.system("clear" if os.name == "posix" else "cls")

def pausar_pantalla():
    """
    Pausa la ejecucion hasta que el usuario presione Enter.
    """
    print("\nPresione Enter para continuar...")
    input()

def mostrar_mensaje(mensaje):
    """
    Muestra un mensaje simple en la consola.
    """
    print(f"\n[MENSAJE] {mensaje}\n")

    """