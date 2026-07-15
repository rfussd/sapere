"""
DIA 4 — Diccionarios y while loops
══════════════════════════════════════════

OBJETIVO: Pares clave-valor y repeticion condicional.
"""

# ═══════════════════════════════════════════════════════════
# PARTE 1 — Diccionarios: clave → valor
# ═══════════════════════════════════════════════════════════

# Piensa en un diccionario como una agenda:
# nombre (clave) → telefono (valor)

estudiante = {
    "nombre": "Rafael",
    "edad": 18,
    "carrera": "Ing. Informatica",
    "promedio": 9.2,
    "activo": True,
}

print(estudiante["nombre"])       # Rafael
print(estudiante["edad"])         # 18
print(estudiante.get("escuela", "IPN"))  # IPN (valor default si no existe)

# Agregar y modificar
estudiante["semestre"] = 1        # Nuevo
estudiante["edad"] = 19           # Modificar
del estudiante["promedio"]        # Eliminar

print(estudiante)

# ═══════════════════════════════════════════════════════════
# PARTE 2 — Recorrer diccionarios
# ═══════════════════════════════════════════════════════════

for clave in estudiante:
    print(f"{clave}: {estudiante[clave]}")

# O mas elegante:
for clave, valor in estudiante.items():
    print(f"{clave} → {valor}")

# Solo claves o solo valores
print(estudiante.keys())    # dict_keys(['nombre', 'edad', ...])
print(estudiante.values())  # dict_values(['Rafael', 19, ...])

# EJERCICIO 1: Crea un diccionario con datos de tu materia favorita
# (nombre, profesor, creditos, aprobada). Imprime todo con .items()
# ──────────── (escribe aqui) ────────────


# ═══════════════════════════════════════════════════════════
# PARTE 3 — while: repetir mientras se cumpla condicion
# ═══════════════════════════════════════════════════════════

contador = 1
while contador <= 5:
    print(f"Vuelta {contador}")
    contador += 1   # contador = contador + 1

# ⚠ CUIDADO: si la condicion nunca se vuelve False,
# el while se vuelve INFINITO. Siempre asegurate de modificar
# algo que eventualmente haga la condicion falsa.

# While con input (el clasico)
# secreto = "python"
# intento = ""
# while intento != secreto:
#     intento = input("Adivina la palabra secreta: ")
# print("Correcto!")

# EJERCICIO 2: Usa while para imprimir los numeros del 10 al 1
# en cuenta regresiva.
# ──────────── (escribe aqui) ────────────


# ═══════════════════════════════════════════════════════════
# PARTE 4 — break y continue
# ═══════════════════════════════════════════════════════════

# break: sale del ciclo inmediatamente
for i in range(10):
    if i == 5:
        break      # Salir al llegar a 5
    print(i)        # Imprime 0, 1, 2, 3, 4

# continue: salta a la siguiente iteracion
for i in range(5):
    if i == 2:
        continue   # Saltar el 2
    print(i)        # Imprime 0, 1, 3, 4

# ═══════════════════════════════════════════════════════════
# DESAFIO DEL DIA 4
# ═══════════════════════════════════════════════════════════
# Crea un sistema de calificaciones:
# 1. Usa un diccionario: {"Juan": 8, "Ana": 9, "Pedro": 6, ...}
# 2. Con un while, deja que el usuario consulte calificaciones
#    (escribe el nombre, muestra la nota)
# 3. Si escribe "salir", termina el programa
# 4. Si el nombre no existe, muestra "No encontrado"
# 5. Usa break para salir

# ──────────── (escribe aqui) ────────────
