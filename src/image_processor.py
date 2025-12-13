# Wallpaper Changer
#
# 画像処理モジュール
#
# Copyright (c) 2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

from pathlib import Path
import random
import tempfile
from PIL import Image, ImageEnhance


class ImageProcessor:

    @staticmethod
    def scan_images(dirs: list[str]) -> list[Path]:
        """
        指定フォルダ群を再帰的に探索し、画像ファイルの一覧を返す。
        ・存在しないフォルダは無視する
        ・画像が1枚もなくても例外にはせず、空リストを返す
        """
        supported_ext = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        results: list[Path] = []

        for d in dirs:
            p = Path(d)
            # 存在しない DIR は無視
            if not p.exists() or not p.is_dir():
                continue

            for file in p.rglob("*"):
                if file.suffix.lower() in supported_ext:
                    results.append(file)

        return results  # 空でもOK

    @staticmethod
    def pick_random(images: list[Path]) -> Path:
        """画像リストからランダムに1つ選ぶ。空リストの場合は例外。"""
        if not images:
            raise ValueError("No images available to pick.")
        return random.choice(images)

    @staticmethod
    def adjust_brightness(img: Image.Image, value: float) -> Image.Image:
        """明るさを調整して新しい Image オブジェクトを返す。"""
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(value)

    @staticmethod
    def save_to_temp(img: Image.Image, filename: str) -> Path:
        """Windows の TEMP フォルダに指定ファイル名で画像を保存して Path を返す。"""
        temp_dir = Path(tempfile.gettempdir())
        save_path = temp_dir / filename
        img.save(save_path)
        return save_path
