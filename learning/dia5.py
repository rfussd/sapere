"""
DIA 5 — Funciones: def, parametros, return
══════════════════════════════════════════════

OBJETIVO: Organizar tu codigo en bloques reutilizables.
"""

# ═══════════════════════════════════════════════════════════
# PARTE 1 — Tu primera funcion
# ═══════════════════════════════════════════════════════════

def saludar():
    """Esta funcion saluda al usuario."""
    print("Hola!")
    print("Bienvenido a Python")

# Llamar la funcion
saludar()
saludar()  # Se puede llamar muchas veces

# ═══════════════════════════════════════════════════════════
# PARTE 2 — Parametros: pasar datos a la funcion
# ═══════════════════════════════════════════════════════════

def saludar_persona(nombre):
    print(f"Hola, {nombre}!")

saludar_persona("Rafael")
saludar_persona("Maria")

# Multiples parametros
def presentar(nombre, edad, ciudad):
    print(f"{nombre} tiene {edad} anios y vive en {ciudad}")

presentar("Rafa", 18, "CDMX")

# Parametros con valor por defecto
def saludar_idioma(nombre, idioma="espaniol"):
    if idioma == "espaniol":
        print(f"Hola, {nombre}!")
    elif idioma == "ingles":
        print(f"Hello, {nombre}!")
    else:
        print(f"Hi, {nombre}!")

saludar_idioma("Rafa")               # Usa "espaniol" por defecto
saludar_idioma("Rafa", "ingles")     # Pasa "ingles"

# EJERCICIO 1: Crea una funcion 'area_rectangulo(base, altura)'
# que calcule y muestre el area. Luego llamala con 5 y 10.
# ──────────── (escribe aqui) ────────────


# ═══════════════════════════════════════════════════════════
# PARTE 3 — return: devolver un resultado
# ═══════════════════════════════════════════════════════════

def sumar(a, b):
    resultado = a + b
    return resultado

suma = sumar(5, 3)
print(f"5 + 3 = {suma}")

# Se puede usar directamente
print(f"10 + 7 = {sumar(10, 7)}")

# Mas ejemplos
def es_par(numero):
    return numero % 2 == 0

print(es_par(4))   # True
print(es_par(7))   # False

def promedio(lista):
    if len(lista) == 0:
        return 0
    return sum(lista) / len(lista)

notas = [8, 9, 7, 10, 6]
print(f"Promedio: {promedio(notas)}")

# ═══════════════════════════════════════════════════════════
# PARTE 4 — Scope: variables dentro y fuera de funciones
# ═══════════════════════════════════════════════════════════

x = 10   # Variable GLOBAL (fuera de funciones)

def cambiar():
    x = 20   # Variable LOCAL (solo existe dentro de la funcion)
    print(f"Dentro: {x}")

cambiar()          # Dentro: 20
print(f"Fuera: {x}")  # Fuera: 10 (la global NO cambio)

# EJERCICIO 2: Crea una funcion 'es_mayor_edad(edad)' que
# devuelva True si edad >= 18, False si no.
# ──────────── (escribe aqui) ────────────


# ═══════════════════════════════════════════════════════════
# PARTE 5 — Documentar funciones (docstrings)
# ═══════════════════════════════════════════════════════════

def celsius_a_fahrenheit(celsius):
    """Convierte grados Celsius a Fahrenheit.

    Args:
        celsius: temperatura en grados Celsius

    Returns:
        float: temperatura en grados Fahrenheit
    """
    return celsius * 9/5 + 32

# El docstring es lo que ves con help()
# help(celsius_a_fahrenheit)  # descomenta para probar

# ═══════════════════════════════════════════════════════════
# DESAFIO DEL DIA 5
# ═══════════════════════════════════════════════════════════
# Crea un programa con estas funciones:
#
# 1. def registrar_estudiante(nombre, edad, carrera):
#    → Devuelve un diccionario con los datos
#
# 2. def mostrar_estudiante(estudiante):
#    → Imprime los datos de forma bonita
#
# 3. def es_mayor_edad(estudiante):
#    → Devuelve True si edad >= 18
#
# 4. Un menu que pregunte que hacer:
#    [1] Registrar estudiante
#    [2] Ver estudiante
#    [3] Verificar mayoria de edad
#    [4] Salir

# ──────────── (escribe aqui) ────────────
