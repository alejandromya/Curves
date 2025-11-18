import csv

def detectar_separador(filename, n=5):
    """Intenta detectar automáticamente el separador CSV."""
    with open(filename, "r", encoding="latin1") as f:
        snippet = "".join([f.readline() for _ in range(n)])
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(snippet)
        return dialect.delimiter
    except:
        return ";"  # por defecto
