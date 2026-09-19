from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials


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