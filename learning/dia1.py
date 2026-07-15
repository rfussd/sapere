"""
DIA 1 — Variables, Tipos de Datos, print(), input(), Strings
═══════════════════════════════════════════════════════════

OBJETIVO: Al final de este archivo, vas a poder escribir
programas simples que interactuen con el usuario.

INSTRUCCIONES:
  Lee, ejecuta el codigo, y luego resuelve los ejercicios.
  Para ejecutar: py learning/dia1.py
"""

# ═══════════════════════════════════════════════════════════
# PARTE 1 — print(): mostrar cosas en pantalla
# ═══════════════════════════════════════════════════════════

print("Hola, mundo!")
print(42)
print(3.14)
print(True)
print("Mi nombre es", "Juan", "y tengo", 18, "anios")
print()  # linea vacia

# EJERCICIO 1: Escribe un print que muestre tu nombre, edad y escuela
# (borra esta linea y escribe tu print aqui)

# ═══════════════════════════════════════════════════════════
# PARTE 2 — Variables: guardar informacion
# ═══════════════════════════════════════════════════════════
# Piensa en una variable como una CAJA con un nombre
# que guarda un valor.

nombre = "Rafael"
edad = 18
altura = 1.75
estudiante = True

print(nombre, "tiene", edad, "anios")
print("Altura:", altura, "metros")
print("Es estudiante?", estudiante)

# Las variables se pueden cambiar
edad = 19
print("Nueva edad:", edad)

# Y se pueden usar para calcular
anio_nacimiento = 2026 - edad
print("Naciste en:", anio_nacimiento)

# REGLAS para nombres de variables:
# ✅ nombre, edad_actual, usuario2, _privado
# ❌ 2usuario, mi-nombre, class, for (palabras reservadas)
# usa snake_case: todo_minusculas_con_guiones_bajos

# EJERCICIO 2: Crea 4 variables sobre ti (nombre, edad, ciudad, hobby)
# y muestralas con print
# ──────────── (escribe aqui) ────────────


# ═══════════════════════════════════════════════════════════
# PARTE 3 — Tipos de datos en Python
# ═══════════════════════════════════════════════════════════

# Python tiene tipos basicos:
texto = "Hola"          # str  — cadenas de texto (strings)
entero = 42             # int  — numeros enteros
decimal = 3.14          # float — numeros con decimales
verdad = True           # bool — True o False (con mayuscula!)
nada = None             # NoneType — "vacio", "nada"

# Puedes saber el tipo con type():
print(type(texto))      # <class 'str'>
print(type(entero))     # <class 'int'>
print(type(decimal))    # <class 'float'>
print(type(verdad))     # <class 'bool'>
print(type(nada))       # <class 'NoneType'>

# ═══════════════════════════════════════════════════════════
# PARTE 4 — Strings (cadenas de texto)
# ═══════════════════════════════════════════════════════════

# Se pueden escribir con comillas simples o dobles
saludo = "Hola"
despedida = 'Adios'

# Para texto largo, usa triple comillas
mensaje_largo = """Esto es un texto
de varias lineas
sin problemas."""

print(mensaje_largo)

# Concatenar (pegar) strings:
nombre_completo = "Rafael" + " " + "Garcia"
print(nombre_completo)

# f-strings: la forma mas FACIL de combinar texto y variables
edad = 18
print(f"Tengo {edad} anios y en 5 tendre {edad + 5}")
print(f"Hola {nombre}, tu altura es {altura}m")

# Metodos utiles de strings:
texto = "  Hola Mundo Python  "
print(texto.upper())       # HOLA MUNDO PYTHON
print(texto.lower())       # hola mundo python
print(texto.strip())       # Quita espacios al inicio y final
print(texto.replace("Mundo", "Universo"))  # Reemplaza
print(len(texto))          # Cuantos caracteres tiene

# EJERCICIO 3: Crea una variable con tu frase favorita.
# Muestrala en mayusculas, cuenta sus caracteres, y reemplaza
# una palabra por otra.
# ──────────── (escribe aqui) ────────────


# ═══════════════════════════════════════════════════════════
# PARTE 5 — input(): preguntar al usuario
# ═══════════════════════════════════════════════════════════

# input() pausa el programa y espera que escribas algo
# ¡DESCOMENTA estas lineas para probar! (quita el # al inicio)

# user_name = input("Como te llamas? ")
# print(f"Hola, {user_name}!")

# IMPORTANTE: input() SIEMPRE devuelve texto (string).
# Si necesitas un numero, conviertelo:

# edad_str = input("Cuantos anios tienes? ")
# edad_num = int(edad_str)           # Convierte "18" a 18
# print(f"En 10 anios tendras {edad_num + 10}")

# EJERCICIO 4: Pregunta al usuario su nombre, edad y ciudad.
# Luego muestra: "Hola [nombre], tienes [edad] anios y vives en [ciudad]"
# ──────────── (escribe aqui) ────────────


# ═══════════════════════════════════════════════════════════
# DESAFIO DEL DIA 1
# ═══════════════════════════════════════════════════════════
# Crea un programa que:
# 1. Le de la bienvenida al usuario
# 2. Le pregunte su nombre
# 3. Le pregunte su edad
# 4. Calcule en que anio nacio (aprox: 2026 - edad)
# 5. Le pregunte su materia favorita
# 6. Muestre un resumen bonito con toda la info

# ──────────── (escribe aqui) ────────────
nombre = "___"  # cambia esto por input()
# ...


# ═══════════════════════════════════════════════════════════
# TAREA (opcional, 10 min)
# ═══════════════════════════════════════════════════════════
# Crea un nuevo archivo dia1_tarea.py con:
# - Un programa que calcule el area de un rectangulo
#   (pregunta base y altura, multiplica, muestra resultado)
# - Un programa que convierta grados Celsius a Fahrenheit
#   (formula: F = C * 9/5 + 32)
