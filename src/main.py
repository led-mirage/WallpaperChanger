# Wallpaper Changer
#
# メイン
#
# Copyright (c) 2025 led-mirage
# このソースコードは MITライセンス の下でライセンスされています。
# ライセンスの詳細については、このプロジェクトのLICENSEファイルを参照してください。

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

from PIL import Image

from config_loader import Config, OverlayConfig, validate_config, load_config
from image_processor import ImageProcessor
from wallpaper_setter import set_wallpaper


APP_NAME = "Wallpaper Changer"
APP_VERSION = "v1.1.0"
COPYRIGHT = "© 2025 led-mirage"

EXIT_OK = 0
EXIT_USAGE_ERROR = 1
EXIT_RUNTIME_ERROR = 2


def print_short_banner():
    print(f"{APP_NAME} {APP_VERSION}  {COPYRIGHT}")
    print("")


def print_long_banner():
    print("----------------------------------------------------------------------")
    print(f"  {APP_NAME} {APP_VERSION}\n")
    print(f"  {COPYRIGHT}")
    print("  MIT License")
    print("----------------------------------------------------------------------")
    print("")


def get_usage_text():
    if getattr(sys, 'frozen', False):
        # PyInstaller でビルドされた EXE の場合
        exe = os.path.basename(sys.argv[0])
        cmd = exe
    else:
        # Python での実行時
        cmd = "python src/main.py"

    return (
        "Usage:\n"
        f"  {cmd} <config.yaml>\n"
        f"  {cmd} --dir <path> [--dir <path> ...] "
        "[--brightness <value>] [--temp <filename>]\n\n"
        "Options:\n"
        "  --dir          画像フォルダを指定（複数可）\n"
        "  --brightness   明るさ (0.0–2.0、デフォルト 1.0)\n"
        "  --temp         TEMP に保存するファイル名\n"
        "  --version      バージョン情報を表示\n"
    )


def parse_args():
    parser = argparse.ArgumentParser(
        prog=os.path.basename(sys.argv[0]),
        description="Wallpaper Changer",
    )

    parser.add_argument("config", nargs="?", help="設定ファイル (yaml)")

    # ワンライナー用
    parser.add_argument("--dir", action="append", help="画像フォルダ（複数可）")
    parser.add_argument("--brightness", type=float, help="明るさ (0.0–2.0)")
    parser.add_argument("--temp", help="TEMPに保存するファイル名")
    parser.add_argument("--overlay", action="store_true", help="オーバーレイを有効化")
    parser.add_argument("--overlay-text", default=None, help="オーバーレイ文字列テンプレート")
    parser.add_argument("--overlay-font-size", type=int, default=None, help="フォントサイズ")
    parser.add_argument("--overlay-margin-x", type=int, default=None, help="横方向マージン")
    parser.add_argument("--overlay-margin-y", type=int, default=None, help="縦方向マージン")

    parser.add_argument("--version", action="store_true", help="バージョン情報を表示")

    args = parser.parse_args()

    # version でもなく、config も dir も無いなら usage
    if not args.version and not args.config and not args.dir:
        parser.print_help()
        sys.exit(EXIT_USAGE_ERROR)

    return args


def build_config_from_args(args) -> Config | None:
    # 1) config 指定があれば、それだけ使う（他は無視）
    if args.config:
        return load_config(Path(args.config))

    # 2) ワンライナー
    if not args.dir:
        return None

    image_dirs = args.dir
    brightness = args.brightness if args.brightness is not None else 1.0
    temp_filename = args.temp or "wallpaper_temp.png"

    # overlay（ワンライナー）
    overlay_enabled = args.overlay
    overlay_text = args.overlay_text or "filename"
    overlay_font_size = args.overlay_font_size or 16
    overlay_margin_x = args.overlay_margin_x or 50
    overlay_margin_y = args.overlay_margin_y or 100
    overlay = OverlayConfig(
        enabled=overlay_enabled,
        text=overlay_text,
        font_size=overlay_font_size,
        margin_x=overlay_margin_x,
        margin_y=overlay_margin_y
    )

    validate_config(image_dirs, brightness, temp_filename, overlay)

    return Config(
        image_dirs=image_dirs,
        brightness=brightness,
        temp_filename=temp_filename,
        overlay=overlay
    )


def write_error_log(config_path: Path, message: str):
    """設定ファイルと同じディレクトリに error.log を出力する。"""
    log_path = config_path.parent / "error.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] Error: {message}\n")


def main():
    args = parse_args()

    if args.version:
        print_long_banner()
        return EXIT_OK

    print_short_banner()

    try:
        # 設定読み込み
        config = build_config_from_args(args)

        # 画像探索
        images = ImageProcessor.scan_images(config.image_dirs)

        # ランダム選択
        selected_path = ImageProcessor.pick_random(images)

        # 画像読み込み
        img = Image.open(selected_path)

        # 明るさ調整
        img = ImageProcessor.adjust_brightness(img, config.brightness)

        # オーバーレイ文字列作成
        if config.overlay.enabled:
            text = ImageProcessor.make_overlay_text(
                selected_path, config.overlay.text)
            img = ImageProcessor.draw_text_overlay(
                img,
                text,
                font_size=config.overlay.font_size,
                margin_x=config.overlay.margin_x,
                margin_y=config.overlay.margin_y
            )

        # TEMP 保存
        temp_path = ImageProcessor.save_to_temp(img, config.temp_filename)

        # 壁紙設定
        set_wallpaper(temp_path)

        return EXIT_OK

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        print("Wrote error details to error.log.")

        config_path = Path(args.config if args.config else ".")
        write_error_log(config_path, str(e))
        return EXIT_RUNTIME_ERROR


if __name__ == "__main__":
    sys.exit(main())
