import hashlib
import re
from datetime import datetime
from pathlib import Path

import gspread
import pandas as pd
import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build



def extract_spreadsheet_id(url: str) -> str:
    """
    Google SpreadsheetのURLからSpreadsheet IDを抽出する

    Parameters
    ----------
    url : str
        Google Spreadsheet URL

    Returns
    -------
    str
        Spreadsheet ID

    Raises
    ------
    ValueError
        URLにSpreadsheet IDが見つからない場合
    """
    url = url.replace("\\","/").replace("//","/")
    
    pattern = r"/spreadsheets/d/([a-zA-Z0-9-_]+)"

    match = re.search(pattern, url)
    if not match:
        raise ValueError("Spreadsheet ID が見つかりません")

    return match.group(1)


def add_new_url(
    spreadsheet_id: str,
    worksheet_name: str,
    date: str,
    youtube_url: str,
    credential_file:str |Path
) -> bool:
    """
    Google Sheetsに予定を追加する

    Parameters
    ----------
    spreadsheet_id : str
        スプレッドシートID
    worksheet_name : str
        シート名
    date : str
        yyyy-mm-dd形式の日付
    youtube_url : str
        YouTube URL
    credential_file : str | Patth
        Service AccountのJSONファイル

    Returns
    -------
    bool
        追加成功ならTrue
        日付重複ならFalse
    """

    credential_file = Path(credential_file)

    gc = gspread.service_account(
        filename=str(credential_file)
    )
    sheet = gc.open_by_key(spreadsheet_id).worksheet(worksheet_name)

    # 全データ取得
    records = sheet.get_all_records()

    # 日付重複チェック
    existing_dates = [str(row["日付"]) for row in records]

    if date in existing_dates:
        print(f"警告: {date} は既に登録されています")
        return False

    # 新規追加
    records.append({
        "日付": date,
        "YouTubeURL": youtube_url
    })

    # 日付順ソート
    records.sort(
        key=lambda x: datetime.strptime(
            str(x["日付"]),
            "%Y-%m-%d"
        )
    )

    # シート全体を書き戻し
    values: list[list[str]] = [
    ["日付", "YouTubeURL"]
    ]

    values.extend(
        [
            [
                str(row["日付"]),
                str(row["YouTubeURL"])
            ]
            for row in records
        ]
    )

    sheet.clear()
    sheet.update(values)

    print(f"{date} を追加しました")
    return True

def update_google_sheet(
    spreadsheet_id: str,
    sheet_name: str,
    cell: str,
    value: str,
    credential_file: str | Path
) -> None:
    """
    Google Spreadsheetの指定セルを更新する

    Parameters
    ----------
    spreadsheet_id : str
        スプレッドシートID
    sheet_name : str
        シート名
    cell : str
        セル位置 (例: A1)
    value : Any
        書き込む値
    credential_file : str
        Service AccountのJSONファイル
    """

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_file(
        credential_file,
        scopes=scopes
    )

    gc = gspread.authorize(creds)

    spreadsheet = gc.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet(sheet_name)

    worksheet.update(range_name=cell, values=[[value]])

    print(f"{sheet_name}!{cell} に '{value}' を更新しました")
if __name__=="__main__":
    spread_sheet_url="https://docs.google.com/spreadsheets/d/1DtDIK2QJGgKmUqMdGREqSv-7EJXrx16vWWCDzyyPhJs/edit?gid=0#gid=0"
    update_google_sheet(spreadsheet_id=extract_spreadsheet_id(spread_sheet_url),
                        sheet_name="SunSpotCalender",
                        cell="C1",
                        value="testcell",
                        credential_file=r"secrets\sunspotcalender-832ea382b537.json")