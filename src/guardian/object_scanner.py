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
        ValueError: Si el archivo está corrupto, el tamaño no coincide o el encabezado es inválido.
        FileNotFoundError: Si el archivo no existe.
        zlib.error: Si el archivo no puede descomprimirse.
    """
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")

    with path.open('rb') as f:
        compressed = f.read()

    decompressed = zlib.decompress(compressed)

    header, _, content = decompressed.partition(b'\x00')
    try:
        type_str, size_str = header.decode().split()
        size = int(size_str)
    except Exception as e:
        raise ValueError("Encabezado inválido") from e

    if len(content) != size:
        raise ValueError("Tamaño del contenido incorrecto")

    sha = hashlib.sha1()
    sha.update(header + b"\x00" + content)
    digest = sha.hexdigest()

    return GitObject(
        type=type_str,
        size=size,
        content=content,
        hash=digest
    )
