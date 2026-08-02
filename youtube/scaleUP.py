import pathlib
from tkinter.filedialog import askdirectory, askopenfilename

import cv2


def upscale_video(
    input_path, output_path, target_width=2560, target_height=1440, method="nearest"
):
    """
    動画の解像度をアップスケールして書き出す関数

    :param input_path: 元動画のファイルパス
    :param output_path: 出力先動画のファイルパス
    :param target_width: 拡大後の横幅（デフォルト: 2560 = 2K）
    :param target_height: 拡大後の縦幅（デフォルト: 1440 = 2K）
    :param method: 'nearest'（ピクセル等分・クッキリ）か 'cubic'（滑らか）
    """
    # 元動画を開く
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("エラー: 動画ファイルを開けませんでした。")
        return

    # 元動画の情報（FPSや総フレーム数）を取得
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # 拡大時の補間方法を選択
    # INTER_NEAREST: ピクセルをそのまま複製（ピクセル等分・くっきり）
    # INTER_CUBIC: バイキュービック補間（なめらか）
    interpolation_flag = cv2.INTER_NEAREST if method == "nearest" else cv2.INTER_CUBIC

    # 書き出し設定 (mp4vコーデックを使用)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_width, target_height))

    print(f"変換を開始します... ({target_width}x{target_height}, 補間: {method})")

    current_frame = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # フレーム単位で解像度を拡大
        resized_frame = cv2.resize(
            frame, (target_width, target_height), interpolation=interpolation_flag
        )

        # 拡大したフレームを書き出し
        out.write(resized_frame)

        current_frame += 1
        if current_frame % 30 == 0 or current_frame == total_frames:
            print(f"進捗: {current_frame}/{total_frames} フレーム完了", end="\r")

    # リソースの解放
    cap.release()
    out.release()
    print(f"\n変換が完了しました！ {output_path} に保存されました。")


if __name__ == "__main__":
    # 入力ファイル名と出力ファイル名を指定してください
    input_file = askopenfilename(title="入力動画を選択")
    output_directory = askdirectory(title="出力動画の保存先を選択")
    output_file = pathlib.Path(output_directory) / f"{pathlib.Path(input_file).stem}_upscaled.mp4"

    # ピクセルを等分してくっきり拡大したい場合 (method='nearest')
    upscale_video(
        input_file, output_file, target_width=2560, target_height=1440, method="nearest"
    )
