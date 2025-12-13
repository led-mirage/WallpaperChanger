# Wallpaper Changer
#
# 設定ファイルローダー
#
# Copyright (c) 2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class Config:
    image_dirs: list[str]
    brightness: float
    temp_filename: str


def validate_config(image_dirs, brightness, temp_filename):
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
    validate_config(image_dirs, brightness, temp_filename)

    return Config(
        image_dirs=image_dirs,
        brightness=float(brightness),
        temp_filename=temp_filename
    )
