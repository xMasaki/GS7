"""Testes de privacidade (acessacidade_vision.sanitize_image)."""

from __future__ import annotations

import io

import cv2
import numpy as np
import pytest

from acessacidade_vision import VisionError, sanitize_image, sanitize_image_with_report
from acessacidade_vision import privacy


def _textured(h: int = 600, w: int = 900) -> np.ndarray:
    rng = np.random.default_rng(3)
    base = rng.integers(90, 170, (h // 10 + 1, w // 10 + 1, 3), dtype=np.uint8)
    return cv2.resize(base, (w, h), interpolation=cv2.INTER_CUBIC)


def _jpeg_with_exif_gps(img_bgr: np.ndarray) -> bytes:
    """JPEG com EXIF (modelo do aparelho, data e GPS) criado com Pillow."""
    PIL = pytest.importorskip("PIL")
    from PIL import Image

    im = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    exif = Image.Exif()
    exif[0x010F] = "FabricanteFicticio"   # Make
    exif[0x0110] = "ModeloFicticio"       # Model
    exif[0x0132] = "2026:11:14 10:00:00"  # DateTime
    gps = {1: "S", 2: (23.0, 33.0, 1.0), 3: "W", 4: (46.0, 38.0, 1.0)}  # coordenadas fictícias
    exif[0x8825] = gps  # GPSInfo IFD
    buf = io.BytesIO()
    im.save(buf, format="JPEG", exif=exif.tobytes(), quality=92)
    return buf.getvalue()


def test_sanitize_remove_exif_e_gps():
    data = _jpeg_with_exif_gps(_textured())
    assert b"Exif" in data and b"ModeloFicticio" in data  # o arquivo de entrada tem EXIF
    out = sanitize_image(data)
    assert out[:3] == b"\xff\xd8\xff"
    assert b"Exif" not in out  # nenhum segmento APP1/EXIF
    assert b"ModeloFicticio" not in out and b"FabricanteFicticio" not in out


def test_sanitize_saida_sem_exif_mesmo_sem_pillow():
    ok, buf = cv2.imencode(".png", _textured())
    out = sanitize_image(buf.tobytes())
    assert b"Exif" not in out
    assert cv2.imdecode(np.frombuffer(out, np.uint8), cv2.IMREAD_COLOR) is not None


def test_sanitize_redimensiona_para_max_side():
    ok, buf = cv2.imencode(".jpg", _textured(1500, 2400))
    out = sanitize_image(buf.tobytes(), max_side=1000)
    img = cv2.imdecode(np.frombuffer(out, np.uint8), cv2.IMREAD_COLOR)
    assert max(img.shape[:2]) == 1000
    assert img.shape[1] / img.shape[0] == pytest.approx(2400 / 1500, rel=0.01)


def test_sanitize_nao_amplia_imagem_pequena():
    ok, buf = cv2.imencode(".jpg", _textured(300, 400))
    out, rep = sanitize_image_with_report(buf.tobytes(), max_side=1600)
    img = cv2.imdecode(np.frombuffer(out, np.uint8), cv2.IMREAD_COLOR)
    assert img.shape[:2] == (300, 400)
    assert rep["redimensionada"] is False
    assert rep["metadados_removidos"] is True


def test_sanitize_rejeita_entrada_invalida():
    with pytest.raises(VisionError):
        sanitize_image(b"nao e imagem")


def test_sanitize_segue_sem_classificador_de_rostos(monkeypatch, caplog):
    monkeypatch.setattr(privacy, "_load_face_cascade", lambda: None)
    ok, buf = cv2.imencode(".jpg", _textured())
    out, rep = sanitize_image_with_report(buf.tobytes(), blur_faces=True)
    assert rep["detector_rostos_disponivel"] is False
    assert rep["rostos_borrados"] == 0
    assert out[:3] == b"\xff\xd8\xff"


def test_classificador_haar_do_opencv_disponivel():
    privacy._load_face_cascade.cache_clear()
    assert privacy._load_face_cascade() is not None
    assert isinstance(privacy.detect_faces(_textured()), list)


def test_blur_faces_borra_as_regioes_detectadas(monkeypatch):
    img = _textured()
    rng = np.random.default_rng(9)
    img[100:220, 300:420] = rng.integers(0, 255, (120, 120, 3), dtype=np.uint8)  # "rosto" com detalhe
    monkeypatch.setattr(privacy, "detect_faces", lambda im: [(300, 100, 120, 120)])
    ok, buf = cv2.imencode(".png", img)
    out, rep = sanitize_image_with_report(buf.tobytes(), blur_faces=True)
    res = cv2.imdecode(np.frombuffer(out, np.uint8), cv2.IMREAD_COLOR)
    assert rep["rostos_borrados"] == 1
    region_before = cv2.Laplacian(cv2.cvtColor(img[100:220, 300:420], cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
    region_after = cv2.Laplacian(cv2.cvtColor(res[100:220, 300:420], cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
    assert region_after < region_before * 0.05


def test_blur_faces_false_nao_executa_deteccao(monkeypatch):
    def _fail(_):
        raise AssertionError("não deveria detectar rostos")

    monkeypatch.setattr(privacy, "detect_faces", _fail)
    ok, buf = cv2.imencode(".jpg", _textured())
    _, rep = sanitize_image_with_report(buf.tobytes(), blur_faces=False)
    assert rep["detector_rostos_disponivel"] is None
