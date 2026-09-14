#!/usr/bin/env python3
"""
Alta y baja de usuarios del panel. No hay registro público: las cuentas
se crean desde el servidor con este script.

    python3 admin/usuarios.py listar
    python3 admin/usuarios.py agregar nacho
    python3 admin/usuarios.py password nacho
    python3 admin/usuarios.py borrar nacho
"""

import os
import sys
import getpass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seguridad as S

MINIMO = 12


def pedir_password(usuario):
    while True:
        p1 = getpass.getpass(f"Contraseña para «{usuario}»: ")
        if len(p1) < MINIMO:
            print(f"  Muy corta: tiene que tener al menos {MINIMO} caracteres.")
            continue
        if p1 != getpass.getpass("Repetila: "):
            print("  No coinciden, probá de nuevo.")
            continue
        return p1


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    accion = sys.argv[1]
    usuarios = S.cargar_usuarios()

    if accion == "listar":
        if not usuarios:
            print("No hay usuarios todavía. Creá uno con:  python3 admin/usuarios.py agregar <usuario>")
        for u, d in sorted(usuarios.items()):
            print(f"  {u:20} {d.get('nombre', '')}")
        return 0

    if len(sys.argv) < 3:
        print("Falta el nombre de usuario.")
        return 1
    usuario = sys.argv[2].strip().lower()

    if accion == "agregar":
        if usuario in usuarios:
            print(f"«{usuario}» ya existe. Para cambiarle la clave usá:  password {usuario}")
            return 1
        nombre = input("Nombre para mostrar (ej. Nacho): ").strip() or usuario
        usuarios[usuario] = {"nombre": nombre, "hash": S.crear_hash(pedir_password(usuario))}
        S.guardar_usuarios(usuarios)
        print(f"✓ Usuario «{usuario}» creado.")
        return 0

    if accion == "password":
        if usuario not in usuarios:
            print(f"«{usuario}» no existe.")
            return 1
        usuarios[usuario]["hash"] = S.crear_hash(pedir_password(usuario))
        S.guardar_usuarios(usuarios)
        print(f"✓ Contraseña de «{usuario}» actualizada.")
        return 0

    if accion == "borrar":
        if usuario not in usuarios:
            print(f"«{usuario}» no existe.")
            return 1
        if len(usuarios) == 1:
            print("Es el único usuario: si lo borrás te quedás afuera del panel.")
            return 1
        usuarios.pop(usuario)
        S.guardar_usuarios(usuarios)
        print(f"✓ Usuario «{usuario}» eliminado.")
        return 0

    print(f"Acción desconocida: {accion}")
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
