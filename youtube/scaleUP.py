import pathlib
from tkinter.filedialog import askdirectory, askopenfilename

import cv2
import numpy as np
from cv2 import VideoWriter_fourcc  # pyright: ignore[reportAttributeAccessIssue]


def upscale_video(
    input_path,
    output_path,
    target_width=2560,
    target_height=1440,
    method="nearest",
    pad_color=(0, 0, 0),  # 余白の色 (B, G, R) デフォルトは黒
):
    """
    元の縦横比を維持したまま動画の解像度をアップスケールする関数

    :param input_path: 元動画のファイルパス
    :param output_path: 出力先動画のファイルパス
    :param target_width: 最終的なキャンバス幅 (デフォルト: 2560 = 2K)
    :param target_height: 最終的なキャンバス高さ (デフォルト: 1440 = 2K)
    :param method: 'nearest'（ピクセル等分・クッキリ）か 'cubic'（滑らか）
    :param pad_color: アスペクト比調整で追加される余白の色 (B, G, R)
    """

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("エラー: 動画ファイルを開けませんでした。")
        return

    # 元動画の情報を取得
    orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # 1. 縦横比を維持するためのスケール（倍率）を計算
    scale = min(target_width / orig_w, target_height / orig_h)

    # 拡大後の画像サイズ（リサイズサイズ）
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)

    # 2. 余白（パディング）の計算 (中央配置用)
    pad_x = (target_width - new_w) // 2
    pad_y = (target_height - new_h) // 2

    # 補間アルゴリズムの選択
    interpolation_flag = cv2.INTER_NEAREST if method == "nearest" else cv2.INTER_CUBIC

    # 動画書き出し設定 (2Kキャンバスサイズで出力)
    fourcc = VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_width, target_height))

    print(f"元サイズ: {orig_w}x{orig_h} -> 拡大サイズ: {new_w}x{new_h}")
    print(
        f"キャンバスサイズ: {target_width}x{target_height} (余白配置 X:{pad_x}px, Y:{pad_y}px)"
    )
    print("変換を開始します...")

    current_frame = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # アスペクト比を維持して拡大
        resized_frame = cv2.resize(
            frame, (new_w, new_h), interpolation=interpolation_flag
        )

        # 指定サイズ（2560x1440）のキャンバス（背景）を作成
        canvas = np.full((target_height, target_width, 3), pad_color, dtype=np.uint8)

        # キャンバスの中央に拡大した動画フレームを書き込み
        canvas[pad_y : pad_y + new_h, pad_x : pad_x + new_w] = resized_frame

        # 出力ファイルに書き出し
        out.write(canvas)

        current_frame += 1
        if current_frame % 30 == 0 or current_frame == total_frames:
            print(f"進捗: {current_frame}/{total_frames} フレーム完了", end="\r")

    cap.release()
    out.release()
    print(f"\n変換が完了しました！ {output_path} に保存されました。")


if __name__ == "__main__":
    # 入力ファイル名と出力ファイル名を指定してください
    input_file = askopenfilename(title="入力動画を選択")
    output_directory = askdirectory(title="出力動画の保存先を選択")
    output_file = (
        pathlib.Path(output_directory) / f"{pathlib.Path(input_file).stem}_upscaled.mp4"
    )

    # ピクセルを等分してくっきり拡大したい場合 (method='nearest')
    upscale_video(
        input_file, output_file, target_width=7680, target_height=4320, method="nearest"
    )
