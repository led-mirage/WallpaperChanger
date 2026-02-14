# Wallpaper Changer
#
# 設定ファイルローダー
#
# Copyright (c) 2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass
class OverlayConfig:
    enabled: bool = False
    text: str = "filename"   # filename | parent_and_filename | fullpath
    font_size: int = 16      # px
    margin_x: int = 100      # 右端からの余白（px）
    margin_y: int = 100      # 下端からの余白（px）


@dataclass
class Config:
    image_dirs: list[str]
    brightness: float
    temp_filename: str
    overlay: OverlayConfig = field(default_factory=OverlayConfig)


def _clamp_int(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(max_value, value))


def validate_config(image_dirs, brightness, temp_filename, overlay: OverlayConfig):
    """
    設定値のバリデーションを行う
    """

    if not isinstance(image_dirs, list):
        raise TypeError("image_dirs must be a list.")

    if not isinstance(brightness, (int, float)):
        raise TypeError("brightness must be a number.")
    if not (0.0 <= brightness <= 2.0):
        raise ValueError("brightness must be between 0.0 and 2.0.")

    if not isinstance(temp_filename, str):
        raise TypeError("temp_filename must be a string.")

    # overlay
    if not isinstance(overlay.enabled, bool):
        raise TypeError("overlay.enabled must be a bool.")

    if not isinstance(overlay.text, str):
        raise TypeError("overlay.text must be a string.")
    allowed = {"filename", "parent_and_filename", "fullpath"}
    if overlay.text not in allowed:
        overlay.text = "filename"

    if not isinstance(overlay.font_size, int):
        raise TypeError("overlay.font_size must be an int.")
    overlay.font_size = _clamp_int(overlay.font_size, 8, 200)

    if not isinstance(overlay.margin_x, int):
        raise TypeError("overlay.margin_x must be an int.")
    overlay.margin_x = _clamp_int(overlay.margin_x, 0, 1000)

    if not isinstance(overlay.margin_y, int):
        raise TypeError("overlay.margin_y must be an int.")
    overlay.margin_y = _clamp_int(overlay.margin_y, 0, 1000)


def load_config(path: str | Path) -> Config:
    """
    YAML の設定ファイルを読み込み、Config オブジェクトにして返す。
    ・存在しないキーがあれば例外
    ・brightness の値チェック
    ・image_dirs は存在しないフォルダが含まれていても許可（image_processor側で無視する）
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    # YAML読み込み
    with path.open("r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Failed to parse YAML: {e}")

    # 必須キーのチェック
    required_keys = ["image_dirs", "brightness", "temp_filename"]
    for key in required_keys:
        if key not in data:
            raise KeyError(f"Missing required config key: {key}")

    # 各設定値の取得
    image_dirs = data["image_dirs"]
    brightness = data["brightness"]
    temp_filename = data["temp_filename"]

    # overlay 設定の取得
    overlay_data = data.get("overlay", None)
    overlay = OverlayConfig()
    if overlay_data is not None:
        overlay.enabled = overlay_data.get("enabled", overlay.enabled)
        overlay.text = overlay_data.get("text", overlay.text)
        overlay.font_size = overlay_data.get("font_size", overlay.font_size)
        overlay.margin_x = overlay_data.get("margin_x", overlay.margin_x)
        overlay.margin_y = overlay_data.get("margin_y", overlay.margin_y)

    validate_config(image_dirs, brightness, temp_filename, overlay)

    return Config(
        image_dirs=image_dirs,
        brightness=float(brightness),
        temp_filename=temp_filename,
        overlay=overlay,
    )
