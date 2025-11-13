# modelo.py (Version Funcional)
"""
fecha: 2025/10/31
Autor: Alejandro Uzcategui, Gabriel Guedez, Hector Vargas
-
descripcion: Componente "Modelo" (MVC) - Version Funcional.
Contiene todas las constantes, el estado del juego (en un diccionario) y 
la logica pura del juego (fisicas, IA, estamina).
NO CONTIENE CODIGO DE RAYLIB (excepto 'winsound' para feedback).
NO USA CLASES (POO).
"""
try:
    import winsound
    _WINSOUND_DISPONIBLE = True
except ImportError:
    print("Advertencia: 'winsound' no disponible en este SO. No habra efectos de sonido.")
    # Creamos un flag para no intentar usar la biblioteca
    _WINSOUND_DISPONIBLE = False
    
import random
import datetime
import os
import math

#========================
# Constantes Globales
#========================
# (Todas las constantes se mantienen igual)
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
GAME_TITLE = "Juego de Ping Pong"
COLOR_FONDO_AZUL = (16, 24, 48, 255) # RGBA
VERSION_JUEGO = "v0.96 (Funcional)" 
PUNTOS_POR_PARTIDA = 12
PARTIDAS_PARA_GANAR = 2
TIEMPO_AUMENTO_VELOCIDAD = 3.5 
FACTOR_AUMENTO = 1.075
COYOTE_TIME_BUFFER = 5
MAX_STAMINA = 1.0 
STAMINA_REGEN_TIME = MAX_STAMINA * 1.2
STAMINA_PENALTY_TIME = MAX_STAMINA * 1.5
BOOST_FACTOR = 2.0
BOOST_HIT_COST = MAX_STAMINA * 0.15
SUPER_BOOST_COST = MAX_STAMINA / 3.0
SUPER_BOOST_DURATION = 0.08
SUPER_BOOST_SPEED_FACTOR = 7.5
SUPER_BOOST_EFFECT_WINDOW = 0.1
SUPER_BOOST_TAP_DELAY = 0.5
STAMINA_REGEN_TIME_SUPER_1 = STAMINA_REGEN_TIME / 1.4
STAMINA_PENALTY_TIME_SUPER_2 = STAMINA_PENALTY_TIME / 1.3
SUPER_BOOST_FLASH_DURATION = 0.06
STAMINA_BAR_WIDTH = 80
BALL_TRAIL_LENGTH = 15
PADDLE_TRAIL_LENGTH = 8
BOOST_HIT_Y_VELOCITY_RANGE = 10.0
COLOR_LERP_SPEED = 10.0 
WHITE_TUPLE = (255, 255, 255, 255)
J1_BOOST_COLOR_TUPLE = (0, 228, 48, 255)
J2_BOOST_COLOR_TUPLE = (230, 41, 55, 255)
FLASH_COLOR_TUPLE = (253, 249, 0, 255)
ESTADO_MENU_PRINCIPAL = 0
ESTADO_SELECCION_MODO = 1
ESTADO_SELECCION_DIFICULTAD = 2
ESTADO_JUGANDO = 3
ESTADO_PAUSA = 4
ESTADO_GAME_OVER = 5
ESTADO_HISTORIAL = 6
ESTADO_CONTROLES = 7
GAMEPAD_J1 = 0
GAMEPAD_J2 = 1
GAMEPAD_AXIS_Y = 1
GAMEPAD_AXIS_DEADZONE = 0.2
GAMEPAD_MENU_DEADZONE = 0.5

#========================
# Funciones de Creacion de Estado
#========================

def crear_entradas_vacias():
    """
    Crea un diccionario para las entradas.
    Reemplaza la clase 'Entradas'.
    """
    return {
        'j1_movimiento': 0.0,
        'j2_movimiento': 0.0,
        'j1_boost_normal': False,
        'j1_super_boost': False,
        'j2_boost_normal': False,
        'j2_super_boost': False,
        'menu_arriba': False,
        'menu_abajo': False,
        'menu_aceptar': False,
        'menu_atras': False,
        'pausa': False,
        'cualquier_tecla': False,
    }

def crear_estado_inicial():
    """
    Crea y retorna un diccionario con todo el estado inicial del juego.
    Reemplaza a GameState.__init__
    """
    estado = {}
    
    estado['debe_cerrar'] = False # Flag para notificar al main.py
    
    # --- Estado de la App ---
    estado['estado_actual'] = ESTADO_MENU_PRINCIPAL
    estado['estado_previo'] = ESTADO_MENU_PRINCIPAL 
    estado['opcion_menu_seleccionada'] = 0
    estado['modo_juego'] = "ia"
    estado['dificultad_ia'] = "normal"
    estado['historial_lineas'] = []
    
    # --- Estado del Controlador (movido aqui) ---
    estado['axis_j1_neutral'] = True
    estado['axis_j2_neutral'] = True

    # --- Estado del Juego ---
    estado['paddle_height'] = 100
    estado['paddle_width'] = 15
    estado['paddle_speed_jugador_base'] = 7
    estado['paddle_speed_j1'] = estado['paddle_speed_jugador_base']
    estado['paddle_speed_op'] = estado['paddle_speed_jugador_base']
    estado['ball_radius'] = 10
    estado['player1_y'] = SCREEN_HEIGHT // 2 - estado['paddle_height'] // 2
    estado['oponente_y'] = SCREEN_HEIGHT // 2 - estado['paddle_height'] // 2
    estado['velocidad_ia'] = 6
    estado['player1_puntos'] = 0
    estado['oponente_puntos'] = 0
    estado['player1_partidas'] = 0
    estado['oponente_partidas'] = 0
    estado['game_over'] = False
    estado['winner'] = ""
    
    # Inicializa la pelota llamando a la funcion de reseteo
    # (ya no es un metodo)
    ball_x, ball_y, ball_speed_x, ball_speed_y = _reset_pelota_valores()
    estado['ball_x'] = ball_x
    estado['ball_y'] = ball_y
    estado['ball_speed_x'] = ball_speed_x
    estado['ball_speed_y'] = ball_speed_y
    
    estado['ball_color_tuple'] = WHITE_TUPLE
    estado['ball_trail'] = []
    estado['player1_paddle_trail'] = []
    estado['oponente_paddle_trail'] = []
    estado['tiempo_acumulado'] = 0.0
    estado['tiempo_partida'] = 0.0
    estado['multiplicador_velocidad'] = 1.0
    estado['player1_stamina'] = MAX_STAMINA
    estado['player1_stamina_cooldown'] = 0.0
    estado['player1_stamina_regen_delay'] = 0.0
    estado['player1_super_boost_timer'] = 0.0
    estado['player1_super_boost_flash_timer'] = 0.0
    estado['player1_dash_effect_window_timer'] = 0.0
    estado['player1_is_boosting'] = False
    estado['player1_current_regen_time'] = STAMINA_REGEN_TIME
    estado['player1_current_penalty_time'] = STAMINA_PENALTY_TIME
    estado['p1_color_r'] = 255.0
    estado['p1_color_g'] = 255.0
    estado['p1_color_b'] = 255.0
    estado['paddle_color_j1_tuple'] = WHITE_TUPLE
    estado['oponente_stamina'] = MAX_STAMINA
    estado['oponente_stamina_cooldown'] = 0.0
    estado['oponente_stamina_regen_delay'] = 0.0
    estado['oponente_super_boost_timer'] = 0.0
    estado['oponente_super_boost_flash_timer'] = 0.0
    estado['oponente_dash_effect_window_timer'] = 0.0
    estado['oponente_is_boosting'] = False
    estado['oponente_current_regen_time'] = STAMINA_REGEN_TIME
    estado['oponente_current_penalty_time'] = STAMINA_PENALTY_TIME
    estado['op_color_r'] = 255.0
    estado['op_color_g'] = 255.0
    estado['op_color_b'] = 255.0
    estado['paddle_color_op_tuple'] = WHITE_TUPLE
    estado['punto_anotado'] = False
    estado['ultimo_anotador'] = ""
    estado['partida_ganada_por_alguien'] = False
    estado['player1_is_moving'] = False
    estado['oponente_is_moving'] = False
    
    return estado

#========================
# Funciones de Reseteo y Guardado
# (Ahora son funciones independientes)
#========================

def _reset_pelota_valores():
    """Esta funcion no necesita estado, solo retorna valores."""
    ball_x = SCREEN_WIDTH // 2
    ball_y = SCREEN_HEIGHT // 2
    direccion_x = random.choice([-1, 1])
    ball_speed_x = 5 * direccion_x
    ball_speed_y = random.uniform(2.0, 4.0) * random.choice([-1, 1])
    return ball_x, ball_y, ball_speed_x, ball_speed_y

def _reset_juego_completo(estado):
    """
    Resetea el estado del juego a su configuracion inicial.
    Modifica el diccionario 'estado' que recibe.
    """
    estado['player1_y'] = SCREEN_HEIGHT // 2 - estado['paddle_height'] // 2
    estado['oponente_y'] = SCREEN_HEIGHT // 2 - estado['paddle_height'] // 2
    estado['player1_puntos'], estado['oponente_puntos'] = 0, 0
    estado['player1_partidas'], estado['oponente_partidas'] = 0, 0
    
    ball_x, ball_y, ball_speed_x, ball_speed_y = _reset_pelota_valores()
    estado['ball_x'] = ball_x
    estado['ball_y'] = ball_y
    estado['ball_speed_x'] = ball_speed_x
    estado['ball_speed_y'] = ball_speed_y
    
    estado['ball_color_tuple'], estado['ball_trail'] = WHITE_TUPLE, []
    estado['player1_paddle_trail'], estado['oponente_paddle_trail'] = [], []
    estado['game_over'], estado['punto_anotado'], estado['partida_ganada_por_alguien'] = False, False, False
    estado['tiempo_partida'], estado['multiplicador_velocidad'], estado['tiempo_acumulado'] = 0.0, 1.0, 0.0
    estado['player1_stamina'], estado['oponente_stamina'] = MAX_STAMINA, MAX_STAMINA
    estado['player1_stamina_cooldown'], estado['oponente_stamina_cooldown'] = 0.0, 0.0
    
    # Retornamos el estado modificado (aunque lo modificamos en el sitio)
    return estado

def _guardar_historial(estado):
    """
    Toma el estado actual para leer los datos de la partida.
    Ya no usa 'self'.
    """
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    nombre_oponente = "IA" if estado['modo_juego'] == "ia" else "JUGADOR 2"
    modo_str = f"J1 vs {nombre_oponente}"
    if estado['dificultad_ia']: modo_str += f" ({estado['dificultad_ia']})"
    
    linea = f"[{ahora}] {estado['winner']} GANA ({estado['player1_partidas']} a {estado['oponente_partidas']}) - Modo: {modo_str}\n"
    try:
        with open("historial.txt", "a", encoding="utf-8") as f:
            f.write(linea)
    except Exception as e:
        print(f"Error al guardar historial: {e}")

def _leer_historial():
    """
    Lee el historial desde el archivo. No necesita estado.
    Retorna una lista de lineas.
    """
    if not os.path.exists("historial.txt"):
        return ["No hay historial. Juega una partida."]
    try:
        with open("historial.txt", "r", encoding="utf-8") as f:
            lineas = f.readlines()
        if not lineas:
            return ["El historial esta vacio."]
        return [linea.strip() for linea in reversed(lineas)]
    except Exception as e:
        return [f"Error al leer historial: {e}"]

#========================
# Bucle de Actualizacion Principal
#========================

def actualizar_estado(estado_juego, entradas, delta_tiempo):
    """
    Esta es la funcion principal de logica.
    Toma el estado, las entradas, y retorna el NUEVO estado.
    Reemplaza a GameState.actualizar_estado
    
    Nota: Para eficiencia, modificamos el diccionario 'estado_juego' 
    directamente en lugar de crear una copia profunda cada fotograma.
    """
    
    # El router de estado
    if estado_juego['estado_actual'] == ESTADO_MENU_PRINCIPAL:
        estado_juego = _actualizar_menu_principal(estado_juego, entradas)
    
    elif estado_juego['estado_actual'] == ESTADO_SELECCION_MODO:
        estado_juego = _actualizar_seleccion_modo(estado_juego, entradas)

    elif estado_juego['estado_actual'] == ESTADO_SELECCION_DIFICULTAD:
        estado_juego = _actualizar_seleccion_dificultad(estado_juego, entradas)

    elif estado_juego['estado_actual'] == ESTADO_HISTORIAL:
        if entradas['menu_atras'] or entradas['menu_aceptar']:
            estado_juego['estado_actual'] = ESTADO_MENU_PRINCIPAL
            estado_juego['opcion_menu_seleccionada'] = 1

    elif estado_juego['estado_actual'] == ESTADO_CONTROLES:
        if entradas['menu_atras'] or entradas['menu_aceptar']:
            estado_juego['estado_actual'] = estado_juego['estado_previo']

    elif estado_juego['estado_actual'] == ESTADO_PAUSA:
        estado_juego = _actualizar_pausa(estado_juego, entradas)

    elif estado_juego['estado_actual'] == ESTADO_GAME_OVER:
        if entradas['menu_aceptar']:
            estado_juego = _reset_juego_completo(estado_juego)
            estado_juego['estado_actual'] = ESTADO_JUGANDO
        if entradas['menu_atras']:
            estado_juego = _reset_juego_completo(estado_juego)
            estado_juego['estado_actual'] = ESTADO_MENU_PRINCIPAL
            estado_juego['opcion_menu_seleccionada'] = 0
    
    elif estado_juego['estado_actual'] == ESTADO_JUGANDO:
        estado_juego = _actualizar_juego(estado_juego, entradas, delta_tiempo)

    # Retornamos el estado modificado
    return estado_juego

#========================
# Funciones de Actualizacion de Estado
# (Reemplazan los metodos privados de GameState)
#========================

def _actualizar_menu_principal(estado, entradas):
    opciones_menu = ["Jugar", "Ver Historial", "Salir"]
    if entradas['menu_abajo']: 
        estado['opcion_menu_seleccionada'] = (estado['opcion_menu_seleccionada'] + 1) % len(opciones_menu)
    if entradas['menu_arriba']: 
        estado['opcion_menu_seleccionada'] = (estado['opcion_menu_seleccionada'] - 1 + len(opciones_menu)) % len(opciones_menu)
    
    if entradas['menu_aceptar']:
        if estado['opcion_menu_seleccionada'] == 0: # Jugar
            if _WINSOUND_DISPONIBLE:
                winsound.PlaySound("C:/Windows/Media/Speech Disambiguation.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
            estado['estado_actual'] = ESTADO_SELECCION_MODO
            estado['opcion_menu_seleccionada'] = 0
            
        elif estado['opcion_menu_seleccionada'] == 1: # Ver Historial
            if _WINSOUND_DISPONIBLE:
                winsound.PlaySound("C:/Windows/Media/Speech Disambiguation.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
            estado['historial_lineas'] = _leer_historial() # Llama a la funcion
            estado['estado_actual'] = ESTADO_HISTORIAL
        
        elif estado['opcion_menu_seleccionada'] == 2: # Salir
            if _WINSOUND_DISPONIBLE:
                winsound.PlaySound("C:/Windows/Media/Alarm02.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
            estado['debe_cerrar'] = True # Cambiamos el flag
            
    return estado


def _actualizar_seleccion_modo(estado, entradas):
    opciones_menu = ["Jugador vs IA", "Jugador 1 vs Jugador 2", "Volver"]
    if entradas['menu_abajo']: 
        estado['opcion_menu_seleccionada'] = (estado['opcion_menu_seleccionada'] + 1) % len(opciones_menu)
    if entradas['menu_arriba']: 
        estado['opcion_menu_seleccionada'] = (estado['opcion_menu_seleccionada'] - 1 + len(opciones_menu)) % len(opciones_menu)
    
    if entradas['menu_aceptar']:
        if _WINSOUND_DISPONIBLE:
            winsound.PlaySound("C:/Windows/Media/Speech Disambiguation.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        
        if estado['opcion_menu_seleccionada'] == 0: # Jugar vs IA
            estado['modo_juego'] = "ia"
            estado['estado_actual'] = ESTADO_SELECCION_DIFICULTAD
            estado['opcion_menu_seleccionada'] = 0
        elif estado['opcion_menu_seleccionada'] == 1: # J1 vs J2
            estado['modo_juego'] = "multi"
            estado['dificultad_ia'] = None
            estado['estado_actual'] = ESTADO_JUGANDO
            estado = _reset_juego_completo(estado)
        elif estado['opcion_menu_seleccionada'] == 2: # Volver
            estado['estado_actual'] = ESTADO_MENU_PRINCIPAL
            estado['opcion_menu_seleccionada'] = 0
            
    if entradas['menu_atras']:
        estado['estado_actual'] = ESTADO_MENU_PRINCIPAL
        estado['opcion_menu_seleccionada'] = 0
        
    return estado

def _actualizar_seleccion_dificultad(estado, entradas):
    opciones_menu = ["Facil", "Normal", "Dificil", "Extremo (Jaque Mate)", "Volver"]
    if entradas['menu_abajo']: 
        estado['opcion_menu_seleccionada'] = (estado['opcion_menu_seleccionada'] + 1) % len(opciones_menu)
    if entradas['menu_arriba']: 
        estado['opcion_menu_seleccionada'] = (estado['opcion_menu_seleccionada'] - 1 + len(opciones_menu)) % len(opciones_menu)
    
    if entradas['menu_aceptar']:
        if _WINSOUND_DISPONIBLE:
            winsound.PlaySound("C:/Windows/Media/Speech Disambiguation.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        
        if estado['opcion_menu_seleccionada'] == 0: 
            estado['dificultad_ia'], estado['velocidad_ia'] = "facil", 4
        elif estado['opcion_menu_seleccionada'] == 1: 
            estado['dificultad_ia'], estado['velocidad_ia'] = "normal", 6
        elif estado['opcion_menu_seleccionada'] == 2: 
            estado['dificultad_ia'], estado['velocidad_ia'] = "dificil", 9
        elif estado['opcion_menu_seleccionada'] == 3: 
            estado['dificultad_ia'], estado['velocidad_ia'] = "extremo", 11
        elif estado['opcion_menu_seleccionada'] == 4: # Volver
            estado['estado_actual'] = ESTADO_SELECCION_MODO
            estado['opcion_menu_seleccionada'] = 0
            return estado # Salir de la funcion
        
        estado['estado_actual'] = ESTADO_JUGANDO
        estado = _reset_juego_completo(estado)
    
    if entradas['menu_atras']:
        estado['estado_actual'] = ESTADO_SELECCION_MODO
        estado['opcion_menu_seleccionada'] = 0
        
    return estado

def _actualizar_pausa(estado, entradas):
    opciones_menu = ["Continuar", "Controles", "Salir al Menu Principal"]
    if entradas['menu_abajo']: 
        estado['opcion_menu_seleccionada'] = (estado['opcion_menu_seleccionada'] + 1) % len(opciones_menu)
    if entradas['menu_arriba']: 
        estado['opcion_menu_seleccionada'] = (estado['opcion_menu_seleccionada'] - 1 + len(opciones_menu)) % len(opciones_menu)
    
    if entradas['menu_atras'] or entradas['pausa']:
        estado['estado_actual'] = ESTADO_JUGANDO
    
    if entradas['menu_aceptar']:
        if estado['opcion_menu_seleccionada'] == 0: # Continuar
            if _WINSOUND_DISPONIBLE:
                winsound.PlaySound("C:/Windows/Media/Speech On.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
            estado['estado_actual'] = ESTADO_JUGANDO
        elif estado['opcion_menu_seleccionada'] == 1: # Controles
            estado['estado_previo'] = ESTADO_PAUSA
            estado['estado_actual'] = ESTADO_CONTROLES
        elif estado['opcion_menu_seleccionada'] == 2: # Salir al Menu
            if _WINSOUND_DISPONIBLE:
                winsound.PlaySound("C:/Windows/Media/Alarm02.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
            estado['estado_actual'] = ESTADO_MENU_PRINCIPAL
            estado['opcion_menu_seleccionada'] = 0
            
    return estado

def _actualizar_juego(estado, entradas, delta_tiempo):
    
    # --- Logica de Pausa por Punto ---
    if estado['punto_anotado']:
        if entradas['cualquier_tecla']:
            estado['punto_anotado'] = False
            estado['tiempo_partida'] = 0.0
            estado['multiplicador_velocidad'] = 1.0
            estado['tiempo_acumulado'] = 0.0
            if estado['partida_ganada_por_alguien']:
                estado['player1_puntos'], estado['oponente_puntos'] = 0, 0
                estado['partida_ganada_por_alguien'] = False
            
            ball_x, ball_y, ball_speed_x, ball_speed_y = _reset_pelota_valores()
            estado['ball_x'] = ball_x
            estado['ball_y'] = ball_y
            estado['ball_speed_x'] = ball_speed_x
            estado['ball_speed_y'] = ball_speed_y
            
            estado['ball_color_tuple'], estado['ball_trail'] = WHITE_TUPLE, []
            estado['player1_paddle_trail'], estado['oponente_paddle_trail'] = [], []
        else:
            return estado # Salir de la actualizacion, estamos pausados

    # --- Logica de Pausa (ESC o Start) ---
    elif entradas['pausa']:
        if _WINSOUND_DISPONIBLE:
            winsound.PlaySound("C:/Windows/Media/Speech Sleep.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        estado['estado_actual'] = ESTADO_PAUSA
        estado['opcion_menu_seleccionada'] = 0
        return estado

    # --- ========================================== ---
    # ---         LOGICA DE JUEGO BASICA           ---
    # --- ========================================== ---
    
    estado['tiempo_partida'] += delta_tiempo
    estado['tiempo_acumulado'] += delta_tiempo
    if estado['tiempo_acumulado'] >= TIEMPO_AUMENTO_VELOCIDAD:
        estado['tiempo_acumulado'] = 0.0
        estado['ball_speed_x'] *= FACTOR_AUMENTO
        estado['ball_speed_y'] *= FACTOR_AUMENTO
        estado['multiplicador_velocidad'] *= FACTOR_AUMENTO
    
    estado['ball_x'] += estado['ball_speed_x']
    estado['ball_y'] += estado['ball_speed_y']
    
    if estado['ball_y'] - estado['ball_radius'] <= 0 or \
       estado['ball_y'] + estado['ball_radius'] >= SCREEN_HEIGHT:
        estado['ball_speed_y'] *= -1
        estado['ball_speed_y'] *= random.uniform(1.0, 1.2)
        if _WINSOUND_DISPONIBLE:
            winsound.PlaySound("C:/Windows/Media/Windows Menu Command.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

    estado['player1_is_moving'] = False
    estado['oponente_is_moving'] = False
    estado['player1_is_boosting'] = False
    estado['oponente_is_boosting'] = False
    
    j1_move_input = entradas['j1_movimiento']
    j2_move_input = entradas['j2_movimiento']

    # --- ========================================== ---
    # ---       LOGICA DE MECANICAS AVANZADAS      ---
    # --- ========================================== ---

    # --- 1. Inputs Avanzados (IA) ---
    boost_j1_tapped = entradas['j1_super_boost']
    boost_j1_down = entradas['j1_boost_normal']
    boost_j2_tapped = entradas['j2_super_boost']
    boost_j2_down = entradas['j2_boost_normal']

    if estado['modo_juego'] == "ia":
        if estado['dificultad_ia'] == "extremo":
            estado['oponente_is_moving'] = True
            target_y = estado['ball_y'] - (estado['paddle_height'] * 0.1) if estado['ball_y'] > SCREEN_HEIGHT / 2 else estado['ball_y'] - (estado['paddle_height'] * 0.9)
            distancia_y_ia = abs((estado['oponente_y'] + estado['paddle_height'] / 2) - estado['ball_y'])
            
            if distancia_y_ia > 250 and estado['oponente_stamina'] >= SUPER_BOOST_COST and estado['oponente_stamina_cooldown'] <= 0:
                boost_j2_tapped = True
            elif distancia_y_ia > 70 and estado['oponente_stamina'] > 0.2 and estado['oponente_stamina_cooldown'] <= 0:
                boost_j2_down = True

            if estado['oponente_y'] > target_y: 
                estado['oponente_y'] -= estado['velocidad_ia']
            elif estado['oponente_y'] < target_y: 
                estado['oponente_y'] += estado['velocidad_ia']
            j2_move_input = 0
        
        elif estado['dificultad_ia'] == "dificil":
            if estado['oponente_y'] + estado['paddle_height'] // 2 < estado['ball_y']: 
                j2_move_input = 1.0
            elif estado['oponente_y'] + estado['paddle_height'] // 2 > estado['ball_y']: 
                j2_move_input = -1.0
        
        else: # Facil / Normal
            if estado['oponente_y'] + estado['paddle_height'] // 2 < estado['ball_y'] - 10: 
                j2_move_input = 1.0
            elif estado['oponente_y'] + estado['paddle_height'] // 2 > estado['ball_y'] + 10: 
                j2_move_input = -1.0


    # --- 2. Logica de Estamina J1 (Boost/Dash) ---
    estado['paddle_speed_j1'] = estado['paddle_speed_jugador_base']
    target_color_j1 = WHITE_TUPLE 

    if estado['player1_super_boost_flash_timer'] > 0:
        estado['player1_super_boost_flash_timer'] -= delta_tiempo
        target_color_j1 = FLASH_COLOR_TUPLE
    
    if estado['player1_dash_effect_window_timer'] > 0:
        estado['player1_dash_effect_window_timer'] -= delta_tiempo

    if estado['player1_super_boost_timer'] > 0:
        estado['player1_super_boost_timer'] -= delta_tiempo
        estado['paddle_speed_j1'] *= SUPER_BOOST_SPEED_FACTOR
        estado['player1_is_boosting'] = True
        if estado['player1_super_boost_flash_timer'] <= 0:
            target_color_j1 = J1_BOOST_COLOR_TUPLE
    
    elif estado['player1_dash_effect_window_timer'] > 0:
        estado['player1_is_boosting'] = True
        target_color_j1 = J1_BOOST_COLOR_TUPLE
    
    elif estado['player1_stamina_cooldown'] > 0:
        estado['player1_stamina_cooldown'] -= delta_tiempo
        estado['player1_stamina'] += delta_tiempo * (MAX_STAMINA / estado['player1_current_penalty_time'])
        if estado['player1_stamina'] >= MAX_STAMINA:
            estado['player1_stamina'] = MAX_STAMINA
            estado['player1_stamina_cooldown'] = 0
    
    elif estado['player1_stamina_regen_delay'] > 0:
        estado['player1_stamina_regen_delay'] -= delta_tiempo
    
    elif boost_j1_tapped and estado['player1_stamina'] >= SUPER_BOOST_COST:
        estado['player1_stamina'] -= SUPER_BOOST_COST
        estado['player1_super_boost_timer'] = SUPER_BOOST_DURATION
        estado['player1_super_boost_flash_timer'] = SUPER_BOOST_FLASH_DURATION
        estado['player1_dash_effect_window_timer'] = SUPER_BOOST_EFFECT_WINDOW
        
        if estado['player1_stamina'] < SUPER_BOOST_COST: 
            estado['player1_stamina'] = 0
            estado['player1_stamina_cooldown'] = STAMINA_PENALTY_TIME_SUPER_2
            estado['player1_current_penalty_time'] = STAMINA_PENALTY_TIME_SUPER_2
        else:
            estado['player1_stamina_regen_delay'] = SUPER_BOOST_TAP_DELAY
            estado['player1_current_regen_time'] = STAMINA_REGEN_TIME_SUPER_1

    elif boost_j1_down:
        estado['player1_is_boosting'] = True
        estado['paddle_speed_j1'] *= BOOST_FACTOR
        target_color_j1 = J1_BOOST_COLOR_TUPLE
        estado['player1_stamina'] -= delta_tiempo
        
        if estado['player1_stamina'] <= 0:
            estado['player1_stamina'] = 0
            estado['player1_stamina_cooldown'] = STAMINA_PENALTY_TIME
            estado['player1_current_penalty_time'] = STAMINA_PENALTY_TIME
        
        estado['player1_current_regen_time'] = STAMINA_REGEN_TIME

    else:
        if estado['player1_stamina'] < MAX_STAMINA:
            estado['player1_stamina'] += delta_tiempo * (MAX_STAMINA / estado['player1_current_regen_time'])
            if estado['player1_stamina'] >= MAX_STAMINA:
                estado['player1_stamina'] = MAX_STAMINA
                estado['player1_current_regen_time'] = STAMINA_REGEN_TIME
    
    
    # --- 3. Logica de Estamina J2 / IA Extrema ---
    estado['paddle_speed_op'] = estado['paddle_speed_jugador_base']
    target_color_op = WHITE_TUPLE
    
    if estado['modo_juego'] == "multi" or (estado['modo_juego'] == "ia" and estado['dificultad_ia'] == "extremo"):
        if estado['oponente_super_boost_flash_timer'] > 0:
            estado['oponente_super_boost_flash_timer'] -= delta_tiempo
            target_color_op = FLASH_COLOR_TUPLE
        
        if estado['oponente_dash_effect_window_timer'] > 0:
            estado['oponente_dash_effect_window_timer'] -= delta_tiempo

        if estado['oponente_super_boost_timer'] > 0:
            estado['oponente_super_boost_timer'] -= delta_tiempo
            estado['paddle_speed_op'] *= SUPER_BOOST_SPEED_FACTOR
            estado['oponente_is_boosting'] = True
            if estado['oponente_super_boost_flash_timer'] <= 0:
                target_color_op = J2_BOOST_COLOR_TUPLE
        
        elif estado['oponente_dash_effect_window_timer'] > 0:
            estado['oponente_is_boosting'] = True
            target_color_op = J2_BOOST_COLOR_TUPLE

        elif estado['oponente_stamina_cooldown'] > 0:
            estado['oponente_stamina_cooldown'] -= delta_tiempo
            estado['oponente_stamina'] += delta_tiempo * (MAX_STAMINA / estado['oponente_current_penalty_time'])
            if estado['oponente_stamina'] >= MAX_STAMINA:
                estado['oponente_stamina'] = MAX_STAMINA
                estado['oponente_stamina_cooldown'] = 0
        
        elif estado['oponente_stamina_regen_delay'] > 0:
            estado['oponente_stamina_regen_delay'] -= delta_tiempo
        
        elif boost_j2_tapped and estado['oponente_stamina'] >= SUPER_BOOST_COST:
            estado['oponente_stamina'] -= SUPER_BOOST_COST
            estado['oponente_super_boost_timer'] = SUPER_BOOST_DURATION
            estado['oponente_super_boost_flash_timer'] = SUPER_BOOST_FLASH_DURATION
            estado['oponente_dash_effect_window_timer'] = SUPER_BOOST_EFFECT_WINDOW
            
            if estado['oponente_stamina'] < SUPER_BOOST_COST:
                estado['oponente_stamina'] = 0
                estado['oponente_stamina_cooldown'] = STAMINA_PENALTY_TIME_SUPER_2
                estado['oponente_current_penalty_time'] = STAMINA_PENALTY_TIME_SUPER_2
            else:
                estado['oponente_stamina_regen_delay'] = SUPER_BOOST_TAP_DELAY
                estado['oponente_current_regen_time'] = STAMINA_REGEN_TIME_SUPER_1

        elif boost_j2_down:
            estado['oponente_is_boosting'] = True
            estado['paddle_speed_op'] *= BOOST_FACTOR
            target_color_op = J2_BOOST_COLOR_TUPLE
            estado['oponente_stamina'] -= delta_tiempo
            
            if estado['oponente_stamina'] <= 0:
                estado['oponente_stamina'] = 0
                estado['oponente_stamina_cooldown'] = STAMINA_PENALTY_TIME
                estado['oponente_current_penalty_time'] = STAMINA_PENALTY_TIME
            
            estado['oponente_current_regen_time'] = STAMINA_REGEN_TIME

        else:
            if estado['oponente_stamina'] < MAX_STAMINA:
                estado['oponente_stamina'] += delta_tiempo * (MAX_STAMINA / estado['oponente_current_regen_time'])
                if estado['oponente_stamina'] >= MAX_STAMINA:
                    estado['oponente_stamina'] = MAX_STAMINA
                    estado['oponente_current_regen_time'] = STAMINA_REGEN_TIME
    
    # --- 4. Aplicar Movimiento Avanzado ---
    if estado['dificultad_ia'] != "extremo":
        estado['player1_y'] += estado['paddle_speed_j1'] * j1_move_input
        estado['oponente_y'] += estado['paddle_speed_op'] * j2_move_input
    else:
        estado['player1_y'] += estado['paddle_speed_j1'] * j1_move_input
    
    if j1_move_input != 0.0: estado['player1_is_moving'] = True
    if j2_move_input != 0.0: estado['oponente_is_moving'] = True

    if estado['player1_y'] < 0: estado['player1_y'] = 0
    if estado['player1_y'] > SCREEN_HEIGHT - estado['paddle_height']: estado['player1_y'] = SCREEN_HEIGHT - estado['paddle_height']
    if estado['oponente_y'] < 0: estado['oponente_y'] = 0
    if estado['oponente_y'] > SCREEN_HEIGHT - estado['paddle_height']: estado['oponente_y'] = SCREEN_HEIGHT - estado['paddle_height']


    # --- 5. Logica de Colision Avanzada (Boost Hit, Coyote) ---
    buffer_j1 = COYOTE_TIME_BUFFER if estado['player1_is_moving'] else 0
    buffer_op = COYOTE_TIME_BUFFER if estado['oponente_is_moving'] else 0
    
    # --- J1 Colision ---
    if (estado['ball_x'] - estado['ball_radius'] <= estado['paddle_width'] and 
        estado['player1_y'] - buffer_j1 <= estado['ball_y'] <= estado['player1_y'] + estado['paddle_height'] + buffer_j1 and 
        estado['ball_speed_x'] < 0):
        
        if estado['player1_is_boosting']:
            estado['ball_color_tuple'] = estado['paddle_color_j1_tuple']
            estado['ball_speed_y'] = random.uniform(-BOOST_HIT_Y_VELOCITY_RANGE, BOOST_HIT_Y_VELOCITY_RANGE)
            estado['ball_speed_x'] *= -1.1
            estado['player1_stamina'] = max(0, estado['player1_stamina'] - BOOST_HIT_COST)
        else:
            estado['ball_color_tuple'] = WHITE_TUPLE
            estado['ball_speed_x'] *= -1
            hit_position = (estado['ball_y'] - estado['player1_y']) / estado['paddle_height']
            estado['ball_speed_y'] = 8 * (hit_position - 0.5)
        
        if _WINSOUND_DISPONIBLE:
            winsound.PlaySound("C:/Windows/Media/Windows Information Bar.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

    # --- J2/Oponente Colision ---
    elif (estado['ball_x'] + estado['ball_radius'] >= SCREEN_WIDTH - estado['paddle_width'] and 
        estado['oponente_y'] - buffer_op <= estado['ball_y'] <= estado['oponente_y'] + estado['paddle_height'] + buffer_op and 
        estado['ball_speed_x'] > 0):
        
        if estado['oponente_is_boosting']:
            estado['ball_color_tuple'] = estado['paddle_color_op_tuple']
            estado['ball_speed_y'] = random.uniform(-BOOST_HIT_Y_VELOCITY_RANGE, BOOST_HIT_Y_VELOCITY_RANGE)
            estado['ball_speed_x'] *= -1.1
            estado['oponente_stamina'] = max(0, estado['oponente_stamina'] - BOOST_HIT_COST)
        else:
            estado['ball_color_tuple'] = WHITE_TUPLE
            estado['ball_speed_x'] *= -1
            hit_position = (estado['ball_y'] - estado['oponente_y']) / estado['paddle_height']
            estado['ball_speed_y'] = 8 * (hit_position - 0.5)
        
        if _WINSOUND_DISPONIBLE:
            winsound.PlaySound("C:/Windows/Media/Windows Information Bar.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)


    # --- 6. Logica de Puntuacion ---
    
    # Oponente anota
    elif (estado['ball_x'] + estado['ball_radius'] < 0): 
        estado['oponente_puntos'] += 1
        estado['punto_anotado'] = True
        estado['ultimo_anotador'] = "oponente"
        if _WINSOUND_DISPONIBLE:
            winsound.PlaySound("C:/Windows/Media/Windows Critical Stop.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        
        estado['player1_stamina'], estado['oponente_stamina'] = MAX_STAMINA, MAX_STAMINA
        estado['player1_stamina_cooldown'], estado['oponente_stamina_cooldown'] = 0.0, 0.0
        
        if estado['oponente_puntos'] >= PUNTOS_POR_PARTIDA:
            estado['oponente_partidas'] += 1
            estado['partida_ganada_por_alguien'] = True
            if estado['oponente_partidas'] >= PARTIDAS_PARA_GANAR:
                estado['game_over'] = True
                estado['winner'] = "IA" if estado['modo_juego'] == "ia" else "JUGADOR 2"
                _guardar_historial(estado)
    
    # J1 anota
    elif (estado['ball_x'] - estado['ball_radius'] > SCREEN_WIDTH): 
        estado['player1_puntos'] += 1
        estado['punto_anotado'] = True
        estado['ultimo_anotador'] = "j1"
        if _WINSOUND_DISPONIBLE:
            winsound.PlaySound("C:/Windows/Media/Windows Critical Stop.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

        estado['player1_stamina'], estado['oponente_stamina'] = MAX_STAMINA, MAX_STAMINA
        estado['player1_stamina_cooldown'], estado['oponente_stamina_cooldown'] = 0.0, 0.0
        
        if estado['player1_puntos'] >= PUNTOS_POR_PARTIDA:
            estado['player1_partidas'] += 1
            estado['partida_ganada_por_alguien'] = True
            if estado['player1_partidas'] >= PARTIDAS_PARA_GANAR:
                estado['game_over'] = True
                estado['winner'] = "JUGADOR 1"
                _guardar_historial(estado)
    
    if estado['game_over']:
        estado['estado_actual'] = ESTADO_GAME_OVER
        estado['opcion_menu_seleccionada'] = 0
    
    # --- 7. Logica de Color Suave (Lerp) ---
    lerp_factor = COLOR_LERP_SPEED * delta_tiempo
    estado['p1_color_r'] += (target_color_j1[0] - estado['p1_color_r']) * lerp_factor
    estado['p1_color_g'] += (target_color_j1[1] - estado['p1_color_g']) * lerp_factor
    estado['p1_color_b'] += (target_color_j1[2] - estado['p1_color_b']) * lerp_factor
    estado['paddle_color_j1_tuple'] = (int(estado['p1_color_r']), int(estado['p1_color_g']), int(estado['p1_color_b']), 255)
    
    estado['op_color_r'] += (target_color_op[0] - estado['op_color_r']) * lerp_factor
    estado['op_color_g'] += (target_color_op[1] - estado['op_color_g']) * lerp_factor
    estado['op_color_b'] += (target_color_op[2] - estado['op_color_b']) * lerp_factor
    estado['paddle_color_op_tuple'] = (int(estado['op_color_r']), int(estado['op_color_g']), int(estado['op_color_b']), 255)
    
    # --- 8. Logica de Estela (Pelota) ---
    estado['ball_trail'].append((estado['ball_x'], estado['ball_y'], estado['ball_color_tuple']))
    if len(estado['ball_trail']) > BALL_TRAIL_LENGTH:
        estado['ball_trail'].pop(0)

    # --- 9. Logica de Estela (Paddle) ---
    if estado['player1_is_boosting']:
        estado['player1_paddle_trail'].append((estado['player1_y'], estado['paddle_color_j1_tuple']))
    if (not estado['player1_is_boosting'] and estado['player1_paddle_trail']) or len(estado['player1_paddle_trail']) > PADDLE_TRAIL_LENGTH:
        estado['player1_paddle_trail'].pop(0)

    if estado['oponente_is_boosting']:
        estado['oponente_paddle_trail'].append((estado['oponente_y'], estado['paddle_color_op_tuple']))
    if (not estado['oponente_is_boosting'] and estado['oponente_paddle_trail']) or len(estado['oponente_paddle_trail']) > PADDLE_TRAIL_LENGTH:
        estado['oponente_paddle_trail'].pop(0)
        
    return estado