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
from PIL import Image, ImageEnhance, ImageDraw, ImageFont, ImageFilter


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

    @staticmethod
    def make_overlay_text(image_path: Path, mode: str) -> str:
        """
        overlay.text の指定に応じて表示文字列を作る。
        mode:
          - filename
          - parent_and_filename
          - fullpath
        """
        if mode == "fullpath":
            return str(image_path)
        if mode == "parent_and_filename":
            # 親フォルダ名/ファイル名
            parent = image_path.parent.name
            return f"{parent}/{image_path.name}" if parent else image_path.name
        # default: filename
        return image_path.name

    @staticmethod
    def draw_text_overlay(
        img: Image.Image,
        text: str,
        font_size: int = 16,
        margin_x: int = 50,
        margin_y: int = 50,
    ) -> Image.Image:
        """
        画像の右下に、可読性のある文字（縁取り）を描画して返す。
        ※元画像は破壊しない
        """
        out = img.copy()

        if out.mode not in ("RGB", "RGBA"):
            out = out.convert("RGBA")

        draw = ImageDraw.Draw(out)

        try:
            font = ImageFont.truetype("meiryo.ttc", font_size)
        except Exception:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except Exception:
                font = ImageFont.load_default()

        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except Exception:
            text_w, text_h = draw.textsize(text, font=font)

        # 右下に描画
        x = out.width - margin_x - text_w
        y = out.height - margin_y - text_h

        # 発光エフェクト用の下地を作成
        glow = Image.new("RGBA", out.size, (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)

        # 光の色（RGBA）
        glow_color = (255, 255, 120, 200)

        # まず少し太めに描いて“光の芯”を作る
        gdraw.text((x, y), text, font=font, fill=glow_color, stroke_width=max(2, font_size // 8), stroke_fill=glow_color)

        # ぼかしてふんわりさせる
        blur_radius = max(5, font_size // 6)
        glow = glow.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # 元画像に合成
        out = Image.alpha_composite(out.convert("RGBA"), glow)
        draw = ImageDraw.Draw(out)  # 合成後に描画し直す

        # 最後に文字本体をくっきり描く
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

        return out
