"""
fecha: 2025/10/31
Autor: Alejandro Uzcategui, Gabriel Guedez, Hector Vargas
-
controlador de lo que hace el programa maneja la interaccion entre el modelo y la vista
"""
#========================
#import
# Conecta este modulo con el modulo vista
import vista
# Conecta este modulo con el modulo modelo (donde está el juego)
import modelo

def gestionar_juego():
    """
    Gestiona el sub-menú y el bucle del juego.
    Se encarga de iniciar el juego y preguntar si se desea volver a jugar.
    """
    while True:
        # 1. Limpia la pantalla TUI antes de iniciar el juego
        vista.limpiar_pantalla()
        vista.mostrar_mensaje("Iniciando juego... (La ventana de Raylib se abrirá)")
        
        # 2. Inicia el juego (esto bloquea el script TUI)
        # El programa esperará aquí hasta que la ventana de raylib se cierre.
        modelo.iniciar_juego()
        
        # 3. Después de que el juego termina, limpiar la pantalla de la TUI
        # (que probablemente muestre el mensaje de "Iniciando juego...")
        vista.limpiar_pantalla()
        
        # 4. Mostrar menú post-juego, según lo solicitado
        vista.mostrar_titulo("Juego Terminado")
        menu_post_juego = ("1. Volver a jugar", "q. Volver al menú principal")
        vista.mostrar_menu(menu_post_juego)
        
        opcion = vista.pedir_opcion()
        
        if opcion == '1':
            # Si elige '1', el bucle (while True) simplemente se repite
            vista.mostrar_mensaje("¡Genial! Preparando otra partida...")
            continue
        elif opcion == 'q':
            # Si elige 'q', rompemos este bucle y volvemos al menú principal
            break
        else:
            # Manejo de opción inválida en este sub-menú
            vista.limpiar_pantalla()
            vista.mostrar_mensaje("Opción no válida.")
            # Pausamos para que vea el error y luego mostramos el menú post-juego de nuevo
            vista.pausar_pantalla()

def mostrar_tui():
    """
    Muestra el menú principal (TUI) y maneja la navegación.
    Este es el bucle principal del programa.
    """
    while True:
        vista.limpiar_pantalla()

        # Muestra el TUI principal
        titulo_principal = "JUEGO DE PING PONG"
        menu_principal = ("1. Jugar", "q. Salir")

        vista.mostrar_titulo(titulo_principal)
        vista.mostrar_menu(menu_principal)

        # Pide una opción al usuario
        opcion_principal = vista.pedir_opcion()

        # Controla las opciones del menú del TUI
        if opcion_principal == '1':
            # Llama a la función que maneja la lógica del juego
            gestionar_juego()
            
        elif opcion_principal == 'q':
            # Opción de salida
            vista.limpiar_pantalla()
            vista.mostrar_mensaje("¡Gracias por jugar! ¡Hasta luego!")
            # Rompe el bucle principal (while True) para terminar el programa
            break
            
        else:
            # Manejo de opción inválida
            vista.limpiar_pantalla()
            vista.mostrar_mensaje("Opción no válida. Intente de nuevo.")
            # Pausa para que el usuario pueda leer el mensaje
            vista.pausar_pantalla()