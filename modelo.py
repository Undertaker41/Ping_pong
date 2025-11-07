"""
fecha: 2025/10/31
Autor: Alejandro Uzcategui, Gabriel Guedez, Hector Vargas
-
descripcion: maneja la logica de negocio (el juego en sí).
nota: logica de negocio son las reglas y procedimientos que definen como opera nuestro juego.
"""
#========================
#imports
# Importamos la biblioteca raylib para gráficos
# El usuario debe instalarla con: pip install raylib-py
try:
    import raylibpy as rl
except ImportError:
    print("Error: No se pudo importar la biblioteca 'raylibpy'.")
    print("Por favor, instálela usando: pip install raylib-py")
    # Salimos si raylib no está instalado, ya que es crucial
    exit()

#========================
# Constantes del Juego
#========================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GAME_TITLE = "Juego de Ping Pong"

#========================
# Funciones del Juego
#========================
def iniciar_juego():
    """
    Inicia y gestiona la ventana del juego con raylib.
    Juego de Ping Pong completo con paletas, pelota y marcador.
    """
    
    # Inicializa la ventana
    rl.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE)
    rl.set_target_fps(60) # Fija el juego a 60 frames por segundo

    # Variables del juego
    paddle_height = 100
    paddle_width = 15
    paddle_speed = 7

    # Paleta del jugador (izquierda)
    player_y = SCREEN_HEIGHT // 2 - paddle_height // 2

    # Paleta de la IA (derecha)  
    ai_y = SCREEN_HEIGHT // 2 - paddle_height // 2

    # Pelota
    ball_x = SCREEN_WIDTH // 2
    ball_y = SCREEN_HEIGHT // 2
    ball_radius = 10
    ball_speed_x = 9
    ball_speed_y = 8

    # Puntuación
    player_score = 0
    ai_score = 0
    max_score = 12 # <-- ¡Puntuación máxima cambiada de 5 a 12!

    game_over = False
    winner = ""

    # --- Bucle Principal del Juego ---
    while not rl.window_should_close() and not game_over:
        
        # -----------------------------------------------------
        # --- 1. ACTUALIZACIÓN (Lógica del juego) ---
        # -----------------------------------------------------
        
        # Movimiento del jugador (teclas W/S o flechas arriba/abajo)
        if rl.is_key_down(rl.KEY_W) or rl.is_key_down(rl.KEY_UP):
            player_y -= paddle_speed
        if rl.is_key_down(rl.KEY_S) or rl.is_key_down(rl.KEY_DOWN):
            player_y += paddle_speed

        # Mantener la paleta del jugador dentro de la pantalla
        if player_y < 0:
            player_y = 0
        if player_y > SCREEN_HEIGHT - paddle_height:
            player_y = SCREEN_HEIGHT - paddle_height

        # IA simple - sigue la pelota con un poco de retraso para hacerlo más justo
        if ai_y + paddle_height // 2 < ball_y - 10:
            ai_y += paddle_speed - 1
        elif ai_y + paddle_height // 2 > ball_y + 10:
            ai_y -= paddle_speed - 1

        # Mantener la IA dentro de la pantalla
        if ai_y < 0:
            ai_y = 0
        if ai_y > SCREEN_HEIGHT - paddle_height:
            ai_y = SCREEN_HEIGHT - paddle_height

        # Movimiento de la pelota
        ball_x += ball_speed_x
        ball_y += ball_speed_y

        # Rebote en los bordes superior e inferior
        if ball_y - ball_radius <= 0 or ball_y + ball_radius >= SCREEN_HEIGHT:
            ball_speed_y *= -1

        # Colisión con paleta izquierda (jugador)
        if (ball_x - ball_radius <= paddle_width and 
            player_y <= ball_y <= player_y + paddle_height and
            ball_speed_x < 0):
            ball_speed_x *= -1
            # Añadir un poco de efecto según donde golpee la paleta
            hit_position = (ball_y - player_y) / paddle_height
            ball_speed_y = 8 * (hit_position - 0.5)

        # Colisión con paleta derecha (IA)
        if (ball_x + ball_radius >= SCREEN_WIDTH - paddle_width and 
            ai_y <= ball_y <= ai_y + paddle_height and
            ball_speed_x > 0):
            ball_speed_x *= -1
            # Añadir un poco de efecto según donde golpee la paleta
            hit_position = (ball_y - ai_y) / paddle_height
            ball_speed_y = 8 * (hit_position - 0.5)

        # Puntuación - Jugador anota (la IA pierde)
        if ball_x + ball_radius < 0:
            player_score += 1
            # Reset pelota
            ball_x = SCREEN_WIDTH // 2
            ball_y = SCREEN_HEIGHT // 2
            ball_speed_x = 5
            ball_speed_y = 4
            # Pequeña pausa para el reset
            rl.begin_drawing()
            rl.clear_background(rl.BLACK)
            rl.draw_text("¡Punto para ti!", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 15, 20, rl.GREEN)
            rl.end_drawing()
            rl.wait_time(0.5)
            
        # Puntuación - IA anota (el jugador pierde)
        if ball_x - ball_radius > SCREEN_WIDTH:
            ai_score += 1
            # Reset pelota
            ball_x = SCREEN_WIDTH // 2
            ball_y = SCREEN_HEIGHT // 2
            ball_speed_x = -5
            ball_speed_y = 4
            # Pequeña pausa para el reset
            rl.begin_drawing()
            rl.clear_background(rl.BLACK)
            rl.draw_text("Punto para la IA", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 15, 20, rl.RED)
            rl.end_drawing()
            rl.wait_time(0.5)

        # Verificar condición de victoria
        if player_score >= max_score:
            game_over = True
            winner = "JUGADOR"
        elif ai_score >= max_score:
            game_over = True
            winner = "IA"
        
        # -----------------------------------------------------
        # --- 2. DIBUJADO (Gráficos) ---
        # -----------------------------------------------------
        rl.begin_drawing()
        rl.clear_background(rl.BLACK)
        
        # Dibuja las paletas
        rl.draw_rectangle(0, player_y, paddle_width, paddle_height, rl.WHITE)  # Jugador
        rl.draw_rectangle(SCREEN_WIDTH - paddle_width, ai_y, paddle_width, paddle_height, rl.WHITE)  # IA

     # Dibuja la pelota
     rl.draw_circle(ball_x, ball_y, ball_radius, rl.WHITE)
     # Dibuja la línea central punteada
     for i in range(0, SCREEN_HEIGHT, 20):
         rl.draw_line(SCREEN_WIDTH // 2, i, SCREEN_WIDTH // 2, i + 10, rl.GRAY)
     # Dibuja el marcador
     rl.draw_text(f"{player_score}", SCREEN_WIDTH // 4, 20, 40, rl.WHITE)
     rl.draw_text(f"{ai_score}", 3 * SCREEN_WIDTH // 4, 20, 40, rl.WHITE)
     # Dibuja instrucciones
     rl.draw_text("W/S o Flechas: Mover", 10, SCREEN_HEIGHT - 30, 15, rl.GRAY)
     rl.draw_text("ESC: Salir", SCREEN_WIDTH - 80, SCREEN_HEIGHT - 30, 15, rl.GRAY)

        # Si el juego terminó, mostrar pantalla de victoria
        if game_over:
            rl.draw_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, rl.Fade(rl.BLACK, 0.8))
            rl.draw_text(f"¡{winner} GANA!", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, 40, rl.GOLD)
            rl.draw_text(f"Marcador Final: {player_score} - {ai_score}", SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2, 20, rl.WHITE)
            rl.draw_text("Presiona ESC para volver al menú", SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 50, 20, rl.GRAY)
    
        rl.end_drawing()

    # --- Fin del Bucle Principal del Juego ---

    # Cierra la ventana de raylib y libera los recursos
    rl.close_window()