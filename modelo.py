"""
fecha: 2025/10/31
Autor: Alejandro Uzcategui, Gabriel Guedez, Hector Vargas
-
descripcion: maneja toda la logica del programa, incluyendo menus
(ahora en Raylib) y el juego en si.
"""
#========================
#imports
try:
    import raylibpy as rl
except ImportError:
    print("Error: No se pudo importar la biblioteca 'raylibpy'.")
    print("Por favor, instálela usando: pip install raylib-py")
    exit()

import random
import datetime
import os # Necesario para leer el historial

#========================
# Constantes Globales
#========================
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
GAME_TITLE = "Juego de Ping Pong"

# Constantes del Juego
PUNTOS_POR_PARTIDA = 12
PARTIDAS_PARA_GANAR = 2
TIEMPO_AUMENTO_VELOCIDAD = 2.5 
FACTOR_AUMENTO = 1.075
COYOTE_TIME_BUFFER = 5 # 5 pixeles de gracia

# Constantes de Habilidad Re-balanceadas
MAX_STAMINA = 1.5 # 1.5 segundos
BOOST_COOLDOWN_TOTAL = 2.8 # 2.8 segundos
BOOST_FACTOR = 2.0 # x2.0
STAMINA_BAR_WIDTH = 80 # Ancho de la barra de estamina

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
GAMEPAD_AXIS_DEADZONE = 0.5 # Deadzone para menus

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
    if not os.path.exists("historial.txt"):
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
    rl.set_target_fps(90) 
    
    # --- Variables de Estado ---
    estado_actual = ESTADO_MENU_PRINCIPAL
    estado_previo = ESTADO_MENU_PRINCIPAL 
    
    opcion_menu_seleccionada = 0
    
    # Variables de configuracion del juego
    modo_juego = "ia"
    dificultad_ia = "normal"
    
    # Variables de estado del historial
    historial_lineas = []
    
    # --- Variables del Juego (se inicializan aqui) ---
    paddle_height = 100
    paddle_width = 15
    paddle_speed_jugador_base = 7 # Velocidad base
    paddle_speed_j1 = paddle_speed_jugador_base
    paddle_speed_op = paddle_speed_jugador_base
    paddle_color_j1 = rl.WHITE
    paddle_color_op = rl.WHITE
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
    
    # --- Variables de Tiempo y Velocidad ---
    tiempo_acumulado = 0.0
    tiempo_partida = 0.0
    multiplicador_velocidad = 1.0

    # --- Variables de Estamina ---
    player1_stamina = MAX_STAMINA
    player1_stamina_cooldown = 0.0
    player1_is_boosting = False
    
    oponente_stamina = MAX_STAMINA
    oponente_stamina_cooldown = 0.0
    oponente_is_boosting = False

    # --- Variables para pausa post-punto ---
    punto_anotado = False
    ultimo_anotador = "" # "j1" o "oponente"
    partida_ganada_por_alguien = False # Para resetear puntos
    
    # Variables de Movimiento (para Coyote Time)
    player1_is_moving = False
    oponente_is_moving = False

    # Deshabilitamos la tecla ESC para cerrar la ventana por defecto
    rl.set_exit_key(0)
    
    # --- Variables de Deteccion de Mando ---
    gamepad_j1_conectado = False
    gamepad_j2_conectado = False
    
    # Estado neutral del Eje (para menus)
    axis_j1_neutral = True
    axis_j2_neutral = True

    # --- BUCLE PRINCIPAL DE LA APLICACION ---
    while not rl.window_should_close():
        
        # --- Deteccion de Mandos (constante) ---
        gamepad_j1_conectado = rl.is_gamepad_available(GAMEPAD_J1)
        gamepad_j2_conectado = rl.is_gamepad_available(GAMEPAD_J2)
        
        # --- Variables de Input (Mando) ---
        
        # D-Pad (Cruceta)
        dpad_j1_up = rl.is_gamepad_button_pressed(GAMEPAD_J1, rl.GAMEPAD_BUTTON_LEFT_FACE_UP)
        dpad_j1_down = rl.is_gamepad_button_pressed(GAMEPAD_J1, rl.GAMEPAD_BUTTON_LEFT_FACE_DOWN)
        dpad_j2_up = rl.is_gamepad_button_pressed(GAMEPAD_J2, rl.GAMEPAD_BUTTON_LEFT_FACE_UP)
        dpad_j2_down = rl.is_gamepad_button_pressed(GAMEPAD_J2, rl.GAMEPAD_BUTTON_LEFT_FACE_DOWN)
        
        # Logica de Eje (Joystick) para menus
        axis_y_j1 = rl.get_gamepad_axis_movement(GAMEPAD_J1, GAMEPAD_AXIS_Y) if gamepad_j1_conectado else 0
        axis_y_j2 = rl.get_gamepad_axis_movement(GAMEPAD_J2, GAMEPAD_AXIS_Y) if gamepad_j2_conectado else 0
        
        axis_j1_up = (gamepad_j1_conectado and axis_y_j1 < -GAMEPAD_AXIS_DEADZONE and axis_j1_neutral)
        axis_j1_down = (gamepad_j1_conectado and axis_y_j1 > GAMEPAD_AXIS_DEADZONE and axis_j1_neutral)
        axis_j2_up = (gamepad_j2_conectado and axis_y_j2 < -GAMEPAD_AXIS_DEADZONE and axis_j2_neutral)
        axis_j2_down = (gamepad_j2_conectado and axis_y_j2 > GAMEPAD_AXIS_DEADZONE and axis_j2_neutral)

        # Actualizar estado neutral del Eje
        if axis_j1_up or axis_j1_down: axis_j1_neutral = False
        if axis_j2_up or axis_j2_down: axis_j2_neutral = False
        if gamepad_j1_conectado and -0.2 < axis_y_j1 < 0.2: axis_j1_neutral = True
        if gamepad_j2_conectado and -0.2 < axis_y_j2 < 0.2: axis_j2_neutral = True
        
        # Combinar inputs de Menu
        menu_arriba = rl.is_key_pressed(rl.KEY_UP) or dpad_j1_up or dpad_j2_up or axis_j1_up or axis_j2_up
        menu_abajo = rl.is_key_pressed(rl.KEY_DOWN) or dpad_j1_down or dpad_j2_down or axis_j1_down or axis_j2_down
        
        # A (Aceptar) y B (Atras)
        menu_aceptar = rl.is_key_pressed(rl.KEY_ENTER) or rl.is_gamepad_button_pressed(GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_DOWN) or rl.is_gamepad_button_pressed(GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_DOWN) # A
        menu_atras_btn = rl.is_key_pressed(rl.KEY_ESCAPE) or rl.is_gamepad_button_pressed(GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_RIGHT) or rl.is_gamepad_button_pressed(GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_RIGHT) # B
        
        # Start (Pausa)
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
                    estado_actual = ESTADO_SELECCION_MODO
                    opcion_menu_seleccionada = 0
                elif opcion_menu_seleccionada == 1: # Ver Historial
                    historial_lineas = leer_historial()
                    estado_actual = ESTADO_HISTORIAL
                elif opcion_menu_seleccionada == 2: # Salir
                    break # Rompe el bucle principal

        # --- ESTADO: SELECCION DE MODO ---
        elif estado_actual == ESTADO_SELECCION_MODO:
            opciones_menu = ["Jugador vs IA", "Jugador 1 vs Jugador 2", "Volver"]
            
            if menu_abajo: opcion_menu_seleccionada = (opcion_menu_seleccionada + 1) % len(opciones_menu)
            if menu_arriba: opcion_menu_seleccionada = (opcion_menu_seleccionada - 1 + len(opciones_menu)) % len(opciones_menu)

            if menu_aceptar:
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
                if opcion_menu_seleccionada == 0: # Facil
                    dificultad_ia = "facil"
                    velocidad_ia = 4
                elif opcion_menu_seleccionada == 1: # Normal
                    dificultad_ia = "normal"
                    velocidad_ia = 6
                elif opcion_menu_seleccionada == 2: # Dificil
                    dificultad_ia = "dificil"
                    velocidad_ia = 9
                elif opcion_menu_seleccionada == 3: # Extremo
                    dificultad_ia = "extremo"
                    velocidad_ia = 11
                elif opcion_menu_seleccionada == 4: # Volver
                    estado_actual = ESTADO_SELECCION_MODO
                    opcion_menu_seleccionada = 0
                    continue
                
                # Si no fue "Volver", iniciar el juego
                estado_actual = ESTADO_JUGANDO
                # --- Resetear el juego antes de empezar ---
                player1_y, oponente_y = SCREEN_HEIGHT // 2 - paddle_height // 2, SCREEN_HEIGHT // 2 - paddle_height // 2
                player1_puntos, oponente_puntos = 0, 0
                player1_partidas, oponente_partidas = 0, 0
                ball_x, ball_y, ball_speed_x, ball_speed_y = reset_pelota()
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
                estado_actual = estado_previo # Volver a donde estabamos (Pausa)
                opcion_menu_seleccionada = 1 # Reseleccionar "Controles"

        # --- ESTADO: PAUSA ---
        elif estado_actual == ESTADO_PAUSA:
            opciones_menu = ["Continuar", "Controles", "Salir al Menu Principal"]
            
            if menu_abajo: opcion_menu_seleccionada = (opcion_menu_seleccionada + 1) % len(opciones_menu)
            if menu_arriba: opcion_menu_seleccionada = (opcion_menu_seleccionada - 1 + len(opciones_menu)) % len(opciones_menu)
            
            # Continuar con ESC, Start, o B
            if menu_atras_btn or juego_pausa_btn:
                estado_actual = ESTADO_JUGANDO
            
            if menu_aceptar:
                if opcion_menu_seleccionada == 0: # Continuar
                    estado_actual = ESTADO_JUGANDO
                elif opcion_menu_seleccionada == 1: # Controles
                    estado_previo = ESTADO_PAUSA # Guardar de donde venimos
                    estado_actual = ESTADO_CONTROLES
                elif opcion_menu_seleccionada == 2: # Salir al Menu
                    estado_actual = ESTADO_MENU_PRINCIPAL
                    opcion_menu_seleccionada = 0

        # --- ESTADO: GAME OVER ---
        elif estado_actual == ESTADO_GAME_OVER:
            if menu_aceptar: # Revancha (ENTER o A)
                # Resetear el juego
                player1_y, oponente_y = SCREEN_HEIGHT // 2 - paddle_height // 2, SCREEN_HEIGHT // 2 - paddle_height // 2
                player1_puntos, oponente_puntos = 0, 0
                player1_partidas, oponente_partidas = 0, 0
                ball_x, ball_y, ball_speed_x, ball_speed_y = reset_pelota()
                game_over, punto_anotado, partida_ganada_por_alguien = False, False, False
                estado_actual = ESTADO_JUGANDO
                tiempo_partida, multiplicador_velocidad, tiempo_acumulado = 0.0, 1.0, 0.0
                player1_stamina, oponente_stamina = MAX_STAMINA, MAX_STAMINA
                player1_stamina_cooldown, oponente_stamina_cooldown = 0.0, 0.0
            
            if menu_atras_btn: # Volver al menu (ESC o B)
                # Resetear por si acaso
                player1_y, oponente_y = SCREEN_HEIGHT // 2 - paddle_height // 2, SCREEN_HEIGHT // 2 - paddle_height // 2
                player1_puntos, oponente_puntos = 0, 0
                player1_partidas, oponente_partidas = 0, 0
                ball_x, ball_y, ball_speed_x, ball_speed_y = reset_pelota()
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
                
                # rl.get_gamepad_button_pressed() devuelve 0 si no hay boton
                if rl.get_key_pressed() != 0 or rl.get_gamepad_button_pressed() != 0:
                    punto_anotado = False
                    
                    # Reiniciar tiempo y velocidad DESPUES de cada punto
                    tiempo_partida = 0.0
                    multiplicador_velocidad = 1.0
                    tiempo_acumulado = 0.0
                    
                    # Si la ronda se gano, AHORA resetea los puntos
                    if partida_ganada_por_alguien:
                        player1_puntos, oponente_puntos = 0, 0
                        partida_ganada_por_alguien = False

                    ball_x, ball_y, ball_speed_x, ball_speed_y = reset_pelota()
                else:
                    pass
            
            # --- Logica de Pausa (ESC o Start) ---
            elif juego_pausa_btn:
                estado_actual = ESTADO_PAUSA
                opcion_menu_seleccionada = 0
            
            # --- LOGICA DEL JUEGO (SI NO ESTA PAUSADO Y NO HAY PUNTO) ---
            elif not punto_anotado:
                
                delta_tiempo = rl.get_frame_time()
                tiempo_partida += delta_tiempo
                
                # --- Aumento de velocidad de la pelota ---
                tiempo_acumulado += delta_tiempo
                if tiempo_acumulado >= TIEMPO_AUMENTO_VELOCIDAD:
                    tiempo_acumulado = 0.0
                    ball_speed_x *= FACTOR_AUMENTO
                    ball_speed_y *= FACTOR_AUMENTO
                    multiplicador_velocidad *= FACTOR_AUMENTO
                
                # --- Resetear flags de movimiento ---
                player1_is_moving = False
                oponente_is_moving = False

                # --- Logica de Estamina J1 ---
                paddle_speed_j1 = paddle_speed_jugador_base
                paddle_color_j1 = rl.WHITE
                
                # Usando (RIGHT_FACE) A,B,X,Y
                boost_j1_teclado = rl.is_key_down(rl.KEY_D)
                boost_j1_mando = gamepad_j1_conectado and (rl.is_gamepad_button_down(GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_DOWN) or # A
                                                            rl.is_gamepad_button_down(GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_RIGHT) or # B
                                                            rl.is_gamepad_button_down(GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_LEFT) or # X
                                                            rl.is_gamepad_button_down(GAMEPAD_J1, rl.GAMEPAD_BUTTON_RIGHT_FACE_UP)) # Y
                
                if player1_stamina_cooldown > 0:
                    player1_stamina_cooldown -= delta_tiempo
                    player1_stamina += delta_tiempo * (MAX_STAMINA / BOOST_COOLDOWN_TOTAL) # Regen en cooldown
                    if player1_stamina > MAX_STAMINA: player1_stamina = MAX_STAMINA
                    player1_is_boosting = False
                else:
                    if (boost_j1_teclado or boost_j1_mando) and player1_stamina > 0:
                        player1_is_boosting = True
                        player1_stamina -= delta_tiempo # Drenar estamina
                        if player1_stamina <= 0:
                            player1_stamina = 0
                            player1_stamina_cooldown = BOOST_COOLDOWN_TOTAL # Activar cooldown
                    else:
                        player1_is_boosting = False
                        player1_stamina += delta_tiempo # Regen 1:1
                        if player1_stamina > MAX_STAMINA: player1_stamina = MAX_STAMINA
                
                if player1_is_boosting:
                    paddle_speed_j1 *= BOOST_FACTOR
                    paddle_color_j1 = rl.SKYBLUE

                # --- Movimiento del Jugador 1 (Izquierda) ---
                # Usando (LEFT_FACE) D-Pad y Eje Y
                axis_y_j1 = rl.get_gamepad_axis_movement(GAMEPAD_J1, GAMEPAD_AXIS_Y) if gamepad_j1_conectado else 0
                
                if rl.is_key_down(rl.KEY_W) or (gamepad_j1_conectado and (rl.is_gamepad_button_down(GAMEPAD_J1, rl.GAMEPAD_BUTTON_LEFT_FACE_UP) or axis_y_j1 < -0.2)):
                    player1_y -= paddle_speed_j1
                    player1_is_moving = True
                if rl.is_key_down(rl.KEY_S) or (gamepad_j1_conectado and (rl.is_gamepad_button_down(GAMEPAD_J1, rl.GAMEPAD_BUTTON_LEFT_FACE_DOWN) or axis_y_j1 > 0.2)):
                    player1_y += paddle_speed_j1
                    player1_is_moving = True

                # Limites J1
                if player1_y < 0: player1_y = 0
                if player1_y > SCREEN_HEIGHT - paddle_height: player1_y = SCREEN_HEIGHT - paddle_height

                # --- Movimiento del Oponente (IA o Jugador 2) ---
                paddle_speed_op = paddle_speed_jugador_base
                paddle_color_op = rl.WHITE

                if modo_juego == "ia":
                    # --- IA ---
                    if dificultad_ia == "extremo":
                        target_y = 0 
                        if ball_y > SCREEN_HEIGHT / 2: target_y = ball_y - (paddle_height * 0.1) 
                        else: target_y = ball_y - (paddle_height * 0.9)
                        
                        if oponente_y > target_y: oponente_y -= velocidad_ia
                        elif oponente_y < target_y: oponente_y += velocidad_ia
                    
                    elif dificultad_ia == "dificil":
                        if oponente_y + paddle_height // 2 < ball_y: oponente_y += velocidad_ia
                        elif oponente_y + paddle_height // 2 > ball_y: oponente_y -= velocidad_ia
                    
                    else: # Facil y Normal
                        if oponente_y + paddle_height // 2 < ball_y - 10: oponente_y += velocidad_ia
                        elif oponente_y + paddle_height // 2 > ball_y + 10: oponente_y -= velocidad_ia
                    
                    oponente_is_moving = True # IA siempre se mueve

                elif modo_juego == "multi":
                    # --- Logica de Estamina J2 ---
                    # Usando (RIGHT_FACE) A,B,X,Y
                    boost_j2_teclado = rl.is_key_down(rl.KEY_LEFT)
                    boost_j2_mando = gamepad_j2_conectado and (rl.is_gamepad_button_down(GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_DOWN) or
                                                                rl.is_gamepad_button_down(GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_RIGHT) or
                                                                rl.is_gamepad_button_down(GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_LEFT) or
                                                                rl.is_gamepad_button_down(GAMEPAD_J2, rl.GAMEPAD_BUTTON_RIGHT_FACE_UP))

                    if oponente_stamina_cooldown > 0:
                        oponente_stamina_cooldown -= delta_tiempo
                        oponente_stamina += delta_tiempo * (MAX_STAMINA / BOOST_COOLDOWN_TOTAL)
                        if oponente_stamina > MAX_STAMINA: oponente_stamina = MAX_STAMINA
                        oponente_is_boosting = False
                    else:
                        if (boost_j2_teclado or boost_j2_mando) and oponente_stamina > 0:
                            oponente_is_boosting = True
                            oponente_stamina -= delta_tiempo
                            if oponente_stamina <= 0:
                                oponente_stamina = 0
                                oponente_stamina_cooldown = BOOST_COOLDOWN_TOTAL
                        else:
                            oponente_is_boosting = False
                            oponente_stamina += delta_tiempo
                            if oponente_stamina > MAX_STAMINA: oponente_stamina = MAX_STAMINA
                    
                    if oponente_is_boosting:
                        paddle_speed_op *= BOOST_FACTOR
                        paddle_color_op = rl.YELLOW

                    # --- Movimiento J2 ---
                    # Usando (LEFT_FACE) D-Pad y Eje Y
                    axis_y_j2 = rl.get_gamepad_axis_movement(GAMEPAD_J2, GAMEPAD_AXIS_Y) if gamepad_j2_conectado else 0

                    if rl.is_key_down(rl.KEY_UP) or (gamepad_j2_conectado and (rl.is_gamepad_button_down(GAMEPAD_J2, rl.GAMEPAD_BUTTON_LEFT_FACE_UP) or axis_y_j2 < -0.2)):
                        oponente_y -= paddle_speed_op
                        oponente_is_moving = True
                    if rl.is_key_down(rl.KEY_DOWN) or (gamepad_j2_conectado and (rl.is_gamepad_button_down(GAMEPAD_J2, rl.GAMEPAD_BUTTON_LEFT_FACE_DOWN) or axis_y_j2 > 0.2)):
                        oponente_y += paddle_speed_op
                        oponente_is_moving = True

                # Limites Oponente
                if oponente_y < 0: oponente_y = 0
                if oponente_y > SCREEN_HEIGHT - paddle_height: oponente_y = SCREEN_HEIGHT - paddle_height

                # --- Movimiento de la pelota ---
                ball_x += ball_speed_x
                ball_y += ball_speed_y

                # --- FISICA MEJORADA: Rebote en los bordes ---
                if ball_y - ball_radius <= 0 or ball_y + ball_radius >= SCREEN_HEIGHT:
                    ball_speed_y *= -1
                    ball_speed_y *= random.uniform(1.0, 1.2)
                
                # --- Puntuacion y Colisiones ---
                
                # Definir buffers de Coyote Time
                buffer_j1 = COYOTE_TIME_BUFFER if player1_is_moving else 0
                buffer_op = COYOTE_TIME_BUFFER if oponente_is_moving else 0

                # --- Logica del Lado Izquierdo (Paleta de J1) ---
                if (ball_x - ball_radius <= paddle_width and 
                    player1_y - buffer_j1 <= ball_y <= player1_y + paddle_height + buffer_j1 and 
                    ball_speed_x < 0):
                    
                    ball_speed_x *= -1
                    hit_position = (ball_y - player1_y) / paddle_height
                    ball_speed_y = 8 * (hit_position - 0.5)
                    
                    if rl.is_key_down(rl.KEY_W): ball_speed_y -= 4
                    if rl.is_key_down(rl.KEY_S): ball_speed_y += 4

                elif (ball_x + ball_radius < 0): # Oponente anota
                    oponente_puntos += 1
                    punto_anotado = True
                    ultimo_anotador = "oponente"
                    
                    # --- Resetear Estamina al anotar punto ---
                    player1_stamina, oponente_stamina = MAX_STAMINA, MAX_STAMINA
                    player1_stamina_cooldown, oponente_stamina_cooldown = 0.0, 0.0
                    
                    if oponente_puntos >= PUNTOS_POR_PARTIDA:
                        oponente_partidas += 1
                        partida_ganada_por_alguien = True # Marcar para resetear puntos
                        
                        if oponente_partidas >= PARTIDAS_PARA_GANAR:
                            game_over = True
                            winner = "IA" if modo_juego == "ia" else "JUGADOR 2"
                            nombre_oponente_str = "IA" if modo_juego == "ia" else "JUGADOR 2"
                            modo_str = f"J1 vs {nombre_oponente_str}"
                            if dificultad_ia: modo_str += f" ({dificultad_ia})"
                            guardar_historial(winner, player1_partidas, oponente_partidas, modo_str)
                
                # --- Logica del Lado Derecho (Paleta de Oponente) ---
                if (ball_x + ball_radius >= SCREEN_WIDTH - paddle_width and 
                    oponente_y - buffer_op <= ball_y <= oponente_y + paddle_height + buffer_op and 
                    ball_speed_x > 0):
                    
                    ball_speed_x *= -1
                    hit_position = (ball_y - oponente_y) / paddle_height
                    ball_speed_y = 8 * (hit_position - 0.5)
                    
                    if modo_juego == "multi":
                        if rl.is_key_down(rl.KEY_UP): ball_speed_y -= 4
                        if rl.is_key_down(rl.KEY_DOWN): ball_speed_y += 4

                elif (ball_x - ball_radius > SCREEN_WIDTH): # J1 anota
                    player1_puntos += 1
                    punto_anotado = True
                    ultimo_anotador = "j1"

                    # --- Resetear Estamina al anotar punto ---
                    player1_stamina, oponente_stamina = MAX_STAMINA, MAX_STAMINA
                    player1_stamina_cooldown, oponente_stamina_cooldown = 0.0, 0.0
                    
                    if player1_puntos >= PUNTOS_POR_PARTIDA:
                        player1_partidas += 1
                        partida_ganada_por_alguien = True # Marcar para resetear puntos
                        
                        if player1_partidas >= PARTIDAS_PARA_GANAR:
                            game_over = True
                            winner = "JUGADOR 1"
                            nombre_oponente = "IA" if modo_juego == "ia" else "JUGADOR 2"
                            modo_str = f"J1 vs {nombre_oponente}"
                            if dificultad_ia: modo_str += f" ({dificultad_ia})"
                            guardar_historial(winner, player1_partidas, oponente_partidas, modo_str)
                
                # Si el juego ha terminado, cambia el estado
                if game_over:
                    estado_actual = ESTADO_GAME_OVER
                    opcion_menu_seleccionada = 0
        
        
        # -----------------------------------------------------
        # --- 2. DIBUJADO (GRAFICOS) ---
        # -----------------------------------------------------
        rl.begin_drawing()
        rl.clear_background(rl.BLACK)
        
        # --- DIBUJAR: ESTADO MENU PRINCIPAL ---
        if estado_actual == ESTADO_MENU_PRINCIPAL:
            opciones_menu = ["Jugar", "Ver Historial", "Salir"]
            rl.draw_text("PING PONG", SCREEN_WIDTH // 2 - (rl.measure_text("PING PONG", 40) // 2), SCREEN_HEIGHT // 2 - 100, 40, rl.WHITE)
            
            for i, opcion in enumerate(opciones_menu):
                color = rl.YELLOW if i == opcion_menu_seleccionada else rl.WHITE
                rl.draw_text(opcion, SCREEN_WIDTH // 2 - (rl.measure_text(opcion, 30) // 2), SCREEN_HEIGHT // 2 + i * 40, 30, color)
            
            rl.draw_text("Usa Flechas/Cruceta/Joystick y Enter/(A)", 10, SCREEN_HEIGHT - 30, 15, rl.GRAY)
            if gamepad_j1_conectado: rl.draw_text("Mando 1 Detectado", SCREEN_WIDTH - 180, 10, 15, rl.GREEN)
            if gamepad_j2_conectado: rl.draw_text("Mando 2 Detectado", SCREEN_WIDTH - 180, 30, 15, rl.GREEN)

        # --- DIBUJAR: ESTADO SELECCION MODO ---
        elif estado_actual == ESTADO_SELECCION_MODO:
            opciones_menu = ["Jugador vs IA", "Jugador 1 vs Jugador 2", "Volver"]
            rl.draw_text("Modo de Juego", SCREEN_WIDTH // 2 - (rl.measure_text("Modo de Juego", 40) // 2), SCREEN_HEIGHT // 2 - 100, 40, rl.WHITE)
            
            for i, opcion in enumerate(opciones_menu):
                color = rl.YELLOW if i == opcion_menu_seleccionada else rl.WHITE
                rl.draw_text(opcion, SCREEN_WIDTH // 2 - (rl.measure_text(opcion, 30) // 2), SCREEN_HEIGHT // 2 + i * 40, 30, color)
            rl.draw_text("ESC/(B) para volver", 10, SCREEN_HEIGHT - 30, 15, rl.GRAY)
        
        # --- DIBUJAR: ESTADO SELECCION DIFICULTAD ---
        elif estado_actual == ESTADO_SELECCION_DIFICULTAD:
            opciones_menu = ["Facil", "Normal", "Dificil", "Extremo (Jaque Mate)", "Volver"]
            rl.draw_text("Dificultad de la IA", SCREEN_WIDTH // 2 - (rl.measure_text("Dificultad de la IA", 40) // 2), SCREEN_HEIGHT // 2 - 120, 40, rl.WHITE)
            
            for i, opcion in enumerate(opciones_menu):
                color = rl.YELLOW if i == opcion_menu_seleccionada else rl.WHITE
                rl.draw_text(opcion, SCREEN_WIDTH // 2 - (rl.measure_text(opcion, 30) // 2), SCREEN_HEIGHT // 2 - 20 + i * 40, 30, color)
            rl.draw_text("ESC/(B) para volver", 10, SCREEN_HEIGHT - 30, 15, rl.GRAY)
        
        # --- DIBUJAR: ESTADO HISTORIAL ---
        elif estado_actual == ESTADO_HISTORIAL:
            rl.draw_text("Historial de Partidas", 20, 20, 30, rl.WHITE)
            rl.draw_text("Presiona ESC/(B) o Enter/(A) para volver", 20, SCREEN_HEIGHT - 30, 15, rl.GRAY)
            
            y_pos = 70
            for linea in historial_lineas[:35]: # Mostrar mas lineas (pantalla mas grande)
                rl.draw_text(linea, 20, y_pos, 20, rl.WHITE)
                y_pos += 25
        
        # --- DIBUJAR ESTADO CONTROLES ---
        elif estado_actual == ESTADO_CONTROLES:
            rl.draw_text("Controles", SCREEN_WIDTH // 2 - (rl.measure_text("Controles", 40) // 2), 100, 40, rl.WHITE)
            rl.draw_text("Presiona ESC/(B) o Enter/(A) para volver", SCREEN_WIDTH // 2 - (rl.measure_text("Presiona ESC/(B) o Enter/(A) para volver", 20) // 2), SCREEN_HEIGHT - 50, 20, rl.GRAY)

            y_base_j1 = 200
            rl.draw_text("Jugador 1 (Izquierda)", 200, y_base_j1, 30, rl.WHITE)
            if gamepad_j1_conectado:
                rl.draw_text("- Mover: Joystick Izquierdo o Cruceta", 200, y_base_j1 + 50, 20, rl.WHITE)
                rl.draw_text("- Boost: A, B, X, o Y", 200, y_base_j1 + 80, 20, rl.WHITE)
            else:
                rl.draw_text("- Mover: W / S", 200, y_base_j1 + 50, 20, rl.WHITE)
                rl.draw_text("- Boost: D", 200, y_base_j1 + 80, 20, rl.WHITE)
            
            y_base_j2 = 200
            rl.draw_text("Jugador 2 (Derecha)", SCREEN_WIDTH - 500, y_base_j2, 30, rl.WHITE)
            if modo_juego == "ia":
                 rl.draw_text("- Oponente: IA", SCREEN_WIDTH - 500, y_base_j2 + 50, 20, rl.GRAY)
            elif gamepad_j2_conectado:
                rl.draw_text("- Mover: Joystick Izquierdo o Cruceta", SCREEN_WIDTH - 500, y_base_j2 + 50, 20, rl.WHITE)
                rl.draw_text("- Boost: A, B, X, o Y", SCREEN_WIDTH - 500, y_base_j2 + 80, 20, rl.WHITE)
            else:
                rl.draw_text("- Mover: Flecha Arriba / Flecha Abajo", SCREEN_WIDTH - 500, y_base_j2 + 50, 20, rl.WHITE)
                rl.draw_text("- Boost: Flecha Izquierda", SCREEN_WIDTH - 500, y_base_j2 + 80, 20, rl.WHITE)
            
            rl.draw_text("General", 200, y_base_j1 + 200, 30, rl.WHITE)
            rl.draw_text("- Pausa: ESC o Start", 200, y_base_j1 + 250, 20, rl.WHITE)
            rl.draw_text("- Menus: Cruceta/Joystick, (A) Aceptar, (B) Atras", 200, y_base_j1 + 280, 20, rl.WHITE)

        # --- DIBUJAR: ESTADO JUGANDO / PAUSA / GAME OVER ---
        elif estado_actual in [ESTADO_JUGANDO, ESTADO_PAUSA, ESTADO_GAME_OVER]:
            # Dibuja paletas con colores de boost
            rl.draw_rectangle(0, player1_y, paddle_width, paddle_height, paddle_color_j1)
            rl.draw_rectangle(SCREEN_WIDTH - paddle_width, oponente_y, paddle_width, paddle_height, paddle_color_op)
            
            # Dibuja el resto
            rl.draw_circle(ball_x, ball_y, ball_radius, rl.WHITE)
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
            rl.draw_text(texto_velocidad, SCREEN_WIDTH // 2 - (rl.measure_text(texto_velocidad, 20) // 2), 35, 20, rl.SKYBLUE)

            # Controles
            rl.draw_text("J1: W/S", 10, SCREEN_HEIGHT - 30, 15, rl.GRAY)
            rl.draw_text("ESC/Start: Pausa", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30, 15, rl.GRAY)
            
            # --- Barras de Estamina (pequenas y coloridas) ---
            # J1
            rl.draw_text("Boost [D]", 10, SCREEN_HEIGHT - 75, 15, rl.GRAY)
            rl.draw_rectangle(10, SCREEN_HEIGHT - 60, STAMINA_BAR_WIDTH, 10, rl.DARKGRAY)
            stamina_width_j1 = int((player1_stamina / MAX_STAMINA) * STAMINA_BAR_WIDTH)
            color_stamina_j1 = rl.RED if player1_stamina_cooldown > 0 else rl.SKYBLUE
            rl.draw_rectangle(10, SCREEN_HEIGHT - 60, stamina_width_j1, 10, color_stamina_j1)
            
            # J2 / Multi
            if modo_juego == "multi":
                rl.draw_text("J2: Flechas Arriba/Abajo", 100, SCREEN_HEIGHT - 30, 15, rl.GRAY)
                rl.draw_text("Boost [<-]", SCREEN_WIDTH - (STAMINA_BAR_WIDTH + 10), SCREEN_HEIGHT - 75, 15, rl.GRAY)
                rl.draw_rectangle(SCREEN_WIDTH - (STAMINA_BAR_WIDTH + 10), SCREEN_HEIGHT - 60, STAMINA_BAR_WIDTH, 10, rl.DARKGRAY)
                stamina_width_op = int((oponente_stamina / MAX_STAMINA) * STAMINA_BAR_WIDTH)
                color_stamina_op = rl.RED if oponente_stamina_cooldown > 0 else rl.YELLOW
                rl.draw_rectangle(SCREEN_WIDTH - (STAMINA_BAR_WIDTH + 10), SCREEN_HEIGHT - 60, stamina_width_op, 10, color_stamina_op)

            
            # --- DIBUJAR: Pausa por Punto (Encima del juego) ---
            if estado_actual == ESTADO_JUGANDO and punto_anotado:
                rl.draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, rl.Color(0, 0, 0, 179))
                texto_punto = ""
                color_punto = rl.WHITE
                
                if ultimo_anotador == "j1":
                    texto_punto = "¡Punto para J1!"
                    color_punto = rl.GREEN
                elif ultimo_anotador == "oponente":
                    nombre_oponente = "IA" if modo_juego == "ia" else "J2"
                    texto_punto = f"Punto para {nombre_oponente}"
                    color_punto = rl.RED
                
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
                
                # Instrucciones claras
                rl.draw_text("Presiona ENTER/(A) para la Revancha", SCREEN_WIDTH // 2 - (rl.measure_text("Presiona ENTER/(A) para la Revancha", 20) // 2), SCREEN_HEIGHT // 2 + 20, 20, rl.YELLOW)
                rl.draw_text("Presiona ESC/(B) para Volver al Menu", SCREEN_WIDTH // 2 - (rl.measure_text("Presiona ESC/(B) para Volver al Menu", 20) // 2), SCREEN_HEIGHT // 2 + 50, 20, rl.WHITE)
        
        rl.end_drawing()
        # --- Fin del Dibujado ---
    
    # --- Fin del Bucle Principal de la Aplicacion ---
    
    # Cierra la ventana de raylib y libera los recursos
    rl.close_window()