import json
import os

def debug_ciclos(ciclos, debug_filename="debug_ciclos.txt"):
    """
    Guarda la información de los ciclos en un archivo legible.
    ciclos: lista de diccionarios, tal como devuelve detectar_ciclos
    """
    debug_path = os.path.abspath(debug_filename)

    # Convertimos valores de tipo NumPy a nativos de Python
    ciclos_serializable = []
    for c in ciclos:
        c_copy = {}
        for k, v in c.items():
            try:
                if hasattr(v, "tolist"):
                    c_copy[k] = v.tolist()  # arrays numpy a listas
                else:
                    c_copy[k] = v
            except Exception:
                c_copy[k] = str(v)
        ciclos_serializable.append(c_copy)

    # Escribimos en JSON con indentación
    with open(debug_path, "w", encoding="utf-8") as f:
        f.write(f"Número de ciclos detectados: {len(ciclos)}\n\n")
        f.write(json.dumps(ciclos_serializable, indent=2, ensure_ascii=False))

    print(f"[DEBUG] Ciclos guardados en {debug_path}")