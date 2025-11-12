"""
fecha de inicio: 2025/10/31
Autor: Alejandro Uzcategui, Gabriel Guedez, Hector Vargas
-
descripcion: maneja toda la logica del programa, incluyendo menus
(ahora en Raylib) y el juego en si.
fecha de entrega: 2025/11/13
"""
#========================
#imports
import winsound
try:
    import raylibpy as rl
except ImportError:
    print("Error: No se pudo importar la biblioteca 'raylibpy'.")
    print("Por favor, instálela usando: pip install raylib-py")
    exit()

import random
import datetime
import os # Necesario para leer el historial
import math # Para el 'lerp' de color

#========================
# Constantes Globales
#========================

SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
GAME_TITLE = "Juego de Ping Pong"

COLOR_FONDO_AZUL = rl.Color(16, 24, 48, 255) # Azul marino oscuro
VERSION_JUEGO = "v0.91" # Version actualizada

# Constantes del Juego
PUNTOS_POR_PARTIDA = 12
PARTIDAS_PARA_GANAR = 2
TIEMPO_AUMENTO_VELOCIDAD = 2.5 
FACTOR_AUMENTO = 1.075
COYOTE_TIME_BUFFER = 5 # 5 pixeles de gracia

# ==================== Constantes de Habilidad ====================
MAX_STAMINA = 1.0 

# --- Boost Normal ---
STAMINA_REGEN_TIME = MAX_STAMINA * 1.2 # 20% mas lento
STAMINA_PENALTY_TIME = MAX_STAMINA * 1.5 # 50% mas lento
BOOST_FACTOR = 2.0
BOOST_HIT_COST = MAX_STAMINA * 0.15 # 15% de la barra

# --- Super Boost (Dash) ---
SUPER_BOOST_COST = MAX_STAMINA / 3.0 # 3 Cargas (33.33%)
SUPER_BOOST_DURATION = 0.08 # 80ms de movimiento (mas rapido)
SUPER_BOOST_SPEED_FACTOR = 7.5 # (mas rapido)
SUPER_BOOST_EFFECT_WINDOW = 0.1 # 100ms de *efecto* (da 20ms de margen)

SUPER_BOOST_TAP_DELAY = 0.5
STAMINA_REGEN_TIME_SUPER_1 = STAMINA_REGEN_TIME / 1.4
STAMINA_PENALTY_TIME_SUPER_2 = STAMINA_PENALTY_TIME / 1.3
SUPER_BOOST_FLASH_DURATION = 0.06

# --- Graficos ---
STAMINA_BAR_WIDTH = 80
BALL_TRAIL_LENGTH = 15
PADDLE_TRAIL_LENGTH = 8 # NUEVO: Estela de la paleta
BOOST_HIT_Y_VELOCITY_RANGE = 10.0

# --- Constantes de Color (para transicion suave) ---
COLOR_LERP_SPEED = 10.0 
WHITE_TUPLE = (255, 255, 255)
J1_BOOST_COLOR_TUPLE = (0, 228, 48)   # Raylib GREEN
J2_BOOST_COLOR_TUPLE = (230, 41, 55)   # Raylib RED
FLASH_COLOR_TUPLE = (253, 249, 0) # Raylib YELLOW

# --- GESTION DE ESTADOS ---
ESTADO_MENU_PRINCIPAL = 0
ESTADO_SELECCION_MODO = 1
ESTADO_SELECCION_DIFICULTAD = 2
ESTADO_JUGANDO = 3
ESTADO_PAUSA = 4
ESTADO_GAME_OVER = 5
ESTADO_HISTORIAL = 6
ESTADO_CONTROLES = 7

# --- Constantes de Gamepad (Xbox) ---
GAMEPAD_J1 = 0
GAMEPAD_J2 = 1
GAMEPAD_AXIS_Y = 1 # Joystick Izquierdo Eje Y
GAMEPAD_AXIS_DEADZONE = 0.2 # Deadzone para movimiento analogico
GAMEPAD_MENU_DEADZONE = 0.5 # Deadzone para menus

#========================
# Funciones de Reseteo y Guardado
#========================

def reset_pelota():
    ball_x = SCREEN_WIDTH // 2
    ball_y = SCREEN_HEIGHT // 2
    direccion_x = random.choice([-1, 1])
    ball_speed_x = 5 * direccion_x
    ball_speed_y = random.uniform(2.0, 4.0) * random.choice([-1, 1])
    return ball_x, ball_y, ball_speed_x, ball_speed_y

def guardar_historial(winner, score_j1, score_op, modo_juego_str):
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    linea = f"[{ahora}] {winner} GANA ({score_j1} a {score_op}) - Modo: {modo_juego_str}\n"
    try:
        with open("historial.txt", "a", encoding="utf-8") as f:
            f.write(linea)
    except Exception as e:
        print(f"Error al guardar historial: {e}")

def leer_historial():
    """Lee el historial.txt y devuelve una lista de lineas."""
    if not os.path.exists("histORIAL.txt"):
        return ["No hay historial. Juega una partida."]
    
    try:
        with open("historial.txt", "r", encoding="utf-8") as f:
            lineas = f.readlines()
        if not lineas:
            return ["El historial esta vacio."]
        
        # Devolvemos las lineas al reves (mas recientes primero)
        return [linea.strip() for linea in reversed(lineas)]
    except Exception as e:
        return [f"Error al leer historial: {e}"]

#========================
# (Gestor de Estados)
#========================

def iniciar_aplicacion_raylib():
    """
    Esta funcion reemplaza a 'mostrar_tui' y 'gestionar_juego'.
    Inicia Raylib y maneja todos los estados del programa.
    """
    
    # Inicializa la ventana
    rl.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE)
    
    # --- Cargar Icono ---
    try:
        icon_image = rl.load_image("icon.png") # Asegurate que "icon.png" exista
        rl.set_window_icon(icon_image)
        rl.unload_image(icon_image)
    except Exception as e:
        print(f"Advertencia: No se pudo cargar 'icon.png'. Usando icono por defecto. Error: {e}")

    winsound.PlaySound("C:/Windows/Media/notify.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
    rl.set_target_fps(90)
    
    # --- Variables de Estado ---
    estado_actual = ESTADO_MENU_PRINCIPAL
    estado_previo = ESTADO_MENU_PRINCIPAL 
    opcion_menu_seleccionada = 0
    modo_juego = "ia"
    dificultad_ia = "normal"
    historial_lineas = []
    
    # --- Variables del Juego ---
    paddle_height = 100
    paddle_width = 15
    paddle_speed_jugador_base = 7
    paddle_speed_j1 = paddle_speed_jugador_base
    paddle_speed_op = paddle_speed_jugador_base
    ball_radius = 10
    
    player1_y = SCREEN_HEIGHT // 2 - paddle_height // 2
    oponente_y = SCREEN_HEIGHT // 2 - paddle_height // 2
    ball_x, ball_y, ball_speed_x, ball_speed_y = reset_pelota()
    velocidad_ia = 6
    player1_puntos = 0
    oponente_puntos = 0
    player1_partidas = 0
    oponente_partidas = 0
    game_over = False
    winner = ""
    
    # --- Variables de Pelota (Color y Estela) ---
    ball_color = rl.WHITE
    ball_trail = []
    
    # --- NUEVO: Variables de Paddle (Estela) ---
    player1_paddle_trail = []
    oponente_paddle_trail = []
    
    # --- Variables de Tiempo y Velocidad ---
    tiempo_acumulado = 0.0
    tiempo_partida = 0.0
    multiplicador_velocidad = 1.0

    # --- Variables de Estamina (Jugador 1) ---
    player1_stamina = MAX_STAMINA
    player1_stamina_cooldown = 0.0
    player1_stamina_regen_delay = 0.0
    player1_super_boost_timer = 0.0
    player1_super_boost_flash_timer = 0.0
    player1_dash_effect_window_timer = 0.0
    player1_is_boosting = False
    player1_current_regen_time = STAMINA_REGEN_TIME
    player1_current_penalty_time = STAMINA_PENALTY_TIME
    p1_color_r, p1_color_g, p1_color_b = 255.0, 255.0, 255.0
    paddle_color_j1 = rl.WHITE
    
    # --- Variables de Estamina (Oponente / J2) ---
    oponente_stamina = MAX_STAMINA
    oponente_stamina_cooldown = 0.0
    oponente_stamina_regen_delay = 0.0
    oponente_super_boost_timer = 0.0
    oponente_super_boost_flash_timer = 0.0
    oponente_dash_effect_window_timer = 0.0
    oponente_is_boosting = False
    oponente_current_regen_time = STAMINA_REGEN_TIME
    oponente_current_penalty_time = STAMINA_PENALTY_TIME
    op_color_r, op_color_g, op_color_b = 255.0, 255.0, 255.0
    paddle_color_op = rl.WHITE

    # --- Variables para pausa post-punto ---
    punto_anotado = False
    ultimo_anotador = ""
    partida_ganada_por_alguien = False
    
    # Variables de Movimiento
    player1_is_moving = False
    oponente_is_moving = False

    rl.set_exit_key(0)
    
    # --- Variables de Deteccion de Mando ---
    gamepad_j1_conectado = False
    gamepad_j2_conectado = False
    axis_j1_neutral = True
    axis_j2_neutral = True

    # --- BUCLE PRINCIPAL DE LA APLICACION ---
    while not rl.window_should_close():
        
        # --- Deteccion de Mandos (constante) ---
        gamepad_j1_conectado = rl.is_gamepad_available(GAMEPAD_J1)
        gamepad_j2_conectado = rl.is_gamepad_available(GAMEPAD_J2)
        
        # --- Variables de Input (Mando) ---
        dpad_j1_up = rl.is_gamepad_button_pressed(GAMEPAD_J1, rl.GAMEPAD_BUTTON_LEFT_FACE_UP)
        dpad_j1_down = rl.is_gamepad_button_pressed(GAMEPAD_J1, rl.GAMEPAD_BUTTON_LEFT_FACE_DOWN)
        dpad_j2_up = rl.is_gamepad_button_pressed(GAMEPAD_J2, rl.GAMEPAD_BUTTON_LEFT_FACE_UP)
        dpad_j2_down = rl.is_gamepad_button_pressed(GAMEPAD_J2, rl.GAMEPAD_BUTTON_LEFT_FACE_DOWN)
        
        axis_y_j1_menu = rl.get_gamepad_axis_movement(GAMEPAD_J1, GAMEPAD_AXIS_Y) if gamepad_j1_conectado else 0
        axis_y_j2_menu = rl.get_gamepad_axis_movement(GAMEPAD_J2, GAMEPAD_AXIS_Y) if gamepad_j2_conectado else 0
        
        axis_j1_up = (gamepad_j1_conectado and axis_y_j1_menu < -GAMEPAD_MENU_DEADZONE and axis_j1_neutral)
        axis_j1_down = (gamepad_j1_conectado and axis_y_j1_menu > GAMEPAD_MENU_DEADZONE and axis_j1_neutral)
        axis_j2_up = (gamepad_j2_conectado and axis_y_j2_menu < -GAMEPAD_MENU_DEADZONE and axis_j2_neutral)
        axis_j2_down = (gamepad_j2_conectado and axis_y_j2_menu > GAMEPAD_MENU_DEADZONE and axis_j2_neutral)
        
        if axis_j1_up or axis_j1_down: axis_j1_neutral = False
        if axis_j2_up or axis_j2_down: axis_j2_neutral = False
        if gamepad_j1_conectado and -0.2 < axis_y_j1_menu < 0.2: axis_j1_neutral = True
        if gamepad_j2_conectado and -0.2 < axis_y_j2_menu < 0.2: axis_j2_neutral = True
        
        menu_arriba = rl.is_key_pressed(rl.KEY_UP) or dpad_j1_up or dpad_j2_up or axis_j1_up or axis_j2_up
        menu_abajo = rl.is_key_pressed(rl.KEY_DOWN) or dpad_j1_down or dpad_j2_down or axis_j1_down or axis_j2_down
        
        menu_aceptar = rl.is_key_pressed(rl.KEY_ENTER) or rl.is_gamepad_button_pressed(GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_DOWN) or rl.is_gamepad_button_pressed(GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_DOWN) # A
        menu_atras_btn = rl.is_key_pressed(rl.KEY_ESCAPE) or rl.is_gamepad_button_pressed(GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_RIGHT) or rl.is_gamepad_button_pressed(GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_RIGHT) # B
        
        juego_pausa_btn = rl.is_key_pressed(rl.KEY_ESCAPE) or rl.is_gamepad_button_pressed(GAMEPAD_J1, rl.GAMEPAD_BUTTON_MIDDLE_RIGHT) or rl.is_gamepad_button_pressed(GAMEPAD_J2, rl.GAMEPAD_BUTTON_MIDDLE_RIGHT)
        
        
        # -----------------------------------------------------
        # --- 1.(INPUTS Y LOGICA) ---
        # -----------------------------------------------------

        # --- ESTADO: MENU PRINCIPAL ---
        if estado_actual == ESTADO_MENU_PRINCIPAL:
            opciones_menu = ["Jugar", "Ver Historial", "Salir"]
            if menu_abajo: opcion_menu_seleccionada = (opcion_menu_seleccionada + 1) % len(opciones_menu)
            if menu_arriba: opcion_menu_seleccionada = (opcion_menu_seleccionada - 1 + len(opciones_menu)) % len(opciones_menu)
            if menu_aceptar:
                if opcion_menu_seleccionada == 0: # Jugar
                    winsound.PlaySound("C:/Windows/Media/Speech Disambiguation.wav", winsound.SND_FILENAME)
                    estado_actual = ESTADO_SELECCION_MODO
                    opcion_menu_seleccionada = 0
                elif opcion_menu_seleccionada == 1: # Ver Historial
                    winsound.PlaySound("C:/Windows/Media/Speech Disambiguation.wav", winsound.SND_FILENAME)
                    historial_lineas = leer_historial()
                    estado_actual = ESTADO_HISTORIAL
                elif opcion_menu_seleccionada == 2: # Salir
                    winsound.PlaySound("C:/Windows/Media/Alarm02.wav", winsound.SND_FILENAME)
                    break 

        # --- ESTADO: SELECCION DE MODO ---
        elif estado_actual == ESTADO_SELECCION_MODO:
            opciones_menu = ["Jugador vs IA", "Jugador 1 vs Jugador 2", "Volver"]
            if menu_abajo: opcion_menu_seleccionada = (opcion_menu_seleccionada + 1) % len(opciones_menu)
            if menu_arriba: opcion_menu_seleccionada = (opcion_menu_seleccionada - 1 + len(opciones_menu)) % len(opciones_menu)
            if menu_aceptar:
                winsound.PlaySound("C:/Windows/Media/Speech Disambiguation.wav", winsound.SND_FILENAME)
                if opcion_menu_seleccionada == 0: # Jugar vs IA
                    modo_juego = "ia"
                    estado_actual = ESTADO_SELECCION_DIFICULTAD
                    opcion_menu_seleccionada = 0
                elif opcion_menu_seleccionada == 1: # J1 vs J2
                    modo_juego = "multi"
                    dificultad_ia = None
                    estado_actual = ESTADO_JUGANDO
                    # --- Resetear el juego antes de empezar ---
                    player1_y, oponente_y = SCREEN_HEIGHT // 2 - paddle_height // 2, SCREEN_HEIGHT // 2 - paddle_height // 2
                    player1_puntos, oponente_puntos = 0, 0
                    player1_partidas, oponente_partidas = 0, 0
                    ball_x, ball_y, ball_speed_x, ball_speed_y = reset_pelota()
                    ball_color, ball_trail = rl.WHITE, []
                    player1_paddle_trail, oponente_paddle_trail = [], [] # NUEVO: Resetear estelas
                    game_over, punto_anotado, partida_ganada_por_alguien = False, False, False
                    tiempo_partida, multiplicador_velocidad, tiempo_acumulado = 0.0, 1.0, 0.0
                    player1_stamina, oponente_stamina = MAX_STAMINA, MAX_STAMINA
                    player1_stamina_cooldown, oponente_stamina_cooldown = 0.0, 0.0
                elif opcion_menu_seleccionada == 2: # Volver
                    estado_actual = ESTADO_MENU_PRINCIPAL
                    opcion_menu_seleccionada = 0
            if menu_atras_btn:
                estado_actual = ESTADO_MENU_PRINCIPAL
                opcion_menu_seleccionada = 0
        
        # --- ESTADO: SELECCION DE DIFICULTAD (si se eligio IA) ---
        elif estado_actual == ESTADO_SELECCION_DIFICULTAD:
            opciones_menu = ["Facil", "Normal", "Dificil", "Extremo (Jaque Mate)", "Volver"]
            if menu_abajo: opcion_menu_seleccionada = (opcion_menu_seleccionada + 1) % len(opciones_menu)
            if menu_arriba: opcion_menu_seleccionada = (opcion_menu_seleccionada - 1 + len(opciones_menu)) % len(opciones_menu)
            if menu_aceptar:
                winsound.PlaySound("C:/Windows/Media/Speech Disambiguation.wav", winsound.SND_FILENAME)
                if opcion_menu_seleccionada == 0: dificultad_ia, velocidad_ia = "facil", 4
                elif opcion_menu_seleccionada == 1: dificultad_ia, velocidad_ia = "normal", 6
                elif opcion_menu_seleccionada == 2: dificultad_ia, velocidad_ia = "dificil", 9
                elif opcion_menu_seleccionada == 3: dificultad_ia, velocidad_ia = "extremo", 11
                elif opcion_menu_seleccionada == 4: # Volver
                    estado_actual = ESTADO_SELECCION_MODO
                    opcion_menu_seleccionada = 0
                    continue
                
                estado_actual = ESTADO_JUGANDO
                # --- Resetear el juego antes de empezar ---
                player1_y, oponente_y = SCREEN_HEIGHT // 2 - paddle_height // 2, SCREEN_HEIGHT // 2 - paddle_height // 2
                player1_puntos, oponente_puntos = 0, 0
                player1_partidas, oponente_partidas = 0, 0
                ball_x, ball_y, ball_speed_x, ball_speed_y = reset_pelota()
                ball_color, ball_trail = rl.WHITE, []
                player1_paddle_trail, oponente_paddle_trail = [], [] # NUEVO: Resetear estelas
                game_over, punto_anotado, partida_ganada_por_alguien = False, False, False
                tiempo_partida, multiplicador_velocidad, tiempo_acumulado = 0.0, 1.0, 0.0
                player1_stamina, oponente_stamina = MAX_STAMINA, MAX_STAMINA
                player1_stamina_cooldown, oponente_stamina_cooldown = 0.0, 0.0
            if menu_atras_btn:
                estado_actual = ESTADO_SELECCION_MODO
                opcion_menu_seleccionada = 0

        # --- ESTADO: HISTORIAL ---
        elif estado_actual == ESTADO_HISTORIAL:
            if menu_atras_btn or menu_aceptar:
                estado_actual = ESTADO_MENU_PRINCIPAL
                opcion_menu_seleccionada = 1
        
        # --- ESTADO CONTROLES ---
        elif estado_actual == ESTADO_CONTROLES:
            if menu_atras_btn or menu_aceptar:
                estado_actual = estado_previo
                opcion_menu_seleccionada = 1

        # --- ESTADO: PAUSA ---
        elif estado_actual == ESTADO_PAUSA:
            opciones_menu = ["Continuar", "Controles", "Salir al Menu Principal"]
            if menu_abajo: opcion_menu_seleccionada = (opcion_menu_seleccionada + 1) % len(opciones_menu)
            if menu_arriba: opcion_menu_seleccionada = (opcion_menu_seleccionada - 1 + len(opciones_menu)) % len(opciones_menu)
            if menu_atras_btn or juego_pausa_btn:
                estado_actual = ESTADO_JUGANDO
            if menu_aceptar:
                if opcion_menu_seleccionada == 0: # Continuar
                    winsound.PlaySound("C:/Windows/Media/Speech On.wav", winsound.SND_FILENAME)
                    estado_actual = ESTADO_JUGANDO
                elif opcion_menu_seleccionada == 1: # Controles
                    estado_previo = ESTADO_PAUSA
                    estado_actual = ESTADO_CONTROLES
                elif opcion_menu_seleccionada == 2: # Salir al Menu
                    winsound.PlaySound("C:/Windows/Media/Alarm02.wav", winsound.SND_FILENAME)
                    estado_actual = ESTADO_MENU_PRINCIPAL
                    opcion_menu_seleccionada = 0

        # --- ESTADO: GAME OVER ---
        elif estado_actual == ESTADO_GAME_OVER:
            if menu_aceptar: # Revancha
                player1_y, oponente_y = SCREEN_HEIGHT // 2 - paddle_height // 2, SCREEN_HEIGHT // 2 - paddle_height // 2
                player1_puntos, oponente_puntos = 0, 0
                player1_partidas, oponente_partidas = 0, 0
                ball_x, ball_y, ball_speed_x, ball_speed_y = reset_pelota()
                ball_color, ball_trail = rl.WHITE, []
                player1_paddle_trail, oponente_paddle_trail = [], [] # NUEVO: Resetear estelas
                game_over, punto_anotado, partida_ganada_por_alguien = False, False, False
                estado_actual = ESTADO_JUGANDO
                tiempo_partida, multiplicador_velocidad, tiempo_acumulado = 0.0, 1.0, 0.0
                player1_stamina, oponente_stamina = MAX_STAMINA, MAX_STAMINA
                player1_stamina_cooldown, oponente_stamina_cooldown = 0.0, 0.0
            
            if menu_atras_btn: # Volver al menu
                player1_y, oponente_y = SCREEN_HEIGHT // 2 - paddle_height // 2, SCREEN_HEIGHT // 2 - paddle_height // 2
                player1_puntos, oponente_puntos = 0, 0
                player1_partidas, oponente_partidas = 0, 0
                ball_x, ball_y, ball_speed_x, ball_speed_y = reset_pelota()
                ball_color, ball_trail = rl.WHITE, []
                player1_paddle_trail, oponente_paddle_trail = [], [] # NUEVO: Resetear estelas
                game_over, punto_anotado, partida_ganada_por_alguien = False, False, False
                estado_actual = ESTADO_MENU_PRINCIPAL
                opcion_menu_seleccionada = 0
                tiempo_partida, multiplicador_velocidad, tiempo_acumulado = 0.0, 1.0, 0.0
                player1_stamina, oponente_stamina = MAX_STAMINA, MAX_STAMINA
                player1_stamina_cooldown, oponente_stamina_cooldown = 0.0, 0.0
        
        # --- ESTADO: JUGANDO ---
        elif estado_actual == ESTADO_JUGANDO:
            
            # --- Logica de Pausa por Punto ---
            if punto_anotado:
                if rl.get_key_pressed() != 0 or rl.get_gamepad_button_pressed() != 0:
                    punto_anotado = False
                    tiempo_partida = 0.0
                    multiplicador_velocidad = 1.0
                    tiempo_acumulado = 0.0
                    if partida_ganada_por_alguien:
                        player1_puntos, oponente_puntos = 0, 0
                        partida_ganada_por_alguien = False
                    ball_x, ball_y, ball_speed_x, ball_speed_y = reset_pelota()
                    ball_color, ball_trail = rl.WHITE, []
                    player1_paddle_trail, oponente_paddle_trail = [], [] # NUEVO: Resetear estelas
                else:
                    pass
            
            # --- Logica de Pausa (ESC o Start) ---
            elif juego_pausa_btn:
                winsound.PlaySound("C:/Windows/Media/Speech Sleep.wav", winsound.SND_FILENAME)
                estado_actual = ESTADO_PAUSA
                opcion_menu_seleccionada = 0
            
            # --- LOGICA DEL JUEGO (SI NO ESTA PAUSADO Y NO HAY PUNTO) ---
            elif not punto_anotado:
                
                delta_tiempo = rl.get_frame_time()
                
                # --- ========================================== ---
                # ---         LOGICA DE JUEGO BASICA           ---
                # --- ========================================== ---
                
                # --- 1. Tiempo y Velocidad de Pelota Basicos ---
                tiempo_partida += delta_tiempo
                tiempo_acumulado += delta_tiempo
                if tiempo_acumulado >= TIEMPO_AUMENTO_VELOCIDAD:
                    tiempo_acumulado = 0.0
                    ball_speed_x *= FACTOR_AUMENTO
                    ball_speed_y *= FACTOR_AUMENTO
                    multiplicador_velocidad *= FACTOR_AUMENTO
                
                # --- 2. Movimiento Basico de Pelota y Paredes ---
                ball_x += ball_speed_x
                ball_y += ball_speed_y
                
                if ball_y - ball_radius <= 0 or ball_y + ball_radius >= SCREEN_HEIGHT:
                    ball_speed_y *= -1
                    ball_speed_y *= random.uniform(1.0, 1.2)
                    winsound.PlaySound("C:/Windows/Media/Windows Menu Command.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

                # --- 3. Resetear flags de estado ---
                player1_is_moving = False
                oponente_is_moving = False
                player1_is_boosting = False
                oponente_is_boosting = False
                
                # --- 4. Inputs de Movimiento Basico J1 ---
                j1_move_input = 0.0
                if rl.is_key_down(rl.KEY_W): j1_move_input = -1.0
                if rl.is_key_down(rl.KEY_S): j1_move_input = 1.0
                
                # --- 5. Inputs de Movimiento Basico J2/IA ---
                j2_move_input = 0.0
                # Inputs de IA (se sobreescriben en seccion avanzada)
                if modo_juego == "ia":
                    oponente_is_moving = True
                    if oponente_y + paddle_height // 2 < ball_y - 10: j2_move_input = 1.0
                    elif oponente_y + paddle_height // 2 > ball_y + 10: j2_move_input = -1.0
                # Inputs de J2 (Teclado)
                elif modo_juego == "multi":
                    if rl.is_key_down(rl.KEY_UP): j2_move_input = -1.0
                    if rl.is_key_down(rl.KEY_DOWN): j2_move_input = 1.0


                # --- ========================================== ---
                # ---       LOGICA DE MECANICAS AVANZADAS      ---
                # --- ========================================== ---

                # --- 1. Inputs Avanzados (Mando, Boost, Dash) ---
                
                # --- J1 ---
                boost_j1_tapped = rl.is_key_pressed(rl.KEY_A) or \
                                  (gamepad_j1_conectado and (rl.is_gamepad_button_pressed(GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_RIGHT) or # B
                                                              rl.is_gamepad_button_pressed(GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_UP)))   # Y
                
                boost_j1_down = rl.is_key_down(rl.KEY_D) or \
                                (gamepad_j1_conectado and (rl.is_gamepad_button_down(GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_DOWN) or # A
                                                            rl.is_gamepad_button_down(GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_LEFT))) # X
                
                # Movimiento Analogico (Sobreescribe teclado)
                if gamepad_j1_conectado:
                    axis_y_j1 = rl.get_gamepad_axis_movement(GAMEPAD_J1, GAMEPAD_AXIS_Y)
                    if abs(axis_y_j1) > GAMEPAD_AXIS_DEADZONE:
                        j1_move_input = axis_y_j1
                    else: # Si joystick esta quieto, usa cruceta
                        if rl.is_gamepad_button_down(GAMEPAD_J1, rl.GAMEPAD_BUTTON_LEFT_FACE_UP): j1_move_input = -1.0
                        if rl.is_gamepad_button_down(GAMEPAD_J1, rl.GAMEPAD_BUTTON_LEFT_FACE_DOWN): j1_move_input = 1.0

                # --- J2 / IA ---
                boost_j2_tapped = False
                boost_j2_down = False

                if modo_juego == "multi":
                    boost_j2_tapped = rl.is_key_pressed(rl.KEY_RIGHT) or \
                                      (gamepad_j2_conectado and (rl.is_gamepad_button_pressed(GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_RIGHT) or # B
                                                                  rl.is_gamepad_button_pressed(GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_UP)))   # Y
                    
                    boost_j2_down = rl.is_key_down(rl.KEY_LEFT) or \
                                    (gamepad_j2_conectado and (rl.is_gamepad_button_down(GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_DOWN) or # A
                                                                rl.is_gamepad_button_down(GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_LEFT))) # X
                    
                    # Movimiento Analogico (Sobreescribe teclado)
                    if gamepad_j2_conectado:
                        axis_y_j2 = rl.get_gamepad_axis_movement(GAMEPAD_J2, GAMEPAD_AXIS_Y)
                        if abs(axis_y_j2) > GAMEPAD_AXIS_DEADZONE:
                            j2_move_input = axis_y_j2
                        else: # Si joystick esta quieto, usa cruceta
                            if rl.is_gamepad_button_down(GAMEPAD_J2, rl.GAMEPAD_BUTTON_LEFT_FACE_UP): j2_move_input = -1.0
                            if rl.is_gamepad_button_down(GAMEPAD_J2, rl.GAMEPAD_BUTTON_LEFT_FACE_DOWN): j2_move_input = 1.0
                
                elif modo_juego == "ia":
                    # --- Logica de IA Extrema ---
                    if dificultad_ia == "extremo":
                        oponente_is_moving = True
                        target_y = ball_y - (paddle_height * 0.1) if ball_y > SCREEN_HEIGHT / 2 else ball_y - (paddle_height * 0.9)
                        
                        distancia_y_ia = abs((oponente_y + paddle_height / 2) - ball_y)
                        
                        # IA decide usar Super Boost (Dash)
                        if distancia_y_ia > 250 and oponente_stamina >= SUPER_BOOST_COST and oponente_stamina_cooldown <= 0:
                            boost_j2_tapped = True
                        # IA decide usar Boost Normal
                        elif distancia_y_ia > 70 and oponente_stamina > 0.2 and oponente_stamina_cooldown <= 0:
                            boost_j2_down = True

                        # Movimiento IA (mas rapido que el input normal)
                        if oponente_y > target_y: oponente_y -= velocidad_ia
                        elif oponente_y < target_y: oponente_y += velocidad_ia
                        j2_move_input = 0 # El movimiento de la IA se maneja arriba, no con input
                    
                    elif dificultad_ia == "dificil":
                        if oponente_y + paddle_height // 2 < ball_y: j2_move_input = 1.0
                        elif oponente_y + paddle_height // 2 > ball_y: j2_move_input = -1.0


                # --- 2. Logica de Estamina J1 (Boost/Dash) ---
                paddle_speed_j1 = paddle_speed_jugador_base
                target_color_j1 = WHITE_TUPLE 

                if player1_super_boost_flash_timer > 0:
                    player1_super_boost_flash_timer -= delta_tiempo
                    target_color_j1 = FLASH_COLOR_TUPLE
                
                if player1_dash_effect_window_timer > 0:
                    player1_dash_effect_window_timer -= delta_tiempo

                if player1_super_boost_timer > 0:
                    player1_super_boost_timer -= delta_tiempo
                    paddle_speed_j1 *= SUPER_BOOST_SPEED_FACTOR
                    player1_is_boosting = True
                    if player1_super_boost_flash_timer <= 0:
                        target_color_j1 = J1_BOOST_COLOR_TUPLE
                
                elif player1_dash_effect_window_timer > 0:
                    player1_is_boosting = True
                    target_color_j1 = J1_BOOST_COLOR_TUPLE
                
                elif player1_stamina_cooldown > 0:
                    player1_stamina_cooldown -= delta_tiempo
                    player1_stamina += delta_tiempo * (MAX_STAMINA / player1_current_penalty_time)
                    if player1_stamina >= MAX_STAMINA:
                        player1_stamina = MAX_STAMINA
                        player1_stamina_cooldown = 0
                
                elif player1_stamina_regen_delay > 0:
                    player1_stamina_regen_delay -= delta_tiempo
                
                elif boost_j1_tapped and player1_stamina >= SUPER_BOOST_COST:
                    player1_stamina -= SUPER_BOOST_COST
                    player1_super_boost_timer = SUPER_BOOST_DURATION
                    player1_super_boost_flash_timer = SUPER_BOOST_FLASH_DURATION
                    player1_dash_effect_window_timer = SUPER_BOOST_EFFECT_WINDOW
                    
                    if player1_stamina < SUPER_BOOST_COST: 
                        player1_stamina = 0
                        player1_stamina_cooldown = STAMINA_PENALTY_TIME_SUPER_2
                        player1_current_penalty_time = STAMINA_PENALTY_TIME_SUPER_2
                    else:
                        player1_stamina_regen_delay = SUPER_BOOST_TAP_DELAY
                        player1_current_regen_time = STAMINA_REGEN_TIME_SUPER_1

                elif boost_j1_down:
                    player1_is_boosting = True
                    paddle_speed_j1 *= BOOST_FACTOR
                    target_color_j1 = J1_BOOST_COLOR_TUPLE
                    player1_stamina -= delta_tiempo
                    
                    if player1_stamina <= 0:
                        player1_stamina = 0
                        player1_stamina_cooldown = STAMINA_PENALTY_TIME
                        player1_current_penalty_time = STAMINA_PENALTY_TIME
                    
                    player1_current_regen_time = STAMINA_REGEN_TIME

                else:
                    if player1_stamina < MAX_STAMINA:
                        player1_stamina += delta_tiempo * (MAX_STAMINA / player1_current_regen_time)
                        if player1_stamina >= MAX_STAMINA:
                            player1_stamina = MAX_STAMINA
                            player1_current_regen_time = STAMINA_REGEN_TIME
                
                
                # --- 3. Logica de Estamina J2 / IA Extrema ---
                paddle_speed_op = paddle_speed_jugador_base
                target_color_op = WHITE_TUPLE
                
                # La IA Extrema y J2 usan estamina. La IA Facil/Normal no.
                if modo_juego == "multi" or (modo_juego == "ia" and dificultad_ia == "extremo"):
                    if oponente_super_boost_flash_timer > 0:
                        oponente_super_boost_flash_timer -= delta_tiempo
                        target_color_op = FLASH_COLOR_TUPLE
                    
                    if oponente_dash_effect_window_timer > 0:
                        oponente_dash_effect_window_timer -= delta_tiempo

                    if oponente_super_boost_timer > 0:
                        oponente_super_boost_timer -= delta_tiempo
                        paddle_speed_op *= SUPER_BOOST_SPEED_FACTOR
                        oponente_is_boosting = True
                        if oponente_super_boost_flash_timer <= 0:
                            target_color_op = J2_BOOST_COLOR_TUPLE
                    
                    elif oponente_dash_effect_window_timer > 0:
                        oponente_is_boosting = True
                        target_color_op = J2_BOOST_COLOR_TUPLE

                    elif oponente_stamina_cooldown > 0:
                        oponente_stamina_cooldown -= delta_tiempo
                        oponente_stamina += delta_tiempo * (MAX_STAMINA / oponente_current_penalty_time)
                        if oponente_stamina >= MAX_STAMINA:
                            oponente_stamina = MAX_STAMINA
                            oponente_stamina_cooldown = 0
                    
                    elif oponente_stamina_regen_delay > 0:
                        oponente_stamina_regen_delay -= delta_tiempo
                    
                    elif boost_j2_tapped and oponente_stamina >= SUPER_BOOST_COST:
                        oponente_stamina -= SUPER_BOOST_COST
                        oponente_super_boost_timer = SUPER_BOOST_DURATION
                        oponente_super_boost_flash_timer = SUPER_BOOST_FLASH_DURATION
                        oponente_dash_effect_window_timer = SUPER_BOOST_EFFECT_WINDOW
                        
                        if oponente_stamina < SUPER_BOOST_COST:
                            oponente_stamina = 0
                            oponente_stamina_cooldown = STAMINA_PENALTY_TIME_SUPER_2
                            oponente_current_penalty_time = STAMINA_PENALTY_TIME_SUPER_2
                        else:
                            oponente_stamina_regen_delay = SUPER_BOOST_TAP_DELAY
                            oponente_current_regen_time = STAMINA_REGEN_TIME_SUPER_1

                    elif boost_j2_down:
                        oponente_is_boosting = True
                        paddle_speed_op *= BOOST_FACTOR
                        target_color_op = J2_BOOST_COLOR_TUPLE
                        oponente_stamina -= delta_tiempo
                        
                        if oponente_stamina <= 0:
                            oponente_stamina = 0
                            oponente_stamina_cooldown = STAMINA_PENALTY_TIME
                            oponente_current_penalty_time = STAMINA_PENALTY_TIME
                        
                        oponente_current_regen_time = STAMINA_REGEN_TIME

                    else:
                        if oponente_stamina < MAX_STAMINA:
                            oponente_stamina += delta_tiempo * (MAX_STAMINA / oponente_current_regen_time)
                            if oponente_stamina >= MAX_STAMINA:
                                oponente_stamina = MAX_STAMINA
                                oponente_current_regen_time = STAMINA_REGEN_TIME
                
                # --- 4. Aplicar Movimiento Avanzado (con velocidad de boost) ---
                
                # J1
                # (La velocidad de IA Extrema ya se aplico, no usa input)
                if dificultad_ia != "extremo":
                    player1_y += paddle_speed_j1 * j1_move_input
                    oponente_y += paddle_speed_op * j2_move_input
                else:
                    player1_y += paddle_speed_j1 * j1_move_input
                
                if j1_move_input != 0.0: player1_is_moving = True
                if j2_move_input != 0.0: oponente_is_moving = True

                # Limites
                if player1_y < 0: player1_y = 0
                if player1_y > SCREEN_HEIGHT - paddle_height: player1_y = SCREEN_HEIGHT - paddle_height
                if oponente_y < 0: oponente_y = 0
                if oponente_y > SCREEN_HEIGHT - paddle_height: oponente_y = SCREEN_HEIGHT - paddle_height


                # --- 5. Logica de Colision Avanzada (Boost Hit, Coyote) ---
                
                # Buffers de Coyote Time
                buffer_j1 = COYOTE_TIME_BUFFER if player1_is_moving else 0
                buffer_op = COYOTE_TIME_BUFFER if oponente_is_moving else 0
                
                # --- J1 Colision ---
                if (ball_x - ball_radius <= paddle_width and 
                    player1_y - buffer_j1 <= ball_y <= player1_y + paddle_height + buffer_j1 and 
                    ball_speed_x < 0):
                    
                    if player1_is_boosting: # Boost o Dash
                        ball_color = paddle_color_j1
                        ball_speed_y = random.uniform(-BOOST_HIT_Y_VELOCITY_RANGE, BOOST_HIT_Y_VELOCITY_RANGE)
                        ball_speed_x *= -1.1
                        player1_stamina = max(0, player1_stamina - BOOST_HIT_COST)
                    else: # Golpe Normal
                        ball_color = rl.WHITE
                        ball_speed_x *= -1
                        hit_position = (ball_y - player1_y) / paddle_height
                        ball_speed_y = 8 * (hit_position - 0.5)
                        if rl.is_key_down(rl.KEY_W): ball_speed_y -= 4
                        if rl.is_key_down(rl.KEY_S): ball_speed_y += 4
                    
                    winsound.PlaySound("C:/Windows/Media/Windows Information Bar.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

                # --- J2/Oponente Colision ---
                elif (ball_x + ball_radius >= SCREEN_WIDTH - paddle_width and 
                    oponente_y - buffer_op <= ball_y <= oponente_y + paddle_height + buffer_op and 
                    ball_speed_x > 0):
                    
                    if oponente_is_boosting: # Boost o Dash
                        ball_color = paddle_color_op
                        ball_speed_y = random.uniform(-BOOST_HIT_Y_VELOCITY_RANGE, BOOST_HIT_Y_VELOCITY_RANGE)
                        ball_speed_x *= -1.1
                        oponente_stamina = max(0, oponente_stamina - BOOST_HIT_COST)
                    else: # Golpe Normal
                        ball_color = rl.WHITE
                        ball_speed_x *= -1
                        hit_position = (ball_y - oponente_y) / paddle_height
                        ball_speed_y = 8 * (hit_position - 0.5)
                        if modo_juego == "multi": # Solo J2 humano puede dirigir
                            if rl.is_key_down(rl.KEY_UP): ball_speed_y -= 4
                            if rl.is_key_down(rl.KEY_DOWN): ball_speed_y += 4
                    
                    winsound.PlaySound("C:/Windows/Media/Windows Information Bar.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)


                # --- 6. Logica de Puntuacion ---
                
                # Oponente anota
                elif (ball_x + ball_radius < 0): 
                    oponente_puntos += 1
                    punto_anotado = True
                    ultimo_anotador = "oponente"
                    winsound.PlaySound("C:/Windows/Media/Windows Critical Stop.wav", winsound.SND_FILENAME)
                    
                    player1_stamina, oponente_stamina = MAX_STAMINA, MAX_STAMINA
                    player1_stamina_cooldown, oponente_stamina_cooldown = 0.0, 0.0
                    
                    if oponente_puntos >= PUNTOS_POR_PARTIDA:
                        oponente_partidas += 1
                        partida_ganada_por_alguien = True
                        
                        if oponente_partidas >= PARTIDAS_PARA_GANAR:
                            game_over = True
                            winner = "IA" if modo_juego == "ia" else "JUGADOR 2"
                            nombre_oponente_str = "IA" if modo_juego == "ia" else "JUGADOR 2"
                            modo_str = f"J1 vs {nombre_oponente_str}"
                            if dificultad_ia: modo_str += f" ({dificultad_ia})"
                            guardar_historial(winner, player1_partidas, oponente_partidas, modo_str)
                
                # J1 anota
                elif (ball_x - ball_radius > SCREEN_WIDTH): 
                    player1_puntos += 1
                    punto_anotado = True
                    ultimo_anotador = "j1"
                    winsound.PlaySound("C:/Windows/Media/Windows Critical Stop.wav", winsound.SND_FILENAME)

                    player1_stamina, oponente_stamina = MAX_STAMINA, MAX_STAMINA
                    player1_stamina_cooldown, oponente_stamina_cooldown = 0.0, 0.0
                    
                    if player1_puntos >= PUNTOS_POR_PARTIDA:
                        player1_partidas += 1
                        partida_ganada_por_alguien = True
                        
                        if player1_partidas >= PARTIDAS_PARA_GANAR:
                            game_over = True
                            winner = "JUGADOR 1"
                            nombre_oponente = "IA" if modo_juego == "ia" else "JUGADOR 2"
                            modo_str = f"J1 vs {nombre_oponente}"
                            if dificultad_ia: modo_str += f" ({dificultad_ia})"
                            guardar_historial(winner, player1_partidas, oponente_partidas, modo_str)
                
                if game_over:
                    estado_actual = ESTADO_GAME_OVER
                    opcion_menu_seleccionada = 0
                
                # --- 7. Logica de Color Suave (Lerp) ---
                
                # J1
                lerp_factor = COLOR_LERP_SPEED * delta_tiempo
                p1_color_r += (target_color_j1[0] - p1_color_r) * lerp_factor
                p1_color_g += (target_color_j1[1] - p1_color_g) * lerp_factor
                p1_color_b += (target_color_j1[2] - p1_color_b) * lerp_factor
                paddle_color_j1 = rl.Color(int(p1_color_r), int(p1_color_g), int(p1_color_b), 255)
                
                # J2 / IA Extrema
                op_color_r += (target_color_op[0] - op_color_r) * lerp_factor
                op_color_g += (target_color_op[1] - op_color_g) * lerp_factor
                op_color_b += (target_color_op[2] - op_color_b) * lerp_factor
                paddle_color_op = rl.Color(int(op_color_r), int(op_color_g), int(op_color_b), 255)
                
                # --- 8. Logica de Estela (Pelota) ---
                ball_trail.append((ball_x, ball_y, ball_color))
                if len(ball_trail) > BALL_TRAIL_LENGTH:
                    ball_trail.pop(0)

                # --- 9. NUEVO: Logica de Estela (Paddle) ---
                # Añadir a la estela de J1
                if player1_is_boosting:
                    player1_paddle_trail.append((player1_y, paddle_color_j1))
                # Limpiar si no esta boosteando o si es muy larga
                if (not player1_is_boosting and player1_paddle_trail) or len(player1_paddle_trail) > PADDLE_TRAIL_LENGTH:
                    player1_paddle_trail.pop(0)

                # Añadir a la estela de J2/IA
                if oponente_is_boosting:
                    oponente_paddle_trail.append((oponente_y, paddle_color_op))
                # Limpiar si no esta boosteando o si es muy larga
                if (not oponente_is_boosting and oponente_paddle_trail) or len(oponente_paddle_trail) > PADDLE_TRAIL_LENGTH:
                    oponente_paddle_trail.pop(0)
        
        
        # -----------------------------------------------------
        # --- 2. DIBUJADO (GRAFICOS) ---
        # -----------------------------------------------------
        rl.begin_drawing()
        rl.clear_background(COLOR_FONDO_AZUL)

        if estado_actual == ESTADO_MENU_PRINCIPAL:
            opciones_menu = ["Jugar", "Ver Historial", "Salir"]
            for i, opcion in enumerate(opciones_menu):
                color = rl.YELLOW if i == opcion_menu_seleccionada else rl.WHITE
                rl.draw_text(opcion, SCREEN_WIDTH // 2 - (rl.measure_text(opcion, 30) // 2), SCREEN_HEIGHT // 2 + i * 40, 30, color)
            
            rl.draw_text("Usa Flechas/Cruceta/Joystick y Enter/(A)", 10, SCREEN_HEIGHT - 30, 15, rl.GRAY)
            rl.draw_text(VERSION_JUEGO, SCREEN_WIDTH - 60, SCREEN_HEIGHT - 30, 15, rl.YELLOW)
            
            if gamepad_j1_conectado: rl.draw_text("Mando 1 Detectado", SCREEN_WIDTH - 180, 10, 15, rl.GREEN)
            if gamepad_j2_conectado: rl.draw_text("Mando 2 Detectado", SCREEN_WIDTH - 180, 30, 15, rl.RED)

        # --- DIBUJAR: ESTADO SELECCION MODO ---
        elif estado_actual == ESTADO_SELECCION_MODO:
            opciones_menu = ["Jugador vs IA", "Jugador 1 vs Jugador 2", "Volver"]
            rl.draw_text("Modo de Juego", SCREEN_WIDTH // 2 - (rl.measure_text("Modo de Juego", 40) // 2), SCREEN_HEIGHT // 2 - 100, 40, rl.WHITE)
            for i, opcion in enumerate(opciones_menu):
                color = rl.YELLOW if i == opcion_menu_seleccionada else rl.WHITE
                rl.draw_text(opcion, SCREEN_WIDTH // 2 - (rl.measure_text(opcion, 30) // 2), SCREEN_HEIGHT // 2 + i * 40, 30, color)
            
            rl.draw_text("ESC/(B) para volver", 10, SCREEN_HEIGHT - 30, 15, rl.GRAY)
            rl.draw_text(VERSION_JUEGO, SCREEN_WIDTH - 60, SCREEN_HEIGHT - 30, 15, rl.YELLOW)
        
        # --- DIBUJAR: ESTADO SELECCION DIFICULTAD ---
        elif estado_actual == ESTADO_SELECCION_DIFICULTAD:
            opciones_menu = ["Facil", "Normal", "Dificil", "Extremo (Jaque Mate)", "Volver"]
            rl.draw_text("Dificultad de la IA", SCREEN_WIDTH // 2 - (rl.measure_text("Dificultad de la IA", 40) // 2), SCREEN_HEIGHT // 2 - 120, 40, rl.WHITE)
            for i, opcion in enumerate(opciones_menu):
                color = rl.YELLOW if i == opcion_menu_seleccionada else rl.WHITE
                rl.draw_text(opcion, SCREEN_WIDTH // 2 - (rl.measure_text(opcion, 30) // 2), SCREEN_HEIGHT // 2 - 20 + i * 40, 30, color)
            
            rl.draw_text("ESC/(B) para volver", 10, SCREEN_HEIGHT - 30, 15, rl.GRAY)
            rl.draw_text(VERSION_JUEGO, SCREEN_WIDTH - 60, SCREEN_HEIGHT - 30, 15, rl.YELLOW)
        
        # --- DIBUJAR: ESTADO HISTORIAL ---
        elif estado_actual == ESTADO_HISTORIAL:
            rl.draw_text("Historial de Partidas", 20, 20, 30, rl.WHITE)
            rl.draw_text("Presiona ESC/(B) o Enter/(A) para volver", 20, SCREEN_HEIGHT - 30, 15, rl.GRAY)
            y_pos = 70
            for linea in historial_lineas[:35]:
                rl.draw_text(linea, 20, y_pos, 20, rl.WHITE)
                y_pos += 25
        
        # --- DIBUJAR ESTADO CONTROLES (ACTUALIZADO) ---
        elif estado_actual == ESTADO_CONTROLES:
            rl.draw_text("Controles", SCREEN_WIDTH // 2 - (rl.measure_text("Controles", 40) // 2), 100, 40, rl.WHITE)
            rl.draw_text("Presiona ESC/(B) o Enter/(A) para volver", SCREEN_WIDTH // 2 - (rl.measure_text("Presiona ESC/(B) o Enter/(A) para volver", 20) // 2), SCREEN_HEIGHT - 50, 20, rl.GRAY)

            y_base_j1 = 200
            rl.draw_text("Jugador 1 (Izquierda)", 200, y_base_j1, 30, rl.WHITE)
            if gamepad_j1_conectado:
                rl.draw_text("- Mover: Joystick Izquierdo o Cruceta", 200, y_base_j1 + 50, 20, rl.WHITE)
                rl.draw_text("- Boost Normal (Mantener): A / X", 200, y_base_j1 + 80, 20, rl.WHITE)
                rl.draw_text("- Super Boost (Tocar): B / Y", 200, y_base_j1 + 110, 20, rl.WHITE)
            else:
                rl.draw_text("- Mover: W / S", 200, y_base_j1 + 50, 20, rl.WHITE)
                rl.draw_text("- Boost Normal (Mantener): D", 200, y_base_j1 + 80, 20, rl.WHITE)
                rl.draw_text("- Super Boost (Tocar): A", 200, y_base_j1 + 110, 20, rl.WHITE)
            
            y_base_j2 = 200
            rl.draw_text("Jugador 2 (Derecha)", SCREEN_WIDTH - 550, y_base_j2, 30, rl.WHITE)
            if modo_juego == "ia":
                 rl.draw_text("- Oponente: IA", SCREEN_WIDTH - 550, y_base_j2 + 50, 20, rl.GRAY)
            elif gamepad_j2_conectado:
                rl.draw_text("- Mover: Joystick Izquierdo o Cruceta", SCREEN_WIDTH - 550, y_base_j2 + 50, 20, rl.WHITE)
                rl.draw_text("- Boost Normal (Mantener): A / X", SCREEN_WIDTH - 550, y_base_j2 + 80, 20, rl.WHITE)
                rl.draw_text("- Super Boost (Tocar): B / Y", SCREEN_WIDTH - 550, y_base_j2 + 110, 20, rl.WHITE)
            else:
                rl.draw_text("- Mover: Flecha Arriba / Flecha Abajo", SCREEN_WIDTH - 550, y_base_j2 + 50, 20, rl.WHITE)
                rl.draw_text("- Boost Normal (Mantener): Flecha Izquierda", SCREEN_WIDTH - 550, y_base_j2 + 80, 20, rl.WHITE)
                rl.draw_text("- Super Boost (Tocar): Flecha Derecha", SCREEN_WIDTH - 550, y_base_j2 + 110, 20, rl.WHITE)
            
            rl.draw_text("General", 200, y_base_j1 + 200, 30, rl.WHITE)
            rl.draw_text("- Pausa: ESC o Start", 200, y_base_j1 + 250, 20, rl.WHITE)
            rl.draw_text("- Menus: Cruceta/Joystick, (A) Aceptar, (B) Atras", 200, y_base_j1 + 280, 20, rl.WHITE)

        # --- DIBUJAR: ESTADO JUGANDO / PAUSA / GAME OVER ---
        elif estado_actual in [ESTADO_JUGANDO, ESTADO_PAUSA, ESTADO_GAME_OVER]:
            
            # --- NUEVO: Dibuja Estelas de Paddles (primero) ---
            for i, (y, color) in enumerate(player1_paddle_trail):
                alpha = (i / PADDLE_TRAIL_LENGTH) * 0.4 # 40% de opacidad max
                trail_color = rl.Color(color.r, color.g, color.b, int(alpha * 255))
                rl.draw_rectangle(0, int(y), paddle_width, paddle_height, trail_color)

            for i, (y, color) in enumerate(oponente_paddle_trail):
                alpha = (i / PADDLE_TRAIL_LENGTH) * 0.4
                trail_color = rl.Color(color.r, color.g, color.b, int(alpha * 255))
                rl.draw_rectangle(SCREEN_WIDTH - paddle_width, int(y), paddle_width, paddle_height, trail_color)

            # Dibuja paletas (encima de la estela)
            rl.draw_rectangle(0, player1_y, paddle_width, paddle_height, paddle_color_j1)
            rl.draw_rectangle(SCREEN_WIDTH - paddle_width, oponente_y, paddle_width, paddle_height, paddle_color_op)
            
            # --- Dibuja la Estela (Pelota) ---
            for i, (x, y, color) in enumerate(ball_trail):
                alpha = (i / BALL_TRAIL_LENGTH) * 0.5
                radius_scale = i / BALL_TRAIL_LENGTH
                trail_color = rl.Color(color.r, color.g, color.b, int(alpha * 255))
                rl.draw_circle(int(x), int(y), ball_radius * radius_scale, trail_color)

            # Dibuja la pelota
            rl.draw_circle(ball_x, ball_y, ball_radius, ball_color)
            
            for i in range(0, SCREEN_HEIGHT, 20):
                rl.draw_line(SCREEN_WIDTH // 2, i, SCREEN_WIDTH // 2, i + 10, rl.GRAY)

            # Marcadores
            rl.draw_text(f"{player1_puntos}", SCREEN_WIDTH // 4, 20, 50, rl.WHITE)
            rl.draw_text(f"{oponente_puntos}", 3 * SCREEN_WIDTH // 4 - 30, 20, 50, rl.WHITE)
            rl.draw_text(f"Partidas: {player1_partidas}", 20, 10, 20, rl.GRAY)
            rl.draw_text(f"Partidas: {oponente_partidas}", SCREEN_WIDTH - 200, 10, 20, rl.GRAY)

            # --- Temporizador y Multiplicador ---
            minutos = int(tiempo_partida) // 60
            segundos = int(tiempo_partida) % 60
            texto_tiempo = f"Tiempo: {minutos}:{segundos:02d}"
            texto_velocidad = f"x{multiplicador_velocidad:.1f}"
            rl.draw_text(texto_tiempo, SCREEN_WIDTH // 2 - (rl.measure_text(texto_tiempo, 20) // 2), 10, 20, rl.WHITE)
            rl.draw_text(texto_velocidad, SCREEN_WIDTH // 2 - (rl.measure_text(texto_velocidad, 20) // 2), 35, 20, rl.YELLOW)

            # Controles
            rl.draw_text("J1: W/S", 10, SCREEN_HEIGHT - 30, 15, rl.GRAY)
            rl.draw_text("ESC/Start: Pausa", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30, 15, rl.GRAY)
            
            # --- Barras de Estamina (J1) ---
            rl.draw_text("Boost [D]", 10, SCREEN_HEIGHT - 75, 15, rl.GRAY)
            rl.draw_text("Dash [A]", 10, SCREEN_HEIGHT - 90, 15, rl.GRAY)
            rl.draw_rectangle(10, SCREEN_HEIGHT - 60, STAMINA_BAR_WIDTH, 10, rl.DARKGRAY)
            stamina_width_j1 = int((player1_stamina / MAX_STAMINA) * STAMINA_BAR_WIDTH)
            color_stamina_j1 = rl.SKYBLUE if player1_stamina_cooldown > 0 else rl.GREEN
            rl.draw_rectangle(10, SCREEN_HEIGHT - 60, stamina_width_j1, 10, color_stamina_j1)
            
            # --- Barras de Estamina (J2 / Multi) ---
            if modo_juego == "multi":
                rl.draw_text("J2: Flechas", 100, SCREEN_HEIGHT - 30, 15, rl.GRAY)
                rl.draw_text("Boost [<-]", SCREEN_WIDTH - (STAMINA_BAR_WIDTH + 10), SCREEN_HEIGHT - 75, 15, rl.GRAY)
                rl.draw_text("Dash [->]", SCREEN_WIDTH - (STAMINA_BAR_WIDTH + 10), SCREEN_HEIGHT - 90, 15, rl.GRAY)
            
            # La IA Extrema tambien tiene barra
            if modo_juego == "multi" or (modo_juego == "ia" and dificultad_ia == "extremo"):
                rl.draw_rectangle(SCREEN_WIDTH - (STAMINA_BAR_WIDTH + 10), SCREEN_HEIGHT - 60, STAMINA_BAR_WIDTH, 10, rl.DARKGRAY)
                stamina_width_op = int((oponente_stamina / MAX_STAMINA) * STAMINA_BAR_WIDTH)
                color_stamina_op = rl.ORANGE if oponente_stamina_cooldown > 0 else rl.RED
                rl.draw_rectangle(SCREEN_WIDTH - (STAMINA_BAR_WIDTH + 10), SCREEN_HEIGHT - 60, stamina_width_op, 10, color_stamina_op)

            
            # --- DIBUJAR: Pausa por Punto (Encima del juego) ---
            if estado_actual == ESTADO_JUGANDO and punto_anotado:
                rl.draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, rl.Color(0, 0, 0, 179))
                texto_punto = ""
                if ultimo_anotador == "j1":
                    texto_punto, color_punto = "¡Punto para J1!", rl.GREEN
                elif ultimo_anotador == "oponente":
                    nombre_oponente = "IA" if modo_juego == "ia" else "J2"
                    texto_punto, color_punto = f"Punto para {nombre_oponente}", rl.RED
                
                rl.draw_text(texto_punto, SCREEN_WIDTH // 2 - (rl.measure_text(texto_punto, 30) // 2), SCREEN_HEIGHT // 2 - 40, 30, color_punto)
                texto_continuar = "Presiona CUALQUIER TECLA/BOTON para continuar"
                rl.draw_text(texto_continuar, SCREEN_WIDTH // 2 - (rl.measure_text(texto_continuar, 20) // 2), SCREEN_HEIGHT // 2 + 20, 20, rl.WHITE)

            # --- DIBUJAR: MENU PAUSA (Encima del juego) ---
            elif estado_actual == ESTADO_PAUSA:
                opciones_menu = ["Continuar", "Controles", "Salir al Menu Principal"]
                rl.draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, rl.Color(0, 0, 0, 179))
                rl.draw_text("PAUSA", SCREEN_WIDTH // 2 - (rl.measure_text("PAUSA", 40) // 2), SCREEN_HEIGHT // 2 - 100, 40, rl.WHITE)
                for i, opcion in enumerate(opciones_menu):
                    color = rl.YELLOW if i == opcion_menu_seleccionada else rl.WHITE
                    rl.draw_text(opcion, SCREEN_WIDTH // 2 - (rl.measure_text(opcion, 30) // 2), SCREEN_HEIGHT // 2 - 20 + i * 40, 30, color)
            
            # --- DIBUJAR: PANTALLA GAME OVER (Encima del juego) ---
            elif estado_actual == ESTADO_GAME_OVER:
                rl.draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, rl.Color(0, 0, 0, 204))
                rl.draw_text(f"¡{winner} GANA EL JUEGO!", SCREEN_WIDTH // 2 - (rl.measure_text(f"¡{winner} GANA EL JUEGO!", 40) // 2), SCREEN_HEIGHT // 2 - 100, 40, rl.GOLD)
                rl.draw_text(f"Marcador Final (Partidas): {player1_partidas} - {oponente_partidas}", SCREEN_WIDTH // 2 - (rl.measure_text(f"Marcador Final (Partidas): {player1_partidas} - {oponente_partidas}", 20) // 2), SCREEN_HEIGHT // 2 - 50, 20, rl.WHITE)
                rl.draw_text("Presiona ENTER/(A) para la Revancha", SCREEN_WIDTH // 2 - (rl.measure_text("Presiona ENTER/(A) para la Revancha", 20) // 2), SCREEN_HEIGHT // 2 + 20, 20, rl.YELLOW)
                rl.draw_text("Presiona ESC/(B) para Volver al Menu", SCREEN_WIDTH // 2 - (rl.measure_text("Presiona ESC/(B) para Volver al Menu", 20) // 2), SCREEN_HEIGHT // 2 + 50, 20, rl.WHITE)
        
        rl.end_drawing()
        # --- Fin del Dibujado ---
    
    # --- Fin del Bucle Principal de la Aplicacion ---
    
    # Cierra la ventana de raylib y libera los recursos
    rl.close_window()
