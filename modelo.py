"""
fecha: 2025/10/31
Autor: Alejandro Uzcategui, Gabriel Guedez, Hector Vargas
-
descripcion: Componente "Modelo" (MVC).
Contiene todas las constantes, el estado del juego (GameState) y 
la logica pura del juego (fisicas, IA, estamina).
NO CONTIENE CODIGO DE RAYLIB (excepto 'winsound' para feedback).
"""
try:
    import winsound
except ImportError:
    print("Advertencia: 'winsound' no disponible en este SO. No habra efectos de sonido.")
    # Crear un objeto 'dummy' para que las llamadas no fallen
    class DummyWinsound:
        def PlaySound(self, *args): pass
        SND_FILENAME = 0
        SND_ASYNC = 0
    winsound = DummyWinsound()
    
import random
import datetime
import os
import math

#========================
# Constantes Globales
#========================
# ... (El resto de las constantes no cambian) ...
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
GAME_TITLE = "Juego de Ping Pong"
COLOR_FONDO_AZUL = (16, 24, 48, 255) # RGBA
VERSION_JUEGO = "v0.96 (MVC)" 
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
# Clases de Estado y Entradas
#========================

class Entradas:
    # ... (Esta clase no cambia) ...
    def __init__(self):
        self.j1_movimiento = 0.0
        self.j2_movimiento = 0.0
        self.j1_boost_normal = False
        self.j1_super_boost = False
        self.j2_boost_normal = False
        self.j2_super_boost = False
        self.menu_arriba = False
        self.menu_abajo = False
        self.menu_aceptar = False
        self.menu_atras = False
        self.pausa = False
        self.cualquier_tecla = False

class GameState:
    """
    Contiene todo el estado del juego.
    """
    def __init__(self):
        
        self.debe_cerrar = False # Flag para notificar al main.py
        
        
        # --- Estado de la App ---
        self.estado_actual = ESTADO_MENU_PRINCIPAL
        self.estado_previo = ESTADO_MENU_PRINCIPAL 
        # ... (El resto de __init__ no cambia) ...
        self.opcion_menu_seleccionada = 0
        self.modo_juego = "ia"
        self.dificultad_ia = "normal"
        self.historial_lineas = []
        self.paddle_height = 100
        self.paddle_width = 15
        self.paddle_speed_jugador_base = 7
        self.paddle_speed_j1 = self.paddle_speed_jugador_base
        self.paddle_speed_op = self.paddle_speed_jugador_base
        self.ball_radius = 10
        self.player1_y = SCREEN_HEIGHT // 2 - self.paddle_height // 2
        self.oponente_y = SCREEN_HEIGHT // 2 - self.paddle_height // 2
        self.velocidad_ia = 6
        self.player1_puntos = 0
        self.oponente_puntos = 0
        self.player1_partidas = 0
        self.oponente_partidas = 0
        self.game_over = False
        self.winner = ""
        self.ball_x, self.ball_y, self.ball_speed_x, self.ball_speed_y = self._reset_pelota_valores()
        self.ball_color_tuple = WHITE_TUPLE
        self.ball_trail = []
        self.player1_paddle_trail = []
        self.oponente_paddle_trail = []
        self.tiempo_acumulado = 0.0
        self.tiempo_partida = 0.0
        self.multiplicador_velocidad = 1.0
        self.player1_stamina = MAX_STAMINA
        self.player1_stamina_cooldown = 0.0
        self.player1_stamina_regen_delay = 0.0
        self.player1_super_boost_timer = 0.0
        self.player1_super_boost_flash_timer = 0.0
        self.player1_dash_effect_window_timer = 0.0
        self.player1_is_boosting = False
        self.player1_current_regen_time = STAMINA_REGEN_TIME
        self.player1_current_penalty_time = STAMINA_PENALTY_TIME
        self.p1_color_r, self.p1_color_g, self.p1_color_b = 255.0, 255.0, 255.0
        self.paddle_color_j1_tuple = WHITE_TUPLE
        self.oponente_stamina = MAX_STAMINA
        self.oponente_stamina_cooldown = 0.0
        self.oponente_stamina_regen_delay = 0.0
        self.oponente_super_boost_timer = 0.0
        self.oponente_super_boost_flash_timer = 0.0
        self.oponente_dash_effect_window_timer = 0.0
        self.oponente_is_boosting = False
        self.oponente_current_regen_time = STAMINA_REGEN_TIME
        self.oponente_current_penalty_time = STAMINA_PENALTY_TIME
        self.op_color_r, self.op_color_g, self.op_color_b = 255.0, 255.0, 255.0
        self.paddle_color_op_tuple = WHITE_TUPLE
        self.punto_anotado = False
        self.ultimo_anotador = ""
        self.partida_ganada_por_alguien = False
        self.player1_is_moving = False
        self.oponente_is_moving = False

    #========================
    # Funciones de Reseteo y Guardado
    #========================
    # ... _reset_pelota_valores, _reset_juego_completo, _guardar_historial, _leer_historial) ...
    def _reset_pelota_valores(self):
        ball_x = SCREEN_WIDTH // 2
        ball_y = SCREEN_HEIGHT // 2
        direccion_x = random.choice([-1, 1])
        ball_speed_x = 5 * direccion_x
        ball_speed_y = random.uniform(2.0, 4.0) * random.choice([-1, 1])
        return ball_x, ball_y, ball_speed_x, ball_speed_y

    def _reset_juego_completo(self):
        self.player1_y = SCREEN_HEIGHT // 2 - self.paddle_height // 2
        self.oponente_y = SCREEN_HEIGHT // 2 - self.paddle_height // 2
        self.player1_puntos, self.oponente_puntos = 0, 0
        self.player1_partidas, self.oponente_partidas = 0, 0
        self.ball_x, self.ball_y, self.ball_speed_x, self.ball_speed_y = self._reset_pelota_valores()
        self.ball_color_tuple, self.ball_trail = WHITE_TUPLE, []
        self.player1_paddle_trail, self.oponente_paddle_trail = [], []
        self.game_over, self.punto_anotado, self.partida_ganada_por_alguien = False, False, False
        self.tiempo_partida, self.multiplicador_velocidad, self.tiempo_acumulado = 0.0, 1.0, 0.0
        self.player1_stamina, self.oponente_stamina = MAX_STAMINA, MAX_STAMINA
        self.player1_stamina_cooldown, self.oponente_stamina_cooldown = 0.0, 0.0

    def _guardar_historial(self):
        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        nombre_oponente = "IA" if self.modo_juego == "ia" else "JUGADOR 2"
        modo_str = f"J1 vs {nombre_oponente}"
        if self.dificultad_ia: modo_str += f" ({self.dificultad_ia})"
        
        linea = f"[{ahora}] {self.winner} GANA ({self.player1_partidas} a {self.oponente_partidas}) - Modo: {modo_str}\n"
        try:
            with open("historial.txt", "a", encoding="utf-8") as f:
                f.write(linea)
        except Exception as e:
            print(f"Error al guardar historial: {e}")

    def _leer_historial(self):
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
    
    def actualizar_estado(self, entradas, delta_tiempo):
        # ... (Sin cambios en el router) ...
        if self.estado_actual == ESTADO_MENU_PRINCIPAL:
            self._actualizar_menu_principal(entradas)
        
        elif self.estado_actual == ESTADO_SELECCION_MODO:
            self._actualizar_seleccion_modo(entradas)

        elif self.estado_actual == ESTADO_SELECCION_DIFICULTAD:
            self._actualizar_seleccion_dificultad(entradas)

        elif self.estado_actual == ESTADO_HISTORIAL:
            if entradas.menu_atras or entradas.menu_aceptar:
                self.estado_actual = ESTADO_MENU_PRINCIPAL
                self.opcion_menu_seleccionada = 1

        elif self.estado_actual == ESTADO_CONTROLES:
            if entradas.menu_atras or entradas.menu_aceptar:
                self.estado_actual = self.estado_previo

        elif self.estado_actual == ESTADO_PAUSA:
            self._actualizar_pausa(entradas)

        elif self.estado_actual == ESTADO_GAME_OVER:
            if entradas.menu_aceptar:
                self._reset_juego_completo()
                self.estado_actual = ESTADO_JUGANDO
            if entradas.menu_atras:
                self._reset_juego_completo()
                self.estado_actual = ESTADO_MENU_PRINCIPAL
                self.opcion_menu_seleccionada = 0
        
        elif self.estado_actual == ESTADO_JUGANDO:
            self._actualizar_juego(entradas, delta_tiempo)

    #========================
    # Funciones de Actualizacion de Estado
    #========================

    def _actualizar_menu_principal(self, entradas):
        opciones_menu = ["Jugar", "Ver Historial", "Salir"]
        if entradas.menu_abajo: self.opcion_menu_seleccionada = (self.opcion_menu_seleccionada + 1) % len(opciones_menu)
        if entradas.menu_arriba: self.opcion_menu_seleccionada = (self.opcion_menu_seleccionada - 1 + len(opciones_menu)) % len(opciones_menu)
        
        if entradas.menu_aceptar:
            if self.opcion_menu_seleccionada == 0: # Jugar
                winsound.PlaySound("C:/Windows/Media/Speech Disambiguation.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
                self.estado_actual = ESTADO_SELECCION_MODO
                self.opcion_menu_seleccionada = 0
            elif self.opcion_menu_seleccionada == 1: # Ver Historial
                winsound.PlaySound("C:/Windows/Media/Speech Disambiguation.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
                self.historial_lineas = self._leer_historial()
                self.estado_actual = ESTADO_HISTORIAL
            
            # ===== INICIO DE LA CORRECCION (ERROR DE SALIR) =====
            elif self.opcion_menu_seleccionada == 2: # Salir
                winsound.PlaySound("C:/Windows/Media/Alarm02.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
                self.debe_cerrar = True # Cambiamos el flag
            # ===== FIN DE LA CORRECCION =====

    # ... (El resto del archivo 'modelo.py' (desde _actualizar_seleccion_modo hasta el final) no tiene más cambios) ...
    def _actualizar_seleccion_modo(self, entradas):
        opciones_menu = ["Jugador vs IA", "Jugador 1 vs Jugador 2", "Volver"]
        if entradas.menu_abajo: self.opcion_menu_seleccionada = (self.opcion_menu_seleccionada + 1) % len(opciones_menu)
        if entradas.menu_arriba: self.opcion_menu_seleccionada = (self.opcion_menu_seleccionada - 1 + len(opciones_menu)) % len(opciones_menu)
        
        if entradas.menu_aceptar:
            winsound.PlaySound("C:/Windows/Media/Speech Disambiguation.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
            if self.opcion_menu_seleccionada == 0: # Jugar vs IA
                self.modo_juego = "ia"
                self.estado_actual = ESTADO_SELECCION_DIFICULTAD
                self.opcion_menu_seleccionada = 0
            elif self.opcion_menu_seleccionada == 1: # J1 vs J2
                self.modo_juego = "multi"
                self.dificultad_ia = None
                self.estado_actual = ESTADO_JUGANDO
                self._reset_juego_completo()
            elif self.opcion_menu_seleccionada == 2: # Volver
                self.estado_actual = ESTADO_MENU_PRINCIPAL
                self.opcion_menu_seleccionada = 0
        if entradas.menu_atras:
            self.estado_actual = ESTADO_MENU_PRINCIPAL
            self.opcion_menu_seleccionada = 0

    def _actualizar_seleccion_dificultad(self, entradas):
        opciones_menu = ["Facil", "Normal", "Dificil", "Extremo (Jaque Mate)", "Volver"]
        if entradas.menu_abajo: self.opcion_menu_seleccionada = (self.opcion_menu_seleccionada + 1) % len(opciones_menu)
        if entradas.menu_arriba: self.opcion_menu_seleccionada = (self.opcion_menu_seleccionada - 1 + len(opciones_menu)) % len(opciones_menu)
        
        if entradas.menu_aceptar:
            winsound.PlaySound("C:/Windows/Media/Speech Disambiguation.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
            if self.opcion_menu_seleccionada == 0: self.dificultad_ia, self.velocidad_ia = "facil", 4
            elif self.opcion_menu_seleccionada == 1: self.dificultad_ia, self.velocidad_ia = "normal", 6
            elif self.opcion_menu_seleccionada == 2: self.dificultad_ia, self.velocidad_ia = "dificil", 9
            elif self.opcion_menu_seleccionada == 3: self.dificultad_ia, self.velocidad_ia = "extremo", 11
            elif self.opcion_menu_seleccionada == 4: # Volver
                self.estado_actual = ESTADO_SELECCION_MODO
                self.opcion_menu_seleccionada = 0
                return # Salir de la funcion
            
            self.estado_actual = ESTADO_JUGANDO
            self._reset_juego_completo()
        
        if entradas.menu_atras:
            self.estado_actual = ESTADO_SELECCION_MODO
            self.opcion_menu_seleccionada = 0

    def _actualizar_pausa(self, entradas):
        opciones_menu = ["Continuar", "Controles", "Salir al Menu Principal"]
        if entradas.menu_abajo: self.opcion_menu_seleccionada = (self.opcion_menu_seleccionada + 1) % len(opciones_menu)
        if entradas.menu_arriba: self.opcion_menu_seleccionada = (self.opcion_menu_seleccionada - 1 + len(opciones_menu)) % len(opciones_menu)
        
        if entradas.menu_atras or entradas.pausa:
            self.estado_actual = ESTADO_JUGANDO
        
        if entradas.menu_aceptar:
            if self.opcion_menu_seleccionada == 0: # Continuar
                winsound.PlaySound("C:/Windows/Media/Speech On.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
                self.estado_actual = ESTADO_JUGANDO
            elif self.opcion_menu_seleccionada == 1: # Controles
                self.estado_previo = ESTADO_PAUSA
                self.estado_actual = ESTADO_CONTROLES
            elif self.opcion_menu_seleccionada == 2: # Salir al Menu
                winsound.PlaySound("C:/Windows/Media/Alarm02.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
                self.estado_actual = ESTADO_MENU_PRINCIPAL
                self.opcion_menu_seleccionada = 0

    def _actualizar_juego(self, entradas, delta_tiempo):
        
        # --- Logica de Pausa por Punto ---
        if self.punto_anotado:
            if entradas.cualquier_tecla:
                self.punto_anotado = False
                self.tiempo_partida = 0.0
                self.multiplicador_velocidad = 1.0
                self.tiempo_acumulado = 0.0
                if self.partida_ganada_por_alguien:
                    self.player1_puntos, self.oponente_puntos = 0, 0
                    self.partida_ganada_por_alguien = False
                self.ball_x, self.ball_y, self.ball_speed_x, self.ball_speed_y = self._reset_pelota_valores()
                self.ball_color_tuple, self.ball_trail = WHITE_TUPLE, []
                self.player1_paddle_trail, self.oponente_paddle_trail = [], []
            else:
                return # Salir de la actualizacion, estamos pausados

        # --- Logica de Pausa (ESC o Start) ---
        elif entradas.pausa:
            winsound.PlaySound("C:/Windows/Media/Speech Sleep.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
            self.estado_actual = ESTADO_PAUSA
            self.opcion_menu_seleccionada = 0
            return

        # --- ========================================== ---
        # ---         LOGICA DE JUEGO BASICA           ---
        # --- ========================================== ---
        
        self.tiempo_partida += delta_tiempo
        self.tiempo_acumulado += delta_tiempo
        if self.tiempo_acumulado >= TIEMPO_AUMENTO_VELOCIDAD:
            self.tiempo_acumulado = 0.0
            self.ball_speed_x *= FACTOR_AUMENTO
            self.ball_speed_y *= FACTOR_AUMENTO
            self.multiplicador_velocidad *= FACTOR_AUMENTO
        
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y
        
        if self.ball_y - self.ball_radius <= 0 or self.ball_y + self.ball_radius >= SCREEN_HEIGHT:
            self.ball_speed_y *= -1
            self.ball_speed_y *= random.uniform(1.0, 1.2)
            winsound.PlaySound("C:/Windows/Media/Windows Menu Command.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

        self.player1_is_moving = False
        self.oponente_is_moving = False
        self.player1_is_boosting = False
        self.oponente_is_boosting = False
        
        j1_move_input = entradas.j1_movimiento
        j2_move_input = entradas.j2_movimiento

        # --- ========================================== ---
        # ---       LOGICA DE MECANICAS AVANZADAS      ---
        # --- ========================================== ---

        # --- 1. Inputs Avanzados (IA) ---
        boost_j1_tapped = entradas.j1_super_boost
        boost_j1_down = entradas.j1_boost_normal
        boost_j2_tapped = entradas.j2_super_boost
        boost_j2_down = entradas.j2_boost_normal

        if self.modo_juego == "ia":
            if self.dificultad_ia == "extremo":
                self.oponente_is_moving = True
                target_y = self.ball_y - (self.paddle_height * 0.1) if self.ball_y > SCREEN_HEIGHT / 2 else self.ball_y - (self.paddle_height * 0.9)
                distancia_y_ia = abs((self.oponente_y + self.paddle_height / 2) - self.ball_y)
                
                if distancia_y_ia > 250 and self.oponente_stamina >= SUPER_BOOST_COST and self.oponente_stamina_cooldown <= 0:
                    boost_j2_tapped = True
                elif distancia_y_ia > 70 and self.oponente_stamina > 0.2 and self.oponente_stamina_cooldown <= 0:
                    boost_j2_down = True

                if self.oponente_y > target_y: self.oponente_y -= self.velocidad_ia
                elif self.oponente_y < target_y: self.oponente_y += self.velocidad_ia
                j2_move_input = 0
            
            elif self.dificultad_ia == "dificil":
                if self.oponente_y + self.paddle_height // 2 < self.ball_y: j2_move_input = 1.0
                elif self.oponente_y + self.paddle_height // 2 > self.ball_y: j2_move_input = -1.0
            
            else: # Facil / Normal
                if self.oponente_y + self.paddle_height // 2 < self.ball_y - 10: j2_move_input = 1.0
                elif self.oponente_y + self.paddle_height // 2 > self.ball_y + 10: j2_move_input = -1.0


        # --- 2. Logica de Estamina J1 (Boost/Dash) ---
        self.paddle_speed_j1 = self.paddle_speed_jugador_base
        target_color_j1 = WHITE_TUPLE 

        if self.player1_super_boost_flash_timer > 0:
            self.player1_super_boost_flash_timer -= delta_tiempo
            target_color_j1 = FLASH_COLOR_TUPLE
        
        if self.player1_dash_effect_window_timer > 0:
            self.player1_dash_effect_window_timer -= delta_tiempo

        if self.player1_super_boost_timer > 0:
            self.player1_super_boost_timer -= delta_tiempo
            self.paddle_speed_j1 *= SUPER_BOOST_SPEED_FACTOR
            self.player1_is_boosting = True
            if self.player1_super_boost_flash_timer <= 0:
                target_color_j1 = J1_BOOST_COLOR_TUPLE
        
        elif self.player1_dash_effect_window_timer > 0:
            self.player1_is_boosting = True
            target_color_j1 = J1_BOOST_COLOR_TUPLE
        
        elif self.player1_stamina_cooldown > 0:
            self.player1_stamina_cooldown -= delta_tiempo
            self.player1_stamina += delta_tiempo * (MAX_STAMINA / self.player1_current_penalty_time)
            if self.player1_stamina >= MAX_STAMINA:
                self.player1_stamina = MAX_STAMINA
                self.player1_stamina_cooldown = 0
        
        elif self.player1_stamina_regen_delay > 0:
            self.player1_stamina_regen_delay -= delta_tiempo
        
        elif boost_j1_tapped and self.player1_stamina >= SUPER_BOOST_COST:
            self.player1_stamina -= SUPER_BOOST_COST
            self.player1_super_boost_timer = SUPER_BOOST_DURATION
            self.player1_super_boost_flash_timer = SUPER_BOOST_FLASH_DURATION
            self.player1_dash_effect_window_timer = SUPER_BOOST_EFFECT_WINDOW
            
            if self.player1_stamina < SUPER_BOOST_COST: 
                self.player1_stamina = 0
                self.player1_stamina_cooldown = STAMINA_PENALTY_TIME_SUPER_2
                self.player1_current_penalty_time = STAMINA_PENALTY_TIME_SUPER_2
            else:
                self.player1_stamina_regen_delay = SUPER_BOOST_TAP_DELAY
                self.player1_current_regen_time = STAMINA_REGEN_TIME_SUPER_1

        elif boost_j1_down:
            self.player1_is_boosting = True
            self.paddle_speed_j1 *= BOOST_FACTOR
            target_color_j1 = J1_BOOST_COLOR_TUPLE
            self.player1_stamina -= delta_tiempo
            
            if self.player1_stamina <= 0:
                self.player1_stamina = 0
                self.player1_stamina_cooldown = STAMINA_PENALTY_TIME
                self.player1_current_penalty_time = STAMINA_PENALTY_TIME
            
            self.player1_current_regen_time = STAMINA_REGEN_TIME

        else:
            if self.player1_stamina < MAX_STAMINA:
                self.player1_stamina += delta_tiempo * (MAX_STAMINA / self.player1_current_regen_time)
                if self.player1_stamina >= MAX_STAMINA:
                    self.player1_stamina = MAX_STAMINA
                    self.player1_current_regen_time = STAMINA_REGEN_TIME
        
        
        # --- 3. Logica de Estamina J2 / IA Extrema ---
        self.paddle_speed_op = self.paddle_speed_jugador_base
        target_color_op = WHITE_TUPLE
        
        if self.modo_juego == "multi" or (self.modo_juego == "ia" and self.dificultad_ia == "extremo"):
            if self.oponente_super_boost_flash_timer > 0:
                self.oponente_super_boost_flash_timer -= delta_tiempo
                target_color_op = FLASH_COLOR_TUPLE
            
            if self.oponente_dash_effect_window_timer > 0:
                self.oponente_dash_effect_window_timer -= delta_tiempo

            if self.oponente_super_boost_timer > 0:
                self.oponente_super_boost_timer -= delta_tiempo
                self.paddle_speed_op *= SUPER_BOOST_SPEED_FACTOR
                self.oponente_is_boosting = True
                if self.oponente_super_boost_flash_timer <= 0:
                    target_color_op = J2_BOOST_COLOR_TUPLE
            
            elif self.oponente_dash_effect_window_timer > 0:
                self.oponente_is_boosting = True
                target_color_op = J2_BOOST_COLOR_TUPLE

            elif self.oponente_stamina_cooldown > 0:
                self.oponente_stamina_cooldown -= delta_tiempo
                self.oponente_stamina += delta_tiempo * (MAX_STAMINA / self.oponente_current_penalty_time)
                if self.oponente_stamina >= MAX_STAMINA:
                    self.oponente_stamina = MAX_STAMINA
                    self.oponente_stamina_cooldown = 0
            
            elif self.oponente_stamina_regen_delay > 0:
                self.oponente_stamina_regen_delay -= delta_tiempo
            
            elif boost_j2_tapped and self.oponente_stamina >= SUPER_BOOST_COST:
                self.oponente_stamina -= SUPER_BOOST_COST
                self.oponente_super_boost_timer = SUPER_BOOST_DURATION
                self.oponente_super_boost_flash_timer = SUPER_BOOST_FLASH_DURATION
                self.oponente_dash_effect_window_timer = SUPER_BOOST_EFFECT_WINDOW
                
                if self.oponente_stamina < SUPER_BOOST_COST:
                    self.oponente_stamina = 0
                    self.oponente_stamina_cooldown = STAMINA_PENALTY_TIME_SUPER_2
                    self.oponente_current_penalty_time = STAMINA_PENALTY_TIME_SUPER_2
                else:
                    self.oponente_stamina_regen_delay = SUPER_BOOST_TAP_DELAY
                    self.oponente_current_regen_time = STAMINA_REGEN_TIME_SUPER_1

            elif boost_j2_down:
                self.oponente_is_boosting = True
                self.paddle_speed_op *= BOOST_FACTOR
                target_color_op = J2_BOOST_COLOR_TUPLE
                self.oponente_stamina -= delta_tiempo
                
                if self.oponente_stamina <= 0:
                    self.oponente_stamina = 0
                    self.oponente_stamina_cooldown = STAMINA_PENALTY_TIME
                    self.oponente_current_penalty_time = STAMINA_PENALTY_TIME
                
                self.oponente_current_regen_time = STAMINA_REGEN_TIME

            else:
                if self.oponente_stamina < MAX_STAMINA:
                    self.oponente_stamina += delta_tiempo * (MAX_STAMINA / self.oponente_current_regen_time)
                    if self.oponente_stamina >= MAX_STAMINA:
                        self.oponente_stamina = MAX_STAMINA
                        self.oponente_current_regen_time = STAMINA_REGEN_TIME
        
        # --- 4. Aplicar Movimiento Avanzado ---
        if self.dificultad_ia != "extremo":
            self.player1_y += self.paddle_speed_j1 * j1_move_input
            self.oponente_y += self.paddle_speed_op * j2_move_input
        else:
            self.player1_y += self.paddle_speed_j1 * j1_move_input
        
        if j1_move_input != 0.0: self.player1_is_moving = True
        if j2_move_input != 0.0: self.oponente_is_moving = True

        if self.player1_y < 0: self.player1_y = 0
        if self.player1_y > SCREEN_HEIGHT - self.paddle_height: self.player1_y = SCREEN_HEIGHT - self.paddle_height
        if self.oponente_y < 0: self.oponente_y = 0
        if self.oponente_y > SCREEN_HEIGHT - self.paddle_height: self.oponente_y = SCREEN_HEIGHT - self.paddle_height


        # --- 5. Logica de Colision Avanzada (Boost Hit, Coyote) ---
        buffer_j1 = COYOTE_TIME_BUFFER if self.player1_is_moving else 0
        buffer_op = COYOTE_TIME_BUFFER if self.oponente_is_moving else 0
        
        # --- J1 Colision ---
        if (self.ball_x - self.ball_radius <= self.paddle_width and 
            self.player1_y - buffer_j1 <= self.ball_y <= self.player1_y + self.paddle_height + buffer_j1 and 
            self.ball_speed_x < 0):
            
            if self.player1_is_boosting:
                self.ball_color_tuple = self.paddle_color_j1_tuple
                self.ball_speed_y = random.uniform(-BOOST_HIT_Y_VELOCITY_RANGE, BOOST_HIT_Y_VELOCITY_RANGE)
                self.ball_speed_x *= -1.1
                self.player1_stamina = max(0, self.player1_stamina - BOOST_HIT_COST)
            else:
                self.ball_color_tuple = WHITE_TUPLE
                self.ball_speed_x *= -1
                hit_position = (self.ball_y - self.player1_y) / self.paddle_height
                self.ball_speed_y = 8 * (hit_position - 0.5)
            
            winsound.PlaySound("C:/Windows/Media/Windows Information Bar.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

        # --- J2/Oponente Colision ---
        elif (self.ball_x + self.ball_radius >= SCREEN_WIDTH - self.paddle_width and 
            self.oponente_y - buffer_op <= self.ball_y <= self.oponente_y + self.paddle_height + buffer_op and 
            self.ball_speed_x > 0):
            
            if self.oponente_is_boosting:
                self.ball_color_tuple = self.paddle_color_op_tuple
                self.ball_speed_y = random.uniform(-BOOST_HIT_Y_VELOCITY_RANGE, BOOST_HIT_Y_VELOCITY_RANGE)
                self.ball_speed_x *= -1.1
                self.oponente_stamina = max(0, self.oponente_stamina - BOOST_HIT_COST)
            else:
                self.ball_color_tuple = WHITE_TUPLE
                self.ball_speed_x *= -1
                hit_position = (self.ball_y - self.oponente_y) / self.paddle_height
                self.ball_speed_y = 8 * (hit_position - 0.5)
            
            winsound.PlaySound("C:/Windows/Media/Windows Information Bar.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)


        # --- 6. Logica de Puntuacion ---
        
        # Oponente anota
        elif (self.ball_x + self.ball_radius < 0): 
            self.oponente_puntos += 1
            self.punto_anotado = True
            self.ultimo_anotador = "oponente"
            winsound.PlaySound("C:/Windows/Media/Windows Critical Stop.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
            
            self.player1_stamina, self.oponente_stamina = MAX_STAMINA, MAX_STAMINA
            self.player1_stamina_cooldown, self.oponente_stamina_cooldown = 0.0, 0.0
            
            if self.oponente_puntos >= PUNTOS_POR_PARTIDA:
                self.oponente_partidas += 1
                self.partida_ganada_por_alguien = True
                if self.oponente_partidas >= PARTIDAS_PARA_GANAR:
                    self.game_over = True
                    self.winner = "IA" if self.modo_juego == "ia" else "JUGADOR 2"
                    self._guardar_historial()
        
        # J1 anota
        elif (self.ball_x - self.ball_radius > SCREEN_WIDTH): 
            self.player1_puntos += 1
            self.punto_anotado = True
            self.ultimo_anotador = "j1"
            winsound.PlaySound("C:/Windows/Media/Windows Critical Stop.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

            self.player1_stamina, self.oponente_stamina = MAX_STAMINA, MAX_STAMINA
            self.player1_stamina_cooldown, self.oponente_stamina_cooldown = 0.0, 0.0
            
            if self.player1_puntos >= PUNTOS_POR_PARTIDA:
                self.player1_partidas += 1
                self.partida_ganada_por_alguien = True
                if self.player1_partidas >= PARTIDAS_PARA_GANAR:
                    self.game_over = True
                    self.winner = "JUGADOR 1"
                    self._guardar_historial()
        
        if self.game_over:
            self.estado_actual = ESTADO_GAME_OVER
            self.opcion_menu_seleccionada = 0
        
        # --- 7. Logica de Color Suave (Lerp) ---
        lerp_factor = COLOR_LERP_SPEED * delta_tiempo
        self.p1_color_r += (target_color_j1[0] - self.p1_color_r) * lerp_factor
        self.p1_color_g += (target_color_j1[1] - self.p1_color_g) * lerp_factor
        self.p1_color_b += (target_color_j1[2] - self.p1_color_b) * lerp_factor
        self.paddle_color_j1_tuple = (int(self.p1_color_r), int(self.p1_color_g), int(self.p1_color_b), 255)
        
        self.op_color_r += (target_color_op[0] - self.op_color_r) * lerp_factor
        self.op_color_g += (target_color_op[1] - self.op_color_g) * lerp_factor
        self.op_color_b += (target_color_op[2] - self.op_color_b) * lerp_factor
        self.paddle_color_op_tuple = (int(self.op_color_r), int(self.op_color_g), int(self.op_color_b), 255)
        
        # --- 8. Logica de Estela (Pelota) ---
        self.ball_trail.append((self.ball_x, self.ball_y, self.ball_color_tuple))
        if len(self.ball_trail) > BALL_TRAIL_LENGTH:
            self.ball_trail.pop(0)

        # --- 9. Logica de Estela (Paddle) ---
        if self.player1_is_boosting:
            self.player1_paddle_trail.append((self.player1_y, self.paddle_color_j1_tuple))
        if (not self.player1_is_boosting and self.player1_paddle_trail) or len(self.player1_paddle_trail) > PADDLE_TRAIL_LENGTH:
            self.player1_paddle_trail.pop(0)

        if self.oponente_is_boosting:
            self.oponente_paddle_trail.append((self.oponente_y, self.paddle_color_op_tuple))
        if (not self.oponente_is_boosting and self.oponente_paddle_trail) or len(self.oponente_paddle_trail) > PADDLE_TRAIL_LENGTH:
            self.oponente_paddle_trail.pop(0)