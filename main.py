import numpy as np # Recomendado para manejar el tablero, aunque puedes usar listas de listas
import random
import math
import copy

# --- Constantes del Juego ---
FILAS = 6
COLUMNAS = 7
JUGADOR_HUMANO = "H"
JUGADOR_IA = "AI"
JUGADOR_RANDOM = "R" # El "jugador base" que toma decisiones aleatorias 
VACIO = " "

# --- Clase Ficha (Requerida ) ---
# En este diseño simple, la "ficha" puede ser solo un string (como "H" o "AI")
# Si quisieras, podrías hacerla una clase, pero puede ser innecesario.
# class Ficha:
#     def __init__(self, color):
#         self.color = color

# --- Clase Jugador (Requerida ) ---
class Jugador:
    """Representa a un jugador (humano o agente)."""
    def __init__(self, tipo_jugador, ficha):
        self.tipo_jugador = tipo_jugador # "H", "AI", "R"
        self.ficha = ficha # La marca que usa, ej: "X" u "O"

    # --- Heurística: Evaluar el estado del tablero ---
    def evaluar_ventana(self, ventana, ficha):
        """Asigna un puntaje a una ventana de 4 celdas."""
        score = 0
        oponente = "O" if ficha == "X" else "X" # Asumiendo X vs O

        if ventana.count(ficha) == 4:
            score += 100
        elif ventana.count(ficha) == 3 and ventana.count(VACIO) == 1:
            score += 5
        elif ventana.count(ficha) == 2 and ventana.count(VACIO) == 2:
            score += 2

        # Estrategia defensiva: Bloquear al oponente es prioritario
        if ventana.count(oponente) == 3 and ventana.count(VACIO) == 1:
            score -= 4 

        return score

    def evaluar_posicion(self, tablero, ficha):
        """Calcula el puntaje total del tablero actual."""
        score = 0
        grid = tablero.grid
        
        # Preferencia por el centro (Estratégico en Connect 4)
        col_centro = [grid[i][COLUMNAS//2] for i in range(FILAS)]
        cuenta_centro = col_centro.count(ficha)
        score += cuenta_centro * 3

        # Horizontal
        for r in range(FILAS):
            fila_array = [i for i in list(grid[r, :])]
            for c in range(COLUMNAS - 3):
                ventana = fila_array[c:c+4]
                score += self.evaluar_ventana(ventana, self.ficha)

        # Vertical
        for c in range(COLUMNAS):
            col_array = [i for i in list(grid[:, c])]
            for r in range(FILAS - 3):
                ventana = col_array[r:r+4]
                score += self.evaluar_ventana(ventana, self.ficha)

        # Diagonal Positiva
        for r in range(FILAS - 3):
            for c in range(COLUMNAS - 3):
                ventana = [grid[r+i][c+i] for i in range(4)]
                score += self.evaluar_ventana(ventana, self.ficha)

        # Diagonal Negativa
        for r in range(FILAS - 3):
            for c in range(COLUMNAS - 3):
                ventana = [grid[r+3-i][c+i] for i in range(4)]
                score += self.evaluar_ventana(ventana, self.ficha)

        return score
    
    # --- Algoritmo Minimax + Alpha-Beta + Memoización ---
    def es_nodo_terminal(self, tablero):
        # Revisa si alguien ganó o si el tablero está lleno
        # Nota: Usamos una lógica simplificada de victoria aquí o llamamos a la del tablero
        # Para optimizar, idealmente la clase Tablero debería tener un check_win global
        # pero aquí lo inferimos si no hay movimientos validos o detectamos victoria.
        return tablero.detectar_victoria("X", 0, 0) or \
               tablero.detectar_victoria("O", 0, 0) or \
               len(tablero.obtener_columnas_validas()) == 0

    def minimax(self, tablero, profundidad, alpha, beta, maximizando):
        # 1. Generar clave para Memoización (Hash del tablero)
        # Convertimos el numpy array a tupla para que sea "hasheable"
        estado_hash = (str(tablero.grid), maximizando)
        
        if hasattr(self, 'memo') and estado_hash in self.memo:
            return self.memo[estado_hash]

        valid_locations = tablero.obtener_columnas_validas()
        es_terminal = self.es_nodo_terminal(tablero) # Ojo: detectar_victoria requiere refactor si no se tiene ultima jugada

        # 2. Casos Base (Fin del juego o Profundidad 0)
        if profundidad == 0 or es_terminal:
            if es_terminal:
                if tablero.detectar_victoria(self.ficha, 0, 0): # IA Gana
                    # PREMIO POR GANAR RÁPIDO: Sumamos la profundidad restante
                    return (None, 100000000000000 + profundidad) 
                
                elif tablero.detectar_victoria("O" if self.ficha=="X" else "X", 0, 0): # IA Pierde
                    # CASTIGO POR PERDER: Restamos profundidad para intentar "alargar" la derrota
                    # (Preferimos perder en 5 turnos que en 1)
                    return (None, -100000000000000 - profundidad) 
                else: # Empate
                    return (None, 0)
            else: # Profundidad 0
                return (None, self.evaluar_posicion(tablero, self.ficha))

        # 3. Parte Recursiva
        if maximizando:
            value = -math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                # Simular jugada
                temp_tablero = copy.deepcopy(tablero)
                fila = temp_tablero.insertar_ficha(col, self.ficha)
                
                # Verificar victoria in-situ para el caso base correcto arriba
                if temp_tablero.detectar_victoria(self.ficha, fila, col):
                    # AQUÍ TAMBIÉN: Sumar profundidad
                    # Nota: Aquí la profundidad es la actual, no profundidad-1
                    score = 100000000000000 + profundidad 
                else:
                    new_score = self.minimax(temp_tablero, profundidad-1, alpha, beta, False)[1]
                    score = new_score

                if score > value:
                    value = score
                    column = col
                
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            
            # Guardar en Memo
            if not hasattr(self, 'memo'): self.memo = {}
            self.memo[estado_hash] = (column, value)
            return column, value

        else: # Minimizando (Turno del oponente)
            value = math.inf
            column = random.choice(valid_locations)
            oponente = "O" if self.ficha == "X" else "X"
            
            for col in valid_locations:
                temp_tablero = copy.deepcopy(tablero)
                fila = temp_tablero.insertar_ficha(col, oponente)

                if temp_tablero.detectar_victoria(oponente, fila, col):
                    score = -100000000000000 - profundidad
                else:
                    new_score = self.minimax(temp_tablero, profundidad-1, alpha, beta, True)[1]
                    score = new_score

                if score < value:
                    value = score
                    column = col
                
                beta = min(beta, value)
                if alpha >= beta:
                    break
            
            if not hasattr(self, 'memo'): self.memo = {}
            self.memo[estado_hash] = (column, value)
            return column, value

    def elegir_columna(self, tablero):
        """
        El jugador decide en qué columna soltar la ficha.
        """
        if self.tipo_jugador == JUGADOR_HUMANO:
            # Lógica para que el jugador humano  elija
            while True:
                try:
                    col = int(input(f"Turno de {self.ficha}. Elige columna (0-{COLUMNAS-1}): "))
                    if 0 <= col < COLUMNAS and tablero.es_columna_valida(col):
                        return col
                    else:
                        print("Columna inválida o llena. Intenta de nuevo.")
                except ValueError:
                    print("Entrada inválida. Ingresa un número.")
        
        elif self.tipo_jugador == JUGADOR_RANDOM:
            # Lógica para el jugador aleatorio 
            # (Esta es tu baseline 1)
            import random
            col = random.choice(tablero.obtener_columnas_validas())
            print(f"Jugador Aleatorio ({self.ficha}) eligió columna {col}")
            return col

        elif self.tipo_jugador == JUGADOR_IA:
            print(f"Agente IA ({self.ficha}) está pensando...")
            
            # Inicializar memoización para este turno (o mantenerla global si prefieres)
            self.memo = {} 
            
            # Profundidad: 4 es rápido, 6 es fuerte, 7+ puede ser lento en Python
            profundidad = 4 
            
            columna_elegida, minimax_score = self.minimax(tablero, profundidad, -math.inf, math.inf, True)
            
            if columna_elegida is None:
                # Fallback por si acaso falla
                print("Fallback: IA no encontró columna, eligiendo aleatoriamente.")
                columna_elegida = random.choice(tablero.obtener_columnas_validas())
            
            print(f"IA eligió columna {columna_elegida} con puntaje {minimax_score}")
            return columna_elegida


# --- Clase Tablero (Requerida ) ---
class Tablero:
    """Maneja el estado y la lógica del tablero 6x7."""
    def __init__(self):
        # Creamos un tablero de 6 filas x 7 columnas
        self.grid = np.full((FILAS, COLUMNAS), VACIO)

    def imprimir_tablero(self):
        """Imprime el tablero en la consola."""
        # Volteamos el tablero para que la fila 0 sea la de abajo
        print("\n  0 1 2 3 4 5 6")
        print("-----------------")
        for fila in np.flip(self.grid, axis=0):
            print(f"| {' '.join(fila)} |")
        print("-----------------")

    def es_columna_valida(self, col):
        """Revisa si la columna superior (fila 5) está vacía."""
        return self.grid[FILAS-1][col] == VACIO

    def obtener_columnas_validas(self):
        """Devuelve una lista de todas las columnas no llenas."""
        validas = []
        for col in range(COLUMNAS):
            if self.es_columna_valida(col):
                validas.append(col)
        return validas

    def insertar_ficha(self, col, ficha):
        """Inserta una ficha en la columna dada."""
        #  "manejando lógica de inserción"
        for fila in range(FILAS):
            if self.grid[fila][col] == VACIO:
                self.grid[fila][col] = ficha
                return fila # Devuelve la fila donde se insertó (útil para detectar victoria)
        return -1 # Esto no debería pasar si se usa es_columna_valida

    def detectar_victoria(self, ficha, ultima_fila, ultima_col):
        """
        Revisa si la última jugada (ficha) resultó en una victoria.
         "detección de victoria"
        """
        
        # 1. Revisar Horizontal
        for c in range(max(0, ultima_col - 3), min(COLUMNAS - 3, ultima_col + 1)):
            if all(self.grid[ultima_fila][c+i] == ficha for i in range(4)):
                return True

        # 2. Revisar Vertical
        # (Solo necesitas revisar hacia abajo desde la ficha insertada)
        if ultima_fila >= 3: # Solo si hay espacio para 4 en línea vertical
            if all(self.grid[ultima_fila-i][ultima_col] == ficha for i in range(4)):
                return True

        # 3. Revisar Diagonal Positiva ( / )
        for f in range(max(0, ultima_fila - 3), min(FILAS - 3, ultima_fila + 1)):
            c_start = ultima_col - (ultima_fila - f)
            if 0 <= c_start <= COLUMNAS - 4:
                if all(self.grid[f+i][c_start+i] == ficha for i in range(4)):
                    return True

        # 4. Revisar Diagonal Negativa ( \ )
        for f in range(max(0, ultima_fila - 3), min(FILAS - 3, ultima_fila + 1)):
            c_start = ultima_col + (ultima_fila - f)
            if 3 <= c_start < COLUMNAS:
                if all(self.grid[f+i][c_start-i] == ficha for i in range(4)):
                    return True
        
        return False

    def esta_lleno(self):
        """Revisa si el tablero está lleno (empate)."""
        return len(self.obtener_columnas_validas()) == 0


# --- Clase Juego (Controlador) ---
class JuegoConnect4:
    """Orquesta el flujo completo del juego."""
    def __init__(self, jugador1, jugador2):
        self.tablero = Tablero()
        self.jugador1 = jugador1
        self.jugador2 = jugador2
        self.jugadores = {jugador1.ficha: jugador1, jugador2.ficha: jugador2}
        self.turno_actual = jugador1.ficha # Empezamos con el jugador 1

    def cambiar_turno(self):
        if self.turno_actual == self.jugador1.ficha:
            self.turno_actual = self.jugador2.ficha
        else:
            self.turno_actual = self.jugador1.ficha

    def iniciar_juego(self):
        """Bucle principal del juego."""
        game_over = False
        self.tablero.imprimir_tablero()

        while not game_over:
            jugador_actual = self.jugadores[self.turno_actual]
            
            # 1. Jugador elige columna
            col = jugador_actual.elegir_columna(self.tablero)
            
            # 2. Insertar ficha
            fila = self.tablero.insertar_ficha(col, jugador_actual.ficha)
            
            # 3. Imprimir estado
            self.tablero.imprimir_tablero()

            # 4. Revisar victoria
            if self.tablero.detectar_victoria(jugador_actual.ficha, fila, col):
                print(f"🎉 ¡El jugador {jugador_actual.ficha} ({jugador_actual.tipo_jugador}) ha ganado!")
                game_over = True
            
            # 5. Revisar empate
            elif self.tablero.esta_lleno():
                print("🤝 ¡Es un empate!")
                game_over = True
            
            # 6. Cambiar turno
            else:
                self.cambiar_turno()


# --- Punto de Entrada Principal ---
if __name__ == "__main__":
    
    # --- Configuración para la prueba ---
    # Para cumplir con la Fase de Resultados, necesitas 3 tipos de partidas:
    
    # 1. Agente DP vs. Jugador Aleatorio 
    # j1 = Jugador(JUGADOR_IA, "X")
    # j2 = Jugador(JUGADOR_RANDOM, "O")

    # 2. Agente DP vs. Jugador Humano 
    j2 = Jugador(JUGADOR_IA, "X")
    j1 = Jugador(JUGADOR_HUMANO, "O")

    # 3. Jugador Humano vs. Jugador Aleatorio (para tu propia prueba)
    # j1 = Jugador(JUGADOR_HUMANO, "X")
    # j2 = Jugador(JUGADOR_RANDOM, "O")
    
    # Iniciar el juego
    juego = JuegoConnect4(j1, j2)
    juego.iniciar_juego()