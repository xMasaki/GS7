"""Testes de validação de entrada (acessacidade_vision.validate_image_bytes)."""

from __future__ import annotations

import struct
import zlib

import cv2
import numpy as np
import pytest

from acessacidade_vision import VisionError, validate_image_bytes
from acessacidade_vision.validation import decode_image, detect_format

MB = 1024 * 1024


def _encode(img: np.ndarray, ext: str = ".jpg") -> bytes:
    ok, buf = cv2.imencode(ext, img)
    assert ok
    return buf.tobytes()


def _textured(h: int = 200, w: int = 300) -> np.ndarray:
    rng = np.random.default_rng(1)
    return rng.integers(80, 180, (h, w, 3), dtype=np.uint8)


def _png_header_only(width: int, height: int) -> bytes:
    """PNG com cabeçalho IHDR declarando dimensões arbitrárias (sem dados de imagem válidos)."""
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    chunk = b"IHDR" + ihdr
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", len(ihdr)) + chunk + struct.pack(">I", zlib.crc32(chunk))


def test_aceita_jpeg_png_webp_validos():
    img = _textured()
    for ext in (".jpg", ".png", ".webp"):
        validate_image_bytes(_encode(img, ext), 5 * MB)  # não levanta


def test_detecta_formato_pela_assinatura():
    img = _textured()
    assert detect_format(_encode(img, ".jpg")) == "JPEG"
    assert detect_format(_encode(img, ".png")) == "PNG"
    assert detect_format(_encode(img, ".webp")) == "WEBP"
    assert detect_format(b"GIF89a....") is None


def test_rejeita_arquivo_vazio():
    with pytest.raises(VisionError) as exc:
        validate_image_bytes(b"", 5 * MB)
    assert exc.value.code == "EMPTY_IMAGE"


@pytest.mark.parametrize("data", [b"isto nao e uma imagem", b"%PDF-1.7\n...", b"GIF89a\x01\x00\x01\x00"])
def test_rejeita_bytes_que_nao_sao_imagem(data):
    with pytest.raises(VisionError) as exc:
        validate_image_bytes(data, 5 * MB)
    assert exc.value.code == "UNSUPPORTED_FORMAT"
    assert "JPEG" in exc.value.message


def test_rejeita_jpeg_corrompido_com_assinatura_valida():
    data = _encode(_textured())
    corrupted = data[:20] + b"\x00" * 200  # assinatura JPEG, conteúdo inválido
    with pytest.raises(VisionError) as exc:
        validate_image_bytes(corrupted, 5 * MB)
    assert exc.value.code == "INVALID_IMAGE"


def test_rejeita_extensao_falsa():
    # texto com "extensão" de imagem: a validação olha o conteúdo, não o nome
    with pytest.raises(VisionError):
        validate_image_bytes("foto.jpg".encode() * 50, 5 * MB)


def test_rejeita_imagem_pequena():
    small = _encode(_textured(40, 40), ".png")
    with pytest.raises(VisionError) as exc:
        validate_image_bytes(small, 5 * MB)
    assert exc.value.code == "IMAGE_TOO_SMALL"
    assert "64" in exc.value.message


def test_rejeita_imagem_com_um_lado_menor_que_64():
    with pytest.raises(VisionError) as exc:
        validate_image_bytes(_encode(_textured(63, 500), ".png"), 5 * MB)
    assert exc.value.code == "IMAGE_TOO_SMALL"


def test_aceita_limite_minimo_de_64px():
    validate_image_bytes(_encode(_textured(64, 64), ".png"), 5 * MB)


def test_rejeita_dimensoes_gigantes_pelo_cabecalho_sem_decodificar():
    data = _png_header_only(9000, 100)
    with pytest.raises(VisionError) as exc:
        validate_image_bytes(data, 5 * MB)
    assert exc.value.code == "IMAGE_DIMENSIONS_TOO_LARGE"


def test_rejeita_dimensoes_acima_de_8000px_decodificadas():
    big = np.full((70, 8001, 3), 128, dtype=np.uint8)
    with pytest.raises(VisionError) as exc:
        validate_image_bytes(_encode(big, ".png"), 5 * MB)
    assert exc.value.code == "IMAGE_DIMENSIONS_TOO_LARGE"


def test_rejeita_arquivo_maior_que_o_limite():
    data = _encode(_textured(400, 400), ".png")
    with pytest.raises(VisionError) as exc:
        validate_image_bytes(data, len(data) - 1)
    assert exc.value.code == "FILE_TOO_LARGE"
    assert "MB" in exc.value.message


def test_tamanho_exatamente_no_limite_e_aceito():
    data = _encode(_textured(), ".jpg")
    validate_image_bytes(data, len(data))


def test_decode_converte_cinza_e_alfa_para_bgr():
    gray = np.random.default_rng(2).integers(0, 255, (100, 120), dtype=np.uint8)
    rgba = np.dstack([_textured(100, 120), np.full((100, 120), 200, np.uint8)])
    for img in (gray, rgba):
        out = decode_image(_encode(img, ".png"))
        assert out.shape == (100, 120, 3) and out.dtype == np.uint8


def test_vision_error_tem_codigo_e_mensagem_em_portugues():
    err = VisionError("X", "Mensagem em português")
    assert err.code == "X" and err.message == "Mensagem em português"
    assert str(err) == "Mensagem em português"
    assert isinstance(err, Exception)
