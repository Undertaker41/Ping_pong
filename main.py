"""
fecha: 2025/10/31
Autor: Alejandro Uzcategui, Gabriel Guedez, Hector Vargas
-
descripcion: Archivo principal de ejecucion.
Inicia el Modelo, la Vista y el Controlador (MVC) y corre el bucle
principal del juego.
"""
try:
    import raylibpy as rl
except ImportError:
    print("Error: No se pudo importar la biblioteca 'raylibpy'.")
    print("Por favor, instálela usando: pip install raylib-py")
    exit()

import modelo
import vista
import controlador

def main():
    """
    Funcion principal que inicializa y corre el juego.
    """
    
    # 1. Inicializar los componentes
    estado_juego = modelo.GameState()
    vista_juego = vista.Vista()
    controlador_juego = controlador.Controlador()

    # 2. Bucle principal del juego
    
    # Anadimos la comprobacion del flag 'debe_cerrar' del modelo
    while not rl.window_should_close() and not estado_juego.debe_cerrar:
   
        
        # 3. Obtener el tiempo delta
        delta_tiempo = rl.get_frame_time()
        
        # 4. Procesar Entradas (Controlador)
        # El controlador lee los inputs y devuelve un objeto 'Entradas'
        entradas = controlador_juego.procesar_entradas()
        
        # 5. Actualizar Estado (Modelo)
        # El modelo actualiza su estado interno basado en las entradas
        estado_juego.actualizar_estado(entradas, delta_tiempo)
        
        # 6. Dibujar (Vista)
        # La vista dibuja la pantalla basandose en el estado actual del modelo
        vista_juego.dibujar(estado_juego)

    # 7. Limpiar al salir
    vista_juego.cerrar()
    
    
    print("\n¡Gracias por jugar!\n")
  

if __name__ == "__main__":
    main()