import numpy as np # Recomendado para manejar el tablero, aunque puedes usar listas de listas

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
            # ⭐ AQUÍ VA TU LÓGICA DE PROGRAMACIÓN DINÁMICA (DP) ⭐
            # Esta es la parte central del proyecto 
            # Implementarás Minimax con memoización.
            print(f"Agente IA ({self.ficha}) está pensando...")
            # (Por ahora, podemos hacer que se comporte como el aleatorio)
            import random
            col = random.choice(tablero.obtener_columnas_validas())
            return col


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
            if 0 <= c_start <= COLUMNAS - 4:
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


# # --- Punto de Entrada Principal ---
# if __name__ == "__main__":
    
#     # --- Configuración para la prueba ---
#     # Para cumplir con la Fase de Resultados, necesitas 3 tipos de partidas:
    
#     # 1. Agente DP vs. Jugador Aleatorio 
#     # j1 = Jugador(JUGADOR_IA, "X")
#     # j2 = Jugador(JUGADOR_RANDOM, "O")

#     # 2. Agente DP vs. Jugador Humano 
#     j1 = Jugador(JUGADOR_IA, "X")
#     j2 = Jugador(JUGADOR_HUMANO, "O")

#     # 3. Jugador Humano vs. Jugador Aleatorio (para tu propia prueba)
#     # j1 = Jugador(JUGADOR_HUMANO, "X")
#     # j2 = Jugador(JUGADOR_RANDOM, "O")
    
#     # Iniciar el juego
#     juego = JuegoConnect4(j1, j2)
#     juego.iniciar_juego()