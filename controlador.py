# controlador.py (Version Funcional)
"""
fecha: 2025/10/31
Autor: Alejandro Uzcategui, Gabriel Guedez, Hector Vargas
-
descripcion: Componente "Controlador" (MVC) - Version Funcional.
Se encarga de leer TODOS los inputs (teclado y gamepad) y 
traducirlos a un objeto 'Entradas' (diccionario) simple para el Modelo.
NO USA CLASES (POO).
"""

try:
    import raylibpy as rl
except ImportError:
    print("Error: No se pudo importar la biblioteca 'raylibpy'.")
    print("Por favor, instálela usando: pip install raylib-py")
    exit()

import modelo # Importa el modelo para la funcion 'crear_entradas_vacias' y constantes

# Ya no hay clase 'Controlador'

def procesar_entradas(estado_juego):
    """
    Lee todos los inputs de Raylib y devuelve un diccionario 'Entradas'.
    Reemplaza a Controlador.procesar_entradas.
    
    Nota: Lee y escribe en 'estado_juego' para manejar el deadzone
    del menu (axis_j1_neutral).
    """
    # Crea un diccionario de entradas vacio
    entradas = modelo.crear_entradas_vacias()

    # --- Deteccion de Mandos ---
    gamepad_j1_conectado = rl.is_gamepad_available(modelo.GAMEPAD_J1)
    gamepad_j2_conectado = rl.is_gamepad_available(modelo.GAMEPAD_J2)

    # --- Inputs de Menu ---
    dpad_j1_up = gamepad_j1_conectado and rl.is_gamepad_button_pressed(modelo.GAMEPAD_J1, rl.GAMEPAD_BUTTON_LEFT_FACE_UP)
    dpad_j1_down = gamepad_j1_conectado and rl.is_gamepad_button_pressed(modelo.GAMEPAD_J1, rl.GAMEPAD_BUTTON_LEFT_FACE_DOWN)
    dpad_j2_up = gamepad_j2_conectado and rl.is_gamepad_button_pressed(modelo.GAMEPAD_J2, rl.GAMEPAD_BUTTON_LEFT_FACE_UP)
    dpad_j2_down = gamepad_j2_conectado and rl.is_gamepad_button_pressed(modelo.GAMEPAD_J2, rl.GAMEPAD_BUTTON_LEFT_FACE_DOWN)
    
    axis_y_j1_menu = rl.get_gamepad_axis_movement(modelo.GAMEPAD_J1, modelo.GAMEPAD_AXIS_Y) if gamepad_j1_conectado else 0
    axis_y_j2_menu = rl.get_gamepad_axis_movement(modelo.GAMEPAD_J2, modelo.GAMEPAD_AXIS_Y) if gamepad_j2_conectado else 0
    
    # Lee el estado del deadzone desde el 'estado_juego' principal
    axis_j1_up = (gamepad_j1_conectado and axis_y_j1_menu < -modelo.GAMEPAD_MENU_DEADZONE and estado_juego['axis_j1_neutral'])
    axis_j1_down = (gamepad_j1_conectado and axis_y_j1_menu > modelo.GAMEPAD_MENU_DEADZONE and estado_juego['axis_j1_neutral'])
    axis_j2_up = (gamepad_j2_conectado and axis_y_j2_menu < -modelo.GAMEPAD_MENU_DEADZONE and estado_juego['axis_j2_neutral'])
    axis_j2_down = (gamepad_j2_conectado and axis_y_j2_menu > modelo.GAMEPAD_MENU_DEADZONE and estado_juego['axis_j2_neutral'])
    
    # Escribe el estado del deadzone de vuelta en 'estado_juego'
    if axis_j1_up or axis_j1_down: estado_juego['axis_j1_neutral'] = False
    if axis_j2_up or axis_j2_down: estado_juego['axis_j2_neutral'] = False
    if gamepad_j1_conectado and -0.2 < axis_y_j1_menu < 0.2: estado_juego['axis_j1_neutral'] = True
    if gamepad_j2_conectado and -0.2 < axis_y_j2_menu < 0.2: estado_juego['axis_j2_neutral'] = True
    
    # Rellena el diccionario de entradas
    entradas['menu_arriba'] = rl.is_key_pressed(rl.KEY_UP) or dpad_j1_up or dpad_j2_up or axis_j1_up or axis_j2_up
    entradas['menu_abajo'] = rl.is_key_pressed(rl.KEY_DOWN) or dpad_j1_down or dpad_j2_down or axis_j1_down or axis_j2_down
    
    entradas['menu_aceptar'] = rl.is_key_pressed(rl.KEY_ENTER) or \
                           (gamepad_j1_conectado and rl.is_gamepad_button_pressed(modelo.GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_DOWN)) or \
                           (gamepad_j2_conectado and rl.is_gamepad_button_pressed(modelo.GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_DOWN)) # A
    
    entradas['menu_atras'] = rl.is_key_pressed(rl.KEY_ESCAPE) or \
                          (gamepad_j1_conectado and rl.is_gamepad_button_pressed(modelo.GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_RIGHT)) or \
                          (gamepad_j2_conectado and rl.is_gamepad_button_pressed(modelo.GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_RIGHT)) # B
    
    entradas['pausa'] = rl.is_key_pressed(rl.KEY_ESCAPE) or \
                     (gamepad_j1_conectado and rl.is_gamepad_button_pressed(modelo.GAMEPAD_J1, rl.GAMEPAD_BUTTON_MIDDLE_RIGHT)) or \
                     (gamepad_j2_conectado and rl.is_gamepad_button_pressed(modelo.GAMEPAD_J2, rl.GAMEPAD_BUTTON_MIDDLE_RIGHT)) # Start
    
    entradas['cualquier_tecla'] = (rl.get_key_pressed() != 0 or rl.get_gamepad_button_pressed() != 0)

    # --- Inputs de Movimiento J1 ---
    j1_move_input = 0.0
    if rl.is_key_down(rl.KEY_W): j1_move_input = -1.0
    if rl.is_key_down(rl.KEY_S): j1_move_input = 1.0
    
    if gamepad_j1_conectado:
        axis_y_j1 = rl.get_gamepad_axis_movement(modelo.GAMEPAD_J1, modelo.GAMEPAD_AXIS_Y)
        if abs(axis_y_j1) > modelo.GAMEPAD_AXIS_DEADZONE:
            j1_move_input = axis_y_j1
        else:
            if rl.is_gamepad_button_down(modelo.GAMEPAD_J1, rl.GAMEPAD_BUTTON_LEFT_FACE_UP): j1_move_input = -1.0
            if rl.is_gamepad_button_down(modelo.GAMEPAD_J1, rl.GAMEPAD_BUTTON_LEFT_FACE_DOWN): j1_move_input = 1.0
    entradas['j1_movimiento'] = j1_move_input

    # --- Inputs de Habilidad J1 ---
    entradas['j1_super_boost'] = rl.is_key_pressed(rl.KEY_A) or \
                              (gamepad_j1_conectado and (rl.is_gamepad_button_pressed(modelo.GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_RIGHT) or \
                                                          rl.is_gamepad_button_pressed(modelo.GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_UP))) # B/Y
    
    entradas['j1_boost_normal'] = rl.is_key_down(rl.KEY_D) or \
                               (gamepad_j1_conectado and (rl.is_gamepad_button_down(modelo.GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_DOWN) or \
                                                           rl.is_gamepad_button_down(modelo.GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_LEFT))) # A/X

    # --- Inputs de Movimiento J2 (si es multi) ---
    j2_move_input = 0.0
    if rl.is_key_down(rl.KEY_UP): j2_move_input = -1.0
    if rl.is_key_down(rl.KEY_DOWN): j2_move_input = 1.0
    
    if gamepad_j2_conectado:
        axis_y_j2 = rl.get_gamepad_axis_movement(modelo.GAMEPAD_J2, modelo.GAMEPAD_AXIS_Y)
        if abs(axis_y_j2) > modelo.GAMEPAD_AXIS_DEADZONE:
            j2_move_input = axis_y_j2
        else:
            if rl.is_gamepad_button_down(modelo.GAMEPAD_J2, rl.GAMEPAD_BUTTON_LEFT_FACE_UP): j2_move_input = -1.0
            if rl.is_gamepad_button_down(modelo.GAMEPAD_J2, rl.GAMEPAD_BUTTON_LEFT_FACE_DOWN): j2_move_input = 1.0
    entradas['j2_movimiento'] = j2_move_input

    # --- Inputs de Habilidad J2 (si es multi) ---
    entradas['j2_super_boost'] = rl.is_key_pressed(rl.KEY_RIGHT) or \
                              (gamepad_j2_conectado and (rl.is_gamepad_button_pressed(modelo.GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_RIGHT) or \
                                                          rl.is_gamepad_button_pressed(modelo.GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_UP)))   # B/Y
    
    entradas['j2_boost_normal'] = rl.is_key_down(rl.KEY_LEFT) or \
                               (gamepad_j2_conectado and (rl.is_gamepad_button_down(modelo.GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_DOWN) or \
                                                           rl.is_gamepad_button_down(modelo.GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_LEFT))) # A/X

    return entradas