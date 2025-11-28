import time
import math
import matplotlib.pyplot as plt

from back_end import Tablero, Jugador, JUGADOR_IA, VACIO

def benchmark_profundidad(max_depth=8):
    """
    Mide cuánto tarda la IA en decidir el primer movimiento 
    para diferentes niveles de profundidad.
    """
    print(f"--- Iniciando Benchmark de Profundidad (1 a {max_depth}) ---")
    print("Nota: El algoritmo Minimax tiene complejidad exponencial.")
    print("Profundidades > 6 pueden tomar MUCHO tiempo en Python puro.\n")

    tiempos = []
    profundidades = range(1, max_depth + 1)
    
    # Preparamos el jugador
    jugador_ia = Jugador(JUGADOR_IA, "X")

    print(f"{'Profundidad':<12} | {'Tiempo (segundos)':<20} | {'Nodos/Acción'}")
    print("-" * 50)

    for depth in profundidades:
        # Crear un tablero limpio para cada prueba
        tablero = Tablero()
        
        #Limpiar la memoria (memoization) 
        if hasattr(jugador_ia, 'memo'):
            jugador_ia.memo = {}

        # Medir tiempo
        start_time = time.time()
        
        # Llamamos minimax
        columna, score = jugador_ia.minimax(tablero, depth, -math.inf, math.inf, True)
        
        end_time = time.time()
        duracion = end_time - start_time
        
        tiempos.append(duracion)
        
        print(f"{depth:<12} | {duracion:.5f} s {'':<11} | Completado")

    return list(profundidades), tiempos

def graficar_resultados(x, y):
    """Genera y guarda el gráfico de líneas."""
    plt.figure(figsize=(10, 6))
    
    # Plot principal
    plt.plot(x, y, marker='o', linestyle='-', color='b', linewidth=2, label='Minimax con Poda Alpha-Beta')
    
    # Configuración del gráfico
    plt.title('Análisis de Complejidad: Tiempo de Ejecución vs Profundidad', fontsize=14)
    plt.xlabel('Profundidad del Árbol de Búsqueda (Depth)', fontsize=12)
    plt.ylabel('Tiempo de Respuesta (segundos)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(x) 
    
    # Anotaciones de valores
    for i, txt in enumerate(y):
        plt.annotate(f"{txt:.2f}s", (x[i], y[i]), textcoords="offset points", xytext=(0,10), ha='center')

    plt.legend()
    
    # Guardar imagen
    filename = "benchmark_profundidad.png"
    plt.savefig(filename)
    print(f"\n[Éxito] Gráfico guardado como '{filename}'")
    plt.show()

if __name__ == "__main__":
    profundidades, tiempos = benchmark_profundidad(max_depth=10)
    
    if len(tiempos) > 0:
        graficar_resultados(profundidades, tiempos)
