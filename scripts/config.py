import os

from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# GitHub API設定
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("GitHub Token is not set in .env file")

# データ保存設定
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CURSORRULES_DATA_FILE = os.path.join(DATA_DIR, "cursorrules_data.json")

# GitHub API検索設定
SEARCH_QUERY = "filename:.cursorrules"
MAX_ITEMS_PER_PAGE = 100
MAX_TOTAL_ITEMS = 100  # スター数の多い上位100件のみを取得
