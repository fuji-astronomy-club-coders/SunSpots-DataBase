import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

# YouTubeアップロード用のスコープ
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def upload_video_to_youtube(file_path: str, title: str, description: str, client_secrets_file: str = 'client_secret.json') -> dict:
    """
    動画をYouTubeに限定公開でアップロードする関数
    
    :param file_path: アップロードする動画ファイルのパス (例: 'video.mp4')
    :param title: 動画のタイトル
    :param description: 動画の概要欄
    :param client_secrets_file: GCPからダウンロードしたOAuth 2.0 クライアントIDのJSONファイルパス
    :return: 成功/失敗のステータスとURLを含む辞書
    """
    if not os.path.exists(file_path):
        return {"success": False, "error": "ファイルが見つかりません。", "url": None}

    creds = None
    # 既存のトークンがあれば読み込む（次回以降の認証を省略するため）
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # 有効な認証情報がない場合はログイン処理を実行
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secrets_file):
                return {"success": False, "error": f"{client_secrets_file} が見つかりません。", "url": None}
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # 認証情報を保存
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # YouTube APIサービスの構築
        youtube = build('youtube', 'v3', credentials=creds)

        # リクエストボディの作成
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'categoryId': '22' # 22 = People & Blogs（必要に応じて変更）
            },
            'status': {
                'privacyStatus': 'unlisted' # 限定公開
            }
        }

        # メディアファイルの読み込み
        media_body = MediaFileUpload(file_path, chunksize=-1, resumable=True)

        # アップロードリクエストの作成と実行
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media_body
        )
        
        response = request.execute()

        # 成功時
        video_id = response.get('id')
        video_url = f"https://youtu.be/{video_id}"
        return {"success": True, "url": video_url, "error": None}

    except HttpError as e:
        # APIエラー時
        return {"success": False, "url": None, "error": f"APIエラーが発生しました: {e.reason}"}
    except Exception as e:
        # その他の予期せぬエラー
        return {"success": False, "url": None, "error": f"予期せぬエラー: {str(e)}"}

# 実行例
if __name__ == '__main__':
    result = upload_video_to_youtube(
        file_path="sample.mp4",
        title="テスト動画のタイトル",
        description="これはAPI経由でアップロードされたテスト動画の概要欄です。\n改行も可能です。"
    )
    
    if result["success"]:
        print(f"アップロード成功！ URL: {result['url']}")
    else:
        print(f"アップロード失敗: {result['error']}")
