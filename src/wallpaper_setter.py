# Wallpaper Changer
#
# Windows 壁紙設定モジュール
#
# Copyright (c) 2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import ctypes
from pathlib import Path

SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02


def set_wallpaper(image_path: str | Path, style: str = "ignore"):
    """
    Windows の壁紙を変更する。
    ・画像パスの適用のみ行う
    ・壁紙の表示スタイルは Windows 側の設定に任せる
    """

    image_path = str(Path(image_path).resolve())

    # SystemParametersInfoW の呼び出し（レジストリは触らない）
    result = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER,
        0,
        image_path,
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )

    if not result:
        raise RuntimeError(f"Failed to set wallpaper: {image_path}")
