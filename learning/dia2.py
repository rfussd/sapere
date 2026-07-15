"""
DIA 2 — if/elif/else, Booleanos, Comparaciones
═══════════════════════════════════════════════════

OBJETIVO: Hacer que tu programa TOME DECISIONES.
"""

# ═══════════════════════════════════════════════════════════
# PARTE 1 — Booleanos y comparaciones
# ═══════════════════════════════════════════════════════════

# Un bool solo puede ser True o False
es_mayor = True
es_menor = False

# Comparaciones: el resultado SIEMPRE es bool
print(5 > 3)      # True
print(5 < 3)      # False
print(10 == 10)   # True   (doble igual: comparacion)
print(10 != 5)    # True   (diferente)
print(8 >= 8)     # True   (mayor o igual)
print(7 <= 6)     # False

edad = 18
print(edad > 17)          # True
print(edad == 18)         # True
print(edad != 20)         # True

# and, or, not
print(True and True)      # True (ambos)
print(True and False)     # False
print(True or False)      # True (al menos uno)
print(not True)           # False
print(edad > 15 and edad < 25)  # True

# ═══════════════════════════════════════════════════════════
# PARTE 2 — if: tomar decisiones
# ═══════════════════════════════════════════════════════════

temperatura = 30

if temperatura > 25:
    print("Hace calor")
    print("Ponte bloqueador")

# IMPORTANTE: en Python los bloques se definen con INDENTACION
# (4 espacios o 1 tab). NO con llaves {} como en otros lenguajes.

# ═══════════════════════════════════════════════════════════
# PARTE 3 — elif y else
# ═══════════════════════════════════════════════════════════

nota = 85

if nota >= 90:
    print("A — Excelente")
elif nota >= 80:
    print("B — Muy bien")
elif nota >= 70:
    print("C — Bien")
elif nota >= 60:
    print("D — Suficiente")
else:
    print("F — Reprobado")

# EJERCICIO 1: Haz un programa que pregunte la edad y diga:
# 0-12:  "Eres ninio"
# 13-17: "Eres adolescente"
# 18-64: "Eres adulto"
# 65+:   "Eres adulto mayor"
# ──────────── (escribe aqui) ────────────


# ═══════════════════════════════════════════════════════════
# PARTE 4 — if dentro de if (anidados)
# ═══════════════════════════════════════════════════════════

tiene_entrada = True
es_mayor_edad = True

if tiene_entrada:
    if es_mayor_edad:
        print("Puedes entrar al concierto y beber")
    else:
        print("Puedes entrar pero no beber")
else:
    print("No puedes entrar")

# ═══════════════════════════════════════════════════════════
# PARTE 5 — Operador ternario (if en una linea)
# ═══════════════════════════════════════════════════════════

edad = 20
mensaje = "Mayor de edad" if edad >= 18 else "Menor de edad"
print(mensaje)

# EJERCICIO 2: Escribe un ternario que diga "Par" o "Impar"
# segun un numero.
# ──────────── (escribe aqui) ────────────


# ═══════════════════════════════════════════════════════════
# DESAFIO DEL DIA 2
# ═══════════════════════════════════════════════════════════
# Crea una calculadora simple:
# 1. Pregunta dos numeros
# 2. Pregunta la operacion: +, -, *, /
# 3. Con if/elif, haz el calculo y muestra el resultado
# 4. Si la operacion no es valida, muestra error
# 5. Si dividen entre cero, muestra "No se puede dividir entre cero"

# ──────────── (escribe aqui) ────────────
