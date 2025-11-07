"""
fecha: 2025/10/31
Autor: Alejandro Uzcategui, Gabriel Guedez, Hector Vargas
-
descripcion: maneja la interfaz de usuario y la presentacion de los datos
"""
#========================
#import
import os

def mostrar_titulo(titulo):
    """
    Imprime un título simple.
    """
    print(f"\n--- {titulo} ---")

def mostrar_menu(items):
    """
    Imprime los ítems de un menú (recibe una tupla o lista).
    """
    # Usamos map para aplicar la función print a cada ítem
    list(map(print, items))
    print() # Deja un espacio

def pedir_opcion():
    """
    Solicita una opción al usuario y la retorna.
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
    Pausa la ejecución hasta que el usuario presione Enter.
    Cumple con el requisito "Presione una tecla para volver al menú".
    """
    print("\nPresione Enter (o cualquier tecla) para continuar...")
    input()

def mostrar_mensaje(mensaje):
    """
    Muestra un mensaje simple en la consola.
    """
    print(f"\n[MENSAJE] {mensaje}\n")