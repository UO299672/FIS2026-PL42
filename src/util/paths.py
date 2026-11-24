import os

# Raíz del proyecto (carpeta que contiene resources/ y src/)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carpeta donde se guardan los ficheros generados por la aplicación (remesas, etc.)
OUTPUT_DIR = os.path.join(ROOT_DIR, "outputs")
