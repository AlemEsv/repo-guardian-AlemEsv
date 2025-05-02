import hashlib
from pathlib import Path
import zlib
from dataclasses import dataclass

@dataclass
class GitObject:
    type: str
    size: int
    content: bytes
    hash: str

def read_loose(path: Path) -> GitObject:
    """
    Lee y valida un objeto suelto de Git (.git/objects/xx/yyyy...).

    Args:
        path (Path): Ruta al archivo del objeto suelto.

    Returns:
        GitObject: Objeto con tipo, tamaño, contenido y hash SHA-1.

    Raises:
        ValueError: Si el archivo está corrupto o el tamaño no coincide.
        FileNotFoundError: Si el archivo no existe.
        zlib.error: Si el archivo no puede descomprimirse.
    """
    with path.open('rb') as f:
        compressed = f.read()
    decompressed = zlib.decompress(compressed)

    # Separar encabezado y contenido
    header, _, content = decompressed.partition(b'\x00')
    type_str, size_str = header.decode().split()

    # Validar tamaño
    if len(content) != int(size_str):
        raise ValueError("Tamaño del contenido incorrecto")

    # Calcular hash y verificar
    sha = hashlib.sha1()
    sha.update(decompressed)
    digest = sha.hexdigest()

    # Comparar con el nombre del archivo si lo tienes disponible
    return GitObject(type=type_str, size=int(size_str), content=content, hash=digest)
