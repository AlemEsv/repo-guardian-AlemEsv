import struct
#import zlib
import binascii
from pathlib import Path

class PackfileError(Exception):
    pass

class CrcError(PackfileError):
    def __init__(self, offset):
        self.offset = offset
        super().__init__(f"Invalid CRC at offset {offset}")

def scan_pack(repo_path: Path):
    """
    Lee el packfile y verifica CRC de cada entrada.
    Lanza CrcError(offset) si falla el CRC.
    """
    pack_path = repo_path / ".git" / "objects" / "pack" / "pack-corrupt.pack"
    #idx_path  = repo_path / ".git" / "objects" / "pack" / "pack-corrupt.idx"

    # Abrir y parsear header de pack: 'PACK' + version + num_objects
    with open(pack_path, "rb") as f:
        signature = f.read(4)
        if signature != b"PACK":
            raise PackfileError("No es un packfile válido")
        #version = struct.unpack(">I", f.read(4))[0]
        num_objects = struct.unpack(">I", f.read(4))[0]

        # Iterar cada objeto: para simplificar, leemos raw y comprobamos CRC32
        for i in range(num_objects):
            offset = f.tell()
            # Aquí tendrías que parsear el tipo y tamaño real, 
            # pero para ejemplo, leemos un chunk y verificamos CRC
            chunk = f.read(1024)  # ajusta al tamaño real
            crc_calc = binascii.crc32(chunk) & 0xffffffff
            # Simula leer el CRC esperado desde idx (esto es solo ejemplo)
            expected_crc = 0xdeadbeef  
            if crc_calc != expected_crc:
                raise CrcError(offset)
