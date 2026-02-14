# Wallpaper Changer

© 2025-2026 led-mirage

Windows の壁紙をランダムに変更するためのシンプルなコマンドラインツールです。  
指定した複数フォルダから画像を選び、明るさを調整して壁紙として適用します。

## ✨ 特徴

* Windows 専用の壁紙チェンジャー
* 複数フォルダ＋サブフォルダから画像を再帰的に探索
* 対応している拡張子は ".jpg", ".jpeg", ".png", ".bmp", ".webp"
* ランダムで 1 枚選択
* 明るさ調整（元画像は変更しません）
* ファイル情報オーバーレイ描画機能（元画像は変更しません）
* TEMP フォルダに一時画像を保存してから適用
* 壁紙の配置方法は **Windows 側の設定をそのまま使用**
* 設定ファイル（YAML）または **ワンライナー実行** の両方に対応
* EXE 版（PyInstaller）と Python 版をサポート

## 📁 ディレクトリ構成

```
WallpaperChanger/
├─ src/
│  ├─ main.py
│  ├─ config_loader.py
│  ├─ image_processor.py
│  └─ wallpaper_setter.py
│
├─ config/
│  └─ config.yaml
│
├─ build_tools/ （ビルド用）
│  ├─ build.bat
│  └─ version.yaml
│
├─ tools/ 
│  └─ task_wallpaper.js
│
└─ design/
   └─ 仕様.md
```

<div class="page" />

## 🖥️ 動作環境

- Windows 11
- Python 3.11以上（EXE版を使う場合は不要）

## 📦 EXE 版の使い方（一般ユーザー向け）

[Releases](https://github.com/led-mirage/WallpaperChanger/releases) から ZIP をダウンロードして展開すると、以下が含まれています。

```
WallpaperChanger.exe  …　プログラム本体
task_wallpaper.js     …　タスクスケジューラ登録用スクリプト
LICENSE               …　ライセンス情報
README.pdf            …　説明書
config/
  └ config.yaml       …　設定ファイル
```

### 1. 設定ファイル方式で使う（通常）

最初に `config/config.yaml` を編集します。
`image_dirs` の値を画像があるフォルダのパスに置き換えてください。

```yaml
# 壁紙があるフォルダ（複数指定可）
image_dirs:
  - 'C:\Users\UserA\Desktop\Wallpapers'
  - 'C:\MyData\Images'

# 壁紙の明るさ (0.0～2.0 : 1.0は明るさ100%)
brightness: 0.8

# テンポラリファイル名（Windows の %TEMP% に保存される）
temp_filename: 'wallpaper_temp.png'

# 画像上に表示するテキストオーバーレイの設定
overlay:
  enabled: false        # オーバーレイ表示の有効/無効
  text: filename        # filename | parent_and_filename | fullpath
  font_size: 16         # px（int）
  margin_x: 50          # 右端からの余白（px）
  margin_y: 100         # 下端からの余白（px）
```

#### 実行

```powershell
WallpaperChanger.exe config/config.yaml
```

### 2. コマンドライン引数方式で使う（設定ファイル不要）

設定ファイルがなくても、`--dir` を指定すれば実行できます。

```powershell
# サンプル
WallpaperChanger.exe --dir "C:/Pictures" --dir "D:/Wallpapers" --brightness 0.8 --temp temp.png
```

* `--dir` は壁紙があるフォルダ（複数指定できます）
* `--brightness` は 0.0〜2.0（省略時 1.0）
* `--temp` は TEMP に保存するファイル名（省略時 wallpaper_temp.png）

※ `WallpaperChanger.exe` を引数なしで実行すると、使用できるオプションの完全なリストと説明が表示されます。

### 3. 自動実行したい場合

このツールはWindowsの **タスクスケジューラー** に登録することで、
以下のような運用が可能です：

* Windows ログイン時に自動実行
* 一定時間ごとに自動更新（例：30分ごと）

※ 登録手順の詳細は Windows の公式ドキュメントをご参照ください。

#### タスクスケジューラ Tips

`WallpaperChanger.exe` を直接タスクスケジューラに登録してもいいですが、  
それだと実行時にコンソールの黒い画面が一瞬表示されてしまいます。

これを避けるには本ツールを非表示状態で実行する必要があります。  
同梱されている `task_wallpaper.js` は `WallpaperChanger.exe` を非表示で実行するための短いスクリプトです。  
これを使ってタスクを登録する手順は以下の通りです（概要）。

1. タスクスケジューラを開く
2. 「タスクの作成」を押す
3. 適当な名前を付ける（壁紙チェンジャーなど）
4. 「操作」タブ → 「新規」 →
    プログラム： `wscript.exe`
    引数： `task_wallpaper.js`
    開始： `task_wallpaper.js`があるフォルダパス
5. 「トリガー」で実行タイミングを選ぶ

<div class="page" />

## 🧰 Python 版の使い方（開発者向け）

Python版も起動方法が変わるだけで、基本的な使い方はEXE版と同じです。

### 1. 必要なライブラリをインストール

※ 初回のみ必要です。

```powershell
pip install -r requirements.txt
```

### 2. 設定ファイル方式で使う

※ あらかじめ設定ファイルを編集しておいてください。

```powershell
python src/main.py config/config.yaml
```

### 3. コマンドライン引数方式で使う（設定ファイル不要）

```powershell
python src/main.py --dir "C:/Pictures" --brightness 0.8
```

## 📝 エラー時の挙動

エラーが発生すると `error.log` にエラーが記録されます。  
設定ファイル方式で実行した場合は、設定ファイルと同じフォルダに `error.log` が生成されます。  
コマンドライン引数方式で実行した場合は カレントフォルダに生成されます。

例：

```log
[2025-12-08 21:36:56] Error: 'No images available to pick.'
```

## 🔧 ビルド方法

自分で EXE ファイルを生成したい場合は次のようにします。

```powershell
pip install pyinstaller pyinstaller_versionfile
build_tools\build.bat
```

実行すると `dist/WallpaperChanger.exe` が生成されます。

<div class="page" />

## ⚠️ ウイルス対策ソフトの誤検知について

本アプリの EXE 版は **PyInstaller** で生成されていますが、
一部のウイルス対策ソフトにより **誤ってマルウェアと判定される場合があります**。

* アプリには悪意のあるコードは一切含まれていません
* ソースコードはすべて公開されています
* 誤検知は PyInstaller 製 EXE で広く見られる既知の問題です

もし気になる場合は、本README内の  
**「Python 版の使い方（開発者向け）」に沿って、ソースコードから直接実行する方法をおすすめします。**

VirusTotal でのスキャン結果は [**こちら**](https://www.virustotal.com/gui/file/2f9425bc599bd7b3e18128119ebc94c413b32acda86522ae60a2d90b898e9db9/detection) から確認できます。  
（72個中3個のアンチウィルスエンジンで検出 :2026/02/14 v1.1.0）


## 📚 使用しているライブラリ

### 🔖 **Pillow 12.1.1**
画像の明るさ調整に使用しています  
ライセンス： MIT-CMUライセンス  
[https://github.com/python-pillow/Pillow](https://github.com/python-pillow/Pillow)

### 🔖 **PyYAML 6.0.3**
設定ファイル（YAML）の読み込みに使用しています  
ライセンス：MIT License  
[https://github.com/yaml/pyyaml](https://github.com/yaml/pyyaml)

### 🔖 **PyInstaller 6.17.0**
EXE 版の作成に使用しています  
ライセンス：GPL-2.0 / Apache License 2.0  
[https://github.com/pyinstaller/pyinstaller](https://github.com/pyinstaller/pyinstaller)

### 🔖 **pyinstaller-versionfile 3.0.1**
EXE 版の作成時に必要です（EXEファイルにバージョン情報を付加するため）  
ライセンス：MIT license  
[https://github.com/DudeNr33/pyinstaller-versionfile](https://github.com/DudeNr33/pyinstaller-versionfile)

<div class="page" />

## ❗ 免責事項

- このソフトの利用によって生じた損害について、作者は責任を負いません
- 可能な範囲で安定動作を目指していますが、完全な動作保証はできません
- 自己の判断と責任で使ってください

## 📄 ライセンス

本プロジェクトは **MIT License** の下で公開されています。  
詳しくは `LICENSE` を参照してください。

## 📜 バージョン履歴

### 1.1.0 (2026/02/14)

- ファイル名を画像の上にオーバーレイ表示する機能を追加
- pillowのバージョンを12.1.1に更新（CVE-2026-25990対応

### 1.0.0 (2025/12/13)

- ファーストリリース
