import re
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials


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