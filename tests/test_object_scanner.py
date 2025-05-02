# tests/test_object_scanner.py
import pytest
import zlib
import hashlib
from pathlib import Path
from src.guardian.object_scanner import read_loose, GitObject

# Helper para crear un loose object válido en tmp_path
def make_loose(tmp_path: Path, type_str: str, content: bytes) -> Path:
    header = f"{type_str} {len(content)}\0".encode()
    data = header + content
    compressed = zlib.compress(data)
    # Calculamos el hash que Git usaría (sha1 de data)
    sha = hashlib.sha1(data).hexdigest()
    # Simulamos la estructura .git/objects/xx/yyyy…  
    obj_dir = tmp_path / "objects" / sha[:2]
    obj_dir.mkdir(parents=True)
    obj_path = obj_dir / sha[2:]
    obj_path.write_bytes(compressed)
    return obj_path

def test_read_loose_valid(tmp_path):
    content = b"hola mundo"
    path = make_loose(tmp_path, "blob", content)
    obj = read_loose(path)
    assert isinstance(obj, GitObject)
    assert obj.type == "blob"
    assert obj.size == len(content)
    assert obj.content == content
    # Verificamos que el hash corresponde
    expected_hash = hashlib.sha1((f"blob {len(content)}\0").encode() + content).hexdigest()
    assert obj.hash == expected_hash

def test_read_loose_invalid_size(tmp_path):
    # Creamos un header con tamaño erróneo
    content = b"1234"
    header = b"blob 10\0"  # tamaño declarado 10 pero len(content)=4
    compressed = zlib.compress(header + content)
    path = tmp_path / "invalid_size"
    path.write_bytes(compressed)
    with pytest.raises(ValueError, match="Tamaño del contenido incorrecto"):
        read_loose(path)

def test_read_loose_invalid_header(tmp_path):
    # Header sin el formato "type size\0"
    bad_header = b"malformed-header\0contenido"
    compressed = zlib.compress(bad_header)
    path = tmp_path / "bad_header"
    path.write_bytes(compressed)
    with pytest.raises(ValueError, match="Encabezado inválido"):
        read_loose(path)

def test_read_loose_decompression_error(tmp_path):
    # Archivo que no es válido zlib
    path = tmp_path / "not_compressed"
    path.write_bytes(b"no es zlib")
    with pytest.raises(zlib.error):
        read_loose(path)

def test_read_loose_file_not_found(tmp_path):
    # Ruta inexistente
    missing = tmp_path / "no_exist"
    with pytest.raises(FileNotFoundError):
        read_loose(missing)
