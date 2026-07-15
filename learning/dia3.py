"""
DIA 3 — Listas y for loops
═══════════════════════════════════════

OBJETIVO: Trabajar con COLECCIONES de datos.
"""

# ═══════════════════════════════════════════════════════════
# PARTE 1 — Listas: guardar varios valores
# ═══════════════════════════════════════════════════════════

frutas = ["manzana", "banana", "naranja", "uva"]
numeros = [1, 2, 3, 4, 5]
mezclado = ["hola", 42, True, 3.14]  # Python permite tipos mezclados

print(frutas[0])       # manzana  (primer elemento, indice 0)
print(frutas[1])       # banana
print(frutas[-1])      # uva  (ultimo elemento)
print(frutas[-2])      # naranja

# Agregar y quitar elementos
frutas.append("mango")        # Agrega al final
frutas.insert(1, "pera")      # Inserta en posicion 1
frutas.remove("banana")       # Elimina por valor
ultima = frutas.pop()         # Saca el ultimo
print(frutas)
print(len(frutas))            # Cuantos elementos hay

# ═══════════════════════════════════════════════════════════
# PARTE 2 — Recorrer listas con for
# ═══════════════════════════════════════════════════════════

for fruta in frutas:
    print(f"Me gusta la {fruta}")

# range(): genera una secuencia de numeros
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 7):       # 2, 3, 4, 5, 6
    print(i)

for i in range(0, 10, 2):   # 0, 2, 4, 6, 8  (de 2 en 2)
    print(i)

# EJERCICIO 1: Crea una lista de 5 numeros. Con un for, imprime
# cada numero multiplicado por 2.
# ──────────── (escribe aqui) ────────────


# ═══════════════════════════════════════════════════════════
# PARTE 3 — Operaciones con listas
# ═══════════════════════════════════════════════════════════

numeros = [3, 1, 4, 1, 5, 9, 2, 6, 5]
print(sum(numeros))         # Suma todos
print(max(numeros))         # El mas grande
print(min(numeros))         # El mas chico
print(sorted(numeros))      # Ordenada (no modifica original)
numeros.sort()              # Ordena IN PLACE (modifica original)
print(numeros)

# Slicing: cortar pedazos de lista
letras = ["a", "b", "c", "d", "e"]
print(letras[1:3])    # ['b', 'c'] (desde 1 hasta 3 sin incluir)
print(letras[:3])     # ['a', 'b', 'c'] (primeros 3)
print(letras[2:])     # ['c', 'd', 'e'] (desde 2 hasta final)
print(letras[::-1])   # ['e', 'd', 'c', 'b', 'a'] (invertida)

# EJERCICIO 2: Crea una lista de 10 numeros. Imprime solo
# los que son PARES usando un for y un if.
# ──────────── (escribe aqui) ────────────


# ═══════════════════════════════════════════════════════════
# DESAFIO DEL DIA 3
# ═══════════════════════════════════════════════════════════
# Crea un programa que:
# 1. Pida al usuario 5 calificaciones (usa input en un for)
# 2. Las guarde en una lista
# 3. Calcule el promedio
# 4. Diga la calificacion mas alta y mas baja
# 5. Diga cuantas estan por encima del promedio

# ──────────── (escribe aqui) ────────────
