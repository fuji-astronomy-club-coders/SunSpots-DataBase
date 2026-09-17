#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
観測画像カレンダー自動生成スクリプト
linklist に (日付: 動画URL, サムネURL) をハードコードしておくと、
月曜始まりのカレンダーHTMLを生成します。
"""

import calendar

# ==========================================================
# 1. 設定：対象の年月
# ==========================================================
YEAR = 2026
MONTH = 9  # 9月

# ==========================================================
# 2. ハードコードされたリンクリスト
#    {日: (動画URL, サムネイル画像URL)}
#    エントリがない日は空マス（サムネなし）として出力されます。
# ==========================================================
linklist = {
    1: [
        "https://www.youtube.com/watch?v=qe29NgNqJZw&list=RDqe29NgNqJZw&start_radio=1",
        "https://via.placeholder.com/150?text=Sun+9/1",
    ],
    2: [
        "https://youtu.be/限定公開URL_02",
        "https://via.placeholder.com/150?text=Sun+9/2",
    ],
    3: [
        "https://youtu.be/限定公開URL_03",
        "https://via.placeholder.com/150?text=Sun+9/3",
    ],
    # 4: ("https://youtu.be/xxx", "https://..."),
    # 必要に応じて追記してください
}

"""
qualities

'maxresdefault'
'sddefault'
'mqdefault'
'default'
"""


def get_youtube_thumbnail(video_url: str, quality: str = "mqdefault") -> str:
    """
    YouTube 動画 URL からサムネイル URL を生成します。

    Args:
        video_url (str): YouTube 動画 URL (例: "https://youtu.be/VIDEO_ID" 或は "https://www.youtube.com/watch?v=VIDEO_ID")
        quality (str): サムネイルの解像度 (default, mqdefault, sddefault, maxresdefault)

    Returns:
        str: サムネイル URL
    """
    # 動画 ID を抽出
    if "youtu.be" in video_url:
        video_id = video_url.split("/")[-1]
    elif "watch?v=" in video_url:
        video_id = video_url.split("watch?v=")[-1].split("&")[0]
    else:
        raise ValueError("無効な YouTube URL です。")

    return f"https://img.youtube.com/vi/{video_id}/{quality}.jpg"


for k, v in linklist.items():
    videoUrl = v[0]
    imgUrl = get_youtube_thumbnail(videoUrl, "maxresdefault")
    linklist[k] = [videoUrl, imgUrl]

# ==========================================================
# 3. テンプレート
# ==========================================================
CSS = """
    .calendar-container {
      max-width: 900px;
      margin: 0 auto;
      font-family: sans-serif;
      box-sizing: border-box;
    }
    .calendar-header {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      text-align: center;
      font-weight: bold;
      background-color: #2c3e50;
      color: #ffffff;
      padding: 10px 0;
      border-radius: 8px 8px 0 0;
    }
    .calendar-grid {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      gap: 6px;
      background-color: #ecf0f1;
      padding: 6px;
      border-radius: 0 0 8px 8px;
    }
    .day-cell {
      background-color: #ffffff;
      min-height: 110px;
      padding: 6px;
      border-radius: 4px;
      display: flex;
      flex-direction: column;
      align-items: center;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .day-number {
      align-self: flex-start;
      font-size: 0.85rem;
      font-weight: bold;
      color: #333;
      margin-bottom: 4px;
    }
    .thumb-link {
      width: 100%;
      text-align: center;
      display: block;
      text-decoration: none;
    }
    .thumb-img {
      width: 100%;
      aspect-ratio: 1 / 1;
      object-fit: cover;
      border-radius: 4px;
      transition: transform 0.2s ease, opacity 0.2s ease;
    }
    .thumb-link:hover .thumb-img {
      transform: scale(1.04);
      opacity: 0.85;
    }
    .empty-cell {
      background-color: transparent;
      box-shadow: none;
    }
"""

CELL_WITH_LINK = """    <div class="day-cell">
      <span class="day-number">{day}</span>
      <a class="thumb-link" href="{url}" target="_blank" rel="noopener noreferrer">
        <img class="thumb-img" src="{thumb}" alt="{month}/{day} 観測画像">
      </a>
    </div>"""

CELL_NO_LINK = """    <div class="day-cell">
      <span class="day-number">{day}</span>
    </div>"""

EMPTY_CELL = '    <div class="day-cell empty-cell"></div>'


def build_cells(year: int, month: int, links: dict) -> str:
    """linklist から日付グリッドのHTMLを生成する"""
    cal = calendar.Calendar(firstweekday=0)  # 0 = 月曜始まり
    cells = []

    for week in cal.monthdatescalendar(year, month):
        for d in week:
            if d.month != month:
                # 前月・翌月分の余白マス（自動計算されるため手書き不要）
                cells.append(EMPTY_CELL)
            elif d.day in links:
                url, thumb = links[d.day]
                cells.append(
                    CELL_WITH_LINK.format(day=d.day, url=url, thumb=thumb, month=month)
                )
            else:
                cells.append(CELL_NO_LINK.format(day=d.day))

    return "\n".join(cells)


def build_html(year: int, month: int, links: dict) -> str:
    cells = build_cells(year, month, links)
    weekdays = "\n".join(
        f"    <div>{w}</div>" for w in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    )
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>{year}年{month}月 観測カレンダー</title>
  <style>{CSS}
  </style>
</head>
<body>

<div class="calendar-container">
  <!-- 1. 曜日ヘッダー (月曜日始まり) -->
  <div class="calendar-header">
{weekdays}
  </div>

  <!-- 2. 日付グリッド (linklist から自動生成) -->
  <div class="calendar-grid">
{cells}
  </div>
</div>

</body>
</html>"""


if __name__ == "__main__":
    from pathlib import Path
    html = build_html(YEAR, MONTH, linklist)
    
    out_path = Path("generated") / f"calendar_{YEAR}_{MONTH:02d}.html"
    out_path.parent.mkdir()
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"生成完了: {out_path}")
