"""
fecha: 2025/10/31
Autor: Alejandro Uzcategui, Gabriel Guedez, Hector Vargas
-
descripcion: Componente "Vista" (MVC).
Se encarga de inicializar la ventana de Raylib y de TODO el dibujado.
Lee el estado del 'modelo' para saber que dibujar.
"""

try:
    import raylibpy as rl
except ImportError:
    print("Error: No se pudo importar la biblioteca 'raylibpy'.")
    print("Por favor, instálela usando: pip install raylib-py")
    exit()

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

import modelo # Para las constantes y leer el estado

class Vista:
    """
    Maneja toda la inicializacion de la ventana y el dibujado.
    """
    def __init__(self):
        rl.init_window(modelo.SCREEN_WIDTH, modelo.SCREEN_HEIGHT, modelo.GAME_TITLE)
        
        try:
            icon_image = rl.load_image("icon.png")
            rl.set_window_icon(icon_image)
            rl.unload_image(icon_image)
        except Exception as e:
            print(f"Advertencia: No se pudo cargar 'icon.png'. Error: {e}")

        # El sonido de inicio esta ligado a la creacion de la ventana
        winsound.PlaySound("C:/Windows/Media/notify.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
            
        rl.set_target_fps(90)
        rl.set_exit_key(0) # El cierre se maneja en el bucle principal

        # Colores de Raylib (cacheados)
        self.COLOR_FONDO = rl.Color(*modelo.COLOR_FONDO_AZUL)
        self.WHITE = rl.Color(*modelo.WHITE_TUPLE)
        self.YELLOW = rl.Color(253, 249, 0, 255)
        self.GREEN = rl.Color(0, 228, 48, 255)
        self.RED = rl.Color(230, 41, 55, 255)
        self.GRAY = rl.Color(130, 130, 130, 255)
        self.DARKGRAY = rl.Color(80, 80, 80, 255)
        self.SKYBLUE = rl.Color(102, 191, 255, 255)
        self.ORANGE = rl.Color(255, 161, 0, 255)
        self.GOLD = rl.Color(255, 203, 0, 255)
        self.BLACK_TINT_WEAK = rl.Color(0, 0, 0, 179)
        self.BLACK_TINT_STRONG = rl.Color(0, 0, 0, 204)

    def cerrar(self):
        """
        Cierra la ventana de Raylib.
        """
        rl.close_window()

    def dibujar(self, estado: modelo.GameState):
        """
        Dibuja el fotograma actual basado en el estado del juego.
        """
        rl.begin_drawing()
        rl.clear_background(self.COLOR_FONDO)

        # --- Router de Dibujado ---
        if estado.estado_actual == modelo.ESTADO_MENU_PRINCIPAL:
            self._dibujar_menu_principal(estado)
        
        elif estado.estado_actual == modelo.ESTADO_SELECCION_MODO:
            self._dibujar_seleccion_modo(estado)

        elif estado.estado_actual == modelo.ESTADO_SELECCION_DIFICULTAD:
            self._dibujar_seleccion_dificultad(estado)

        elif estado.estado_actual == modelo.ESTADO_HISTORIAL:
            self._dibujar_historial(estado)
        
        elif estado.estado_actual == modelo.ESTADO_CONTROLES:
            self._dibujar_controles(estado)

        elif estado.estado_actual in [modelo.ESTADO_JUGANDO, modelo.ESTADO_PAUSA, modelo.ESTADO_GAME_OVER]:
            self._dibujar_juego(estado)
            
            # --- Capas Superpuestas (Overlays) ---
            if estado.punto_anotado and estado.estado_actual == modelo.ESTADO_JUGANDO:
                self._dibujar_pausa_punto(estado)
            elif estado.estado_actual == modelo.ESTADO_PAUSA:
                self._dibujar_pausa(estado)
            elif estado.estado_actual == modelo.ESTADO_GAME_OVER:
                self._dibujar_game_over(estado)
        
        rl.end_drawing()

    #========================
    # Funciones de Dibujado (Privadas)
    #========================

    def _dibujar_menu_principal(self, estado: modelo.GameState):
        opciones_menu = ["Jugar", "Ver Historial", "Salir"]
        for i, opcion in enumerate(opciones_menu):
            color = self.YELLOW if i == estado.opcion_menu_seleccionada else self.WHITE
            rl.draw_text(opcion, modelo.SCREEN_WIDTH // 2 - (rl.measure_text(opcion, 30) // 2), modelo.SCREEN_HEIGHT // 2 + i * 40, 30, color)
        
        rl.draw_text("Usa Flechas/Cruceta/Joystick y Enter/(A)", 10, modelo.SCREEN_HEIGHT - 30, 15, self.GRAY)
        rl.draw_text(modelo.VERSION_JUEGO, modelo.SCREEN_WIDTH - 150, modelo.SCREEN_HEIGHT - 30, 15, self.YELLOW)
        
        # Deteccion de mandos (esto es 'vista' porque es UI)
        if rl.is_gamepad_available(modelo.GAMEPAD_J1): rl.draw_text("Mando 1 Detectado", modelo.SCREEN_WIDTH - 180, 10, 15, self.GREEN)
        if rl.is_gamepad_available(modelo.GAMEPAD_J2): rl.draw_text("Mando 2 Detectado", modelo.SCREEN_WIDTH - 180, 30, 15, self.RED)

    def _dibujar_seleccion_modo(self, estado: modelo.GameState):
        opciones_menu = ["Jugador vs IA", "Jugador 1 vs Jugador 2", "Volver"]
        rl.draw_text("Modo de Juego", modelo.SCREEN_WIDTH // 2 - (rl.measure_text("Modo de Juego", 40) // 2), modelo.SCREEN_HEIGHT // 2 - 100, 40, self.WHITE)
        for i, opcion in enumerate(opciones_menu):
            color = self.YELLOW if i == estado.opcion_menu_seleccionada else self.WHITE
            rl.draw_text(opcion, modelo.SCREEN_WIDTH // 2 - (rl.measure_text(opcion, 30) // 2), modelo.SCREEN_HEIGHT // 2 + i * 40, 30, color)
        rl.draw_text("ESC/(B) para volver", 10, modelo.SCREEN_HEIGHT - 30, 15, self.GRAY)
        rl.draw_text(modelo.VERSION_JUEGO, modelo.SCREEN_WIDTH - 150, modelo.SCREEN_HEIGHT - 30, 15, self.YELLOW)

    def _dibujar_seleccion_dificultad(self, estado: modelo.GameState):
        opciones_menu = ["Facil", "Normal", "Dificil", "Extremo (Jaque Mate)", "Volver"]
        rl.draw_text("Dificultad de la IA", modelo.SCREEN_WIDTH // 2 - (rl.measure_text("Dificultad de la IA", 40) // 2), modelo.SCREEN_HEIGHT // 2 - 120, 40, self.WHITE)
        for i, opcion in enumerate(opciones_menu):
            color = self.YELLOW if i == estado.opcion_menu_seleccionada else self.WHITE
            rl.draw_text(opcion, modelo.SCREEN_WIDTH // 2 - (rl.measure_text(opcion, 30) // 2), modelo.SCREEN_HEIGHT // 2 - 20 + i * 40, 30, color)
        rl.draw_text("ESC/(B) para volver", 10, modelo.SCREEN_HEIGHT - 30, 15, self.GRAY)
        rl.draw_text(modelo.VERSION_JUEGO, modelo.SCREEN_WIDTH - 150, modelo.SCREEN_HEIGHT - 30, 15, self.YELLOW)

    def _dibujar_historial(self, estado: modelo.GameState):
        rl.draw_text("Historial de Partidas", 20, 20, 30, self.WHITE)
        rl.draw_text("Presiona ESC/(B) o Enter/(A) para volver", 20, modelo.SCREEN_HEIGHT - 30, 15, self.GRAY)
        y_pos = 70
        for linea in estado.historial_lineas[:35]:
            rl.draw_text(linea, 20, y_pos, 20, self.WHITE)
            y_pos += 25

    def _dibujar_controles(self, estado: modelo.GameState):
        rl.draw_text("Controles", modelo.SCREEN_WIDTH // 2 - (rl.measure_text("Controles", 40) // 2), 100, 40, self.WHITE)
        rl.draw_text("Presiona ESC/(B) o Enter/(A) para volver", modelo.SCREEN_WIDTH // 2 - (rl.measure_text("Presiona ESC/(B) o Enter/(A) para volver", 20) // 2), modelo.SCREEN_HEIGHT - 50, 20, self.GRAY)
        
        y_base_j1 = 200
        rl.draw_text("Jugador 1 (Izquierda)", 200, y_base_j1, 30, self.WHITE)
        if rl.is_gamepad_available(modelo.GAMEPAD_J1):
            rl.draw_text("- Mover: Joystick Izquierdo o Cruceta", 200, y_base_j1 + 50, 20, self.WHITE)
            rl.draw_text("- Boost Normal (Mantener): A / X", 200, y_base_j1 + 80, 20, self.WHITE)
            rl.draw_text("- Super Boost (Tocar): B / Y", 200, y_base_j1 + 110, 20, self.WHITE)
        else:
            rl.draw_text("- Mover: W / S", 200, y_base_j1 + 50, 20, self.WHITE)
            rl.draw_text("- Boost Normal (Mantener): D", 200, y_base_j1 + 80, 20, self.WHITE)
            rl.draw_text("- Super Boost (Tocar): A", 200, y_base_j1 + 110, 20, self.WHITE)
        
        y_base_j2 = 200
        rl.draw_text("Jugador 2 (Derecha)", modelo.SCREEN_WIDTH - 550, y_base_j2, 30, self.WHITE)
        if estado.modo_juego == "ia":
                rl.draw_text("- Oponente: IA", modelo.SCREEN_WIDTH - 550, y_base_j2 + 50, 20, self.GRAY)
        elif rl.is_gamepad_available(modelo.GAMEPAD_J2):
            rl.draw_text("- Mover: Joystick Izquierdo o Cruceta", modelo.SCREEN_WIDTH - 550, y_base_j2 + 50, 20, self.WHITE)
            rl.draw_text("- Boost Normal (Mantener): A / X", modelo.SCREEN_WIDTH - 550, y_base_j2 + 80, 20, self.WHITE)
            rl.draw_text("- Super Boost (Tocar): B / Y", modelo.SCREEN_WIDTH - 550, y_base_j2 + 110, 20, self.WHITE)
        else:
            rl.draw_text("- Mover: Flecha Arriba / Flecha Abajo", modelo.SCREEN_WIDTH - 550, y_base_j2 + 50, 20, self.WHITE)
            rl.draw_text("- Boost Normal (Mantener): Flecha Izquierda", modelo.SCREEN_WIDTH - 550, y_base_j2 + 80, 20, self.WHITE)
            rl.draw_text("- Super Boost (Tocar): Flecha Derecha", modelo.SCREEN_WIDTH - 550, y_base_j2 + 110, 20, self.WHITE)
        
        rl.draw_text("General", 200, y_base_j1 + 200, 30, self.WHITE)
        rl.draw_text("- Pausa: ESC o Start", 200, y_base_j1 + 250, 20, self.WHITE)
        rl.draw_text("- Menus: Cruceta/Joystick, (A) Aceptar, (B) Atras", 200, y_base_j1 + 280, 20, self.WHITE)

    def _dibujar_juego(self, estado: modelo.GameState):
        # Dibuja Estelas de Paddles
        for i, (y, color_tuple) in enumerate(estado.player1_paddle_trail):
            alpha = (i / modelo.PADDLE_TRAIL_LENGTH) * 0.4
            # La tupla ahora es RGBA (4 valores)
            trail_color = rl.Color(color_tuple[0], color_tuple[1], color_tuple[2], int(alpha * 255))
            rl.draw_rectangle(0, int(y), estado.paddle_width, estado.paddle_height, trail_color)

        for i, (y, color_tuple) in enumerate(estado.oponente_paddle_trail):
            alpha = (i / modelo.PADDLE_TRAIL_LENGTH) * 0.4
            # La tupla ahora es RGBA (4 valores)
            trail_color = rl.Color(color_tuple[0], color_tuple[1], color_tuple[2], int(alpha * 255))
            rl.draw_rectangle(modelo.SCREEN_WIDTH - estado.paddle_width, int(y), estado.paddle_width, estado.paddle_height, trail_color)

        # ===== INICIO DE LA CORRECCION =====
        # Dibuja paletas (con color lerp)
        # La tupla ahora tiene 4 valores (RGBA), asi que no pasamos el '255' extra.
        color_j1 = rl.Color(*estado.paddle_color_j1_tuple)
        color_op = rl.Color(*estado.paddle_color_op_tuple)
        # ===== FIN DE LA CORRECCION =====
        
        rl.draw_rectangle(0, estado.player1_y, estado.paddle_width, estado.paddle_height, color_j1)
        rl.draw_rectangle(modelo.SCREEN_WIDTH - estado.paddle_width, estado.oponente_y, estado.paddle_width, estado.paddle_height, color_op)
        
        # Dibuja la Estela (Pelota)
        for i, (x, y, color_tuple) in enumerate(estado.ball_trail):
            alpha = (i / modelo.BALL_TRAIL_LENGTH) * 0.5
            radius_scale = i / modelo.BALL_TRAIL_LENGTH
            # La tupla de la estela de la pelota (ball_color_tuple) SI tiene 4 valores (RGBA)
            trail_color = rl.Color(color_tuple[0], color_tuple[1], color_tuple[2], int(alpha * 255))
            rl.draw_circle(int(x), int(y), estado.ball_radius * radius_scale, trail_color)

        # Dibuja la pelota
        # La tupla de la pelota (ball_color_tuple) SI tiene 4 valores (RGBA)
        ball_color = rl.Color(*estado.ball_color_tuple)
        rl.draw_circle(estado.ball_x, estado.ball_y, estado.ball_radius, ball_color)
        
        # Linea de medio campo
        for i in range(0, modelo.SCREEN_HEIGHT, 20):
            rl.draw_line(modelo.SCREEN_WIDTH // 2, i, modelo.SCREEN_WIDTH // 2, i + 10, self.GRAY)

        # Marcadores
        rl.draw_text(f"{estado.player1_puntos}", modelo.SCREEN_WIDTH // 4, 20, 50, self.WHITE)
        rl.draw_text(f"{estado.oponente_puntos}", 3 * modelo.SCREEN_WIDTH // 4 - 30, 20, 50, self.WHITE)
        rl.draw_text(f"Partidas: {estado.player1_partidas}", 20, 10, 20, self.GRAY)
        rl.draw_text(f"Partidas: {estado.oponente_partidas}", modelo.SCREEN_WIDTH - 200, 10, 20, self.GRAY)

        # Temporizador y Multiplicador
        minutos = int(estado.tiempo_partida) // 60
        segundos = int(estado.tiempo_partida) % 60
        texto_tiempo = f"Tiempo: {minutos}:{segundos:02d}"
        texto_velocidad = f"x{estado.multiplicador_velocidad:.1f}"
        rl.draw_text(texto_tiempo, modelo.SCREEN_WIDTH // 2 - (rl.measure_text(texto_tiempo, 20) // 2), 10, 20, self.WHITE)
        rl.draw_text(texto_velocidad, modelo.SCREEN_WIDTH // 2 - (rl.measure_text(texto_velocidad, 20) // 2), 35, 20, self.YELLOW)

        # Controles
        rl.draw_text("J1: W/S", 10, modelo.SCREEN_HEIGHT - 30, 15, self.GRAY)
        rl.draw_text("ESC/Start: Pausa", modelo.SCREEN_WIDTH - 150, modelo.SCREEN_HEIGHT - 30, 15, self.GRAY)
        
        # Barras de Estamina (J1)
        rl.draw_text("Boost [D]", 10, modelo.SCREEN_HEIGHT - 75, 15, self.GRAY)
        rl.draw_text("Dash [A]", 10, modelo.SCREEN_HEIGHT - 90, 15, self.GRAY)
        rl.draw_rectangle(10, modelo.SCREEN_HEIGHT - 60, modelo.STAMINA_BAR_WIDTH, 10, self.DARKGRAY)
        stamina_width_j1 = int((estado.player1_stamina / modelo.MAX_STAMINA) * modelo.STAMINA_BAR_WIDTH)
        color_stamina_j1 = self.SKYBLUE if estado.player1_stamina_cooldown > 0 else self.GREEN
        rl.draw_rectangle(10, modelo.SCREEN_HEIGHT - 60, stamina_width_j1, 10, color_stamina_j1)
        
        # Barras de Estamina (J2 / Multi)
        if estado.modo_juego == "multi":
            rl.draw_text("J2: Flechas", 100, modelo.SCREEN_HEIGHT - 30, 15, self.GRAY)
            rl.draw_text("Boost [<-]", modelo.SCREEN_WIDTH - (modelo.STAMINA_BAR_WIDTH + 10), modelo.SCREEN_HEIGHT - 75, 15, self.GRAY)
            rl.draw_text("Dash [->]", modelo.SCREEN_WIDTH - (modelo.STAMINA_BAR_WIDTH + 10), modelo.SCREEN_HEIGHT - 90, 15, self.GRAY)
        
        if estado.modo_juego == "multi" or (estado.modo_juego == "ia" and estado.dificultad_ia == "extremo"):
            rl.draw_rectangle(modelo.SCREEN_WIDTH - (modelo.STAMINA_BAR_WIDTH + 10), modelo.SCREEN_HEIGHT - 60, modelo.STAMINA_BAR_WIDTH, 10, self.DARKGRAY)
            stamina_width_op = int((estado.oponente_stamina / modelo.MAX_STAMINA) * modelo.STAMINA_BAR_WIDTH)
            color_stamina_op = self.ORANGE if estado.oponente_stamina_cooldown > 0 else self.RED
            rl.draw_rectangle(modelo.SCREEN_WIDTH - (modelo.STAMINA_BAR_WIDTH + 10), modelo.SCREEN_HEIGHT - 60, stamina_width_op, 10, color_stamina_op)

    def _dibujar_pausa_punto(self, estado: modelo.GameState):
        rl.draw_rectangle(0, 0, modelo.SCREEN_WIDTH, modelo.SCREEN_HEIGHT, self.BLACK_TINT_WEAK)
        texto_punto, color_punto = "", self.WHITE
        if estado.ultimo_anotador == "j1":
            texto_punto, color_punto = "¡Punto para J1!", self.GREEN
        elif estado.ultimo_anotador == "oponente":
            nombre_oponente = "IA" if estado.modo_juego == "ia" else "J2"
            texto_punto, color_punto = f"Punto para {nombre_oponente}", self.RED
        
        rl.draw_text(texto_punto, modelo.SCREEN_WIDTH // 2 - (rl.measure_text(texto_punto, 30) // 2), modelo.SCREEN_HEIGHT // 2 - 40, 30, color_punto)
        texto_continuar = "Presiona CUALQUIER TECLA/BOTON para continuar"
        rl.draw_text(texto_continuar, modelo.SCREEN_WIDTH // 2 - (rl.measure_text(texto_continuar, 20) // 2), modelo.SCREEN_HEIGHT // 2 + 20, 20, self.WHITE)

    def _dibujar_pausa(self, estado: modelo.GameState):
        opciones_menu = ["Continuar", "Controles", "Salir al Menu Principal"]
        rl.draw_rectangle(0, 0, modelo.SCREEN_WIDTH, modelo.SCREEN_HEIGHT, self.BLACK_TINT_WEAK)
        rl.draw_text("PAUSA", modelo.SCREEN_WIDTH // 2 - (rl.measure_text("PAUSA", 40) // 2), modelo.SCREEN_HEIGHT // 2 - 100, 40, self.WHITE)
        for i, opcion in enumerate(opciones_menu):
            color = self.YELLOW if i == estado.opcion_menu_seleccionada else self.WHITE
            rl.draw_text(opcion, modelo.SCREEN_WIDTH // 2 - (rl.measure_text(opcion, 30) // 2), modelo.SCREEN_HEIGHT // 2 - 20 + i * 40, 30, color)

    def _dibujar_game_over(self, estado: modelo.GameState):
        rl.draw_rectangle(0, 0, modelo.SCREEN_WIDTH, modelo.SCREEN_HEIGHT, self.BLACK_TINT_STRONG)
        texto_ganador = f"¡{estado.winner} GANA EL JUEGO!"
        rl.draw_text(texto_ganador, modelo.SCREEN_WIDTH // 2 - (rl.measure_text(texto_ganador, 40) // 2), modelo.SCREEN_HEIGHT // 2 - 100, 40, self.GOLD)
        
        texto_marcador = f"Marcador Final (Partidas): {estado.player1_partidas} - {estado.oponente_partidas}"
        rl.draw_text(texto_marcador, modelo.SCREEN_WIDTH // 2 - (rl.measure_text(texto_marcador, 20) // 2), modelo.SCREEN_HEIGHT // 2 - 50, 20, self.WHITE)
        
        rl.draw_text("Presiona ENTER/(A) para la Revancha", modelo.SCREEN_WIDTH // 2 - (rl.measure_text("Presiona ENTER/(A) para la Revancha", 20) // 2), modelo.SCREEN_HEIGHT // 2 + 20, 20, self.YELLOW)
        rl.draw_text("Presiona ESC/(B) para Volver al Menu", modelo.SCREEN_WIDTH // 2 - (rl.measure_text("Presiona ESC/(B) para Volver al Menu", 20) // 2), modelo.SCREEN_HEIGHT // 2 + 50, 20, self.WHITE)