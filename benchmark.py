import sys
import os
import time
import matplotlib.pyplot as plt 
from back_end import Tablero, Jugador, JUGADOR_IA, JUGADOR_RANDOM, JUGADOR_HUMANO, VACIO

class SilenciarSalida:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

#  Función para simular una sola partida 
def simular_partida(id_partida):
    """
    Ejecuta una partida completa entre IA (X) y Random (O).
    Retorna: "IA", "Random" o "Empate"
    """
    # IA = "X", Random = "O"
    
    jugador_ia = Jugador(JUGADOR_IA, "X")
    jugador_random = Jugador(JUGADOR_RANDOM, "O")
    
    tablero = Tablero()
    
    # Alternar turno inicial para balancear
    turno_actual = jugador_ia if id_partida % 2 == 0 else jugador_random
    
    game_over = False
    
    while not game_over:
        # Lógica de turno (Simplificada del main original para velocidad)
        col = turno_actual.elegir_columna(tablero)
        
        # Validación de seguridad
        if col is None or not tablero.es_columna_valida(col):
            # Si la IA falla o el Random elige mal (raro), forzamos empate o derrota
            return "Error"

        fila = tablero.insertar_ficha(col, turno_actual.ficha)
        
        # Chequear victoria
        if tablero.detectar_victoria(turno_actual.ficha, fila, col):
            if turno_actual.tipo_jugador == JUGADOR_IA:
                return "IA"
            else:
                return "Random"
        
        # Chequear empate
        if tablero.esta_lleno():
            return "Empate"
            
        # Cambiar turno
        if turno_actual == jugador_ia:
            turno_actual = jugador_random
        else:
            turno_actual = jugador_ia

# Función Principal del Benchmark 
def correr_benchmark(cantidad_partidas=100):
    print(f" Iniciando Simulación de {cantidad_partidas} Partidas ")
    print("Configuración: Agente IA (Minimax) vs Agente Random")
    print("Nota: Esto puede tardar unos minutos dependiendo de la profundidad del Minimax...\n")

    resultados = {
        "IA": 0,
        "Random": 0,
        "Empate": 0,
        "Errores": 0
    }
    
    tiempo_inicio = time.time()

    for i in range(1, cantidad_partidas + 1):
        # Usamos el silenciador para que no imprima cada movimiento
        with SilenciarSalida():
            ganador = simular_partida(i)
        
        # Registrar resultado
        if ganador == "IA":
            resultados["IA"] += 1
        elif ganador == "Random":
            resultados["Random"] += 1
        elif ganador == "Empate":
            resultados["Empate"] += 1
        else:
            resultados["Errores"] += 1
            
        # Barra de progreso simple
        porcentaje = (i / cantidad_partidas) * 100
        sys.stdout.write(f"\rProgreso: [{i}/{cantidad_partidas}] - {porcentaje:.1f}% completado")
        sys.stdout.flush()

    tiempo_total = time.time() - tiempo_inicio
    print(f"\n\n Simulación Finalizada en {tiempo_total:.2f} segundos ")
    
    return resultados

#  Ejecución 
if __name__ == "__main__":
    
    N_PARTIDAS = 100
    datos = correr_benchmark(N_PARTIDAS)
    
    #  Reporte de Texto 
    print("\nRESULTADOS FINALES:")
    print(f"Victorias IA:     {datos['IA']} ({datos['IA']/N_PARTIDAS*100}%)")
    print(f"Victorias Random: {datos['Random']} ({datos['Random']/N_PARTIDAS*100}%)")
    print(f"Empates:          {datos['Empate']} ({datos['Empate']/N_PARTIDAS*100}%)")
    
    #  Generación de Gráfico 
    etiquetas = ['IA (Minimax)', 'Aleatorio', 'Empates']
    valores = [datos['IA'], datos['Random'], datos['Empate']]
    colores = ['#4CAF50', '#F44336', '#FFC107'] # Verde, Rojo, Amarillo

    plt.figure(figsize=(8, 6))
    barras = plt.bar(etiquetas, valores, color=colores)
    
    # Añadir etiquetas de valor encima de las barras
    for barra in barras:
        height = barra.get_height()
        plt.text(barra.get_x() + barra.get_width()/2., height,
                    f'{height}',
                    ha='center', va='bottom')

    plt.title(f'Rendimiento Agente IA vs Random ({N_PARTIDAS} Partidas)')
    plt.ylabel('Cantidad de Victorias')
    plt.ylim(0, N_PARTIDAS + 10)
    
    nombre_archivo = "resultados_benchmark.png"
    plt.savefig(nombre_archivo)
    print(f"\n[Éxito] Gráfico guardado como '{nombre_archivo}'.")
    plt.show()