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

from config_loader import Config, validate_config, load_config
from image_processor import ImageProcessor
from wallpaper_setter import set_wallpaper


APP_NAME = "Wallpaper Changer"
APP_VERSION = "v1.0.0"
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
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument("config", nargs="?")
    parser.add_argument("--dir", action="append")
    parser.add_argument("--brightness", type=float)
    parser.add_argument("--temp")

    return parser.parse_args()


def build_config_from_args(args) -> Config | None:
    if args.config:
        # 設定ファイルが指定されていた場合
        config = load_config(Path(args.config))
    else:
        # ワンライナーの場合
        if not args.dir:
            return None
        image_dirs = args.dir or []
        brightness = args.brightness if args.brightness is not None else 1.0
        temp_filename = args.temp or "wallpaper_temp.png"
        validate_config(image_dirs, brightness, temp_filename)
        
        config = Config(
            image_dirs=image_dirs,
            brightness=brightness,
            temp_filename=temp_filename
        )
        args.config = "./config.yaml" # error.logの置き場所を決めるために必要
    return config


def write_error_log(config_path: Path, message: str):
    """設定ファイルと同じディレクトリに error.log を出力する。"""
    log_path = config_path.parent / "error.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] Error: {message}\n")


def main():
    if "--version" in sys.argv:
        print_long_banner()
        return EXIT_OK

    print_short_banner()

    args = parse_args()

    try:
        # 設定読み込み
        config = build_config_from_args(args)
        if config is None:
            print(get_usage_text())
            return EXIT_USAGE_ERROR

        # 画像探索
        images = ImageProcessor.scan_images(config.image_dirs)

        # ランダム選択
        selected_path = ImageProcessor.pick_random(images)

        # 画像読み込み
        img = Image.open(selected_path)

        # 明るさ調整
        img = ImageProcessor.adjust_brightness(img, config.brightness)

        # TEMP 保存
        temp_path = ImageProcessor.save_to_temp(img, config.temp_filename)

        # 壁紙設定
        set_wallpaper(temp_path)

        return EXIT_OK

    except Exception as e:
        print("An error occurred. See error.log for details.")
        config_path = Path(args.config)
        write_error_log(config_path, str(e))
        return EXIT_RUNTIME_ERROR


if __name__ == "__main__":
    sys.exit(main())
