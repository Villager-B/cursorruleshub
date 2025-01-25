import json
import logging
import os
import time
from datetime import datetime

from config import (
    CURSORRULES_DATA_FILE,
    DATA_DIR,
    GITHUB_TOKEN,
)
from dotenv import load_dotenv
from github import Github
from github.Repository import Repository
from tqdm import tqdm

# 環境変数の読み込み
load_dotenv()

# ロガーの設定
logging.basicConfig(
    level=os.getenv("ERROR_LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class CursorRulesCollector:
    def __init__(self):
        self.token = GITHUB_TOKEN
        self.api_url = os.getenv("GITHUB_API_URL", "https://api.github.com")
        self.github = Github(self.token)
        self.ensure_data_directory()

    def ensure_data_directory(self):
        """データディレクトリが存在しない場合は作成"""
        os.makedirs(DATA_DIR, exist_ok=True)

    def check_rate_limit(self) -> bool:
        """APIのレート制限をチェックする（基本的な制限チェックのみ）"""
        rate_limit = self.github.get_rate_limit()
        remaining = rate_limit.core.remaining

        logger.info(f"API Requests remaining: {remaining}")

        if remaining <= 10:  # 最小限の安全マージン
            wait_time = rate_limit.core.reset.timestamp() - time.time()
            if wait_time > 0:
                logger.warning(
                    f"Rate limit reached. Waiting for {wait_time:.2f} seconds"
                )
                time.sleep(wait_time)
            return False

        return True

    def get_repo_info(self, repo: Repository) -> dict:
        """リポジトリの情報を取得"""
        return {
            "name": repo.full_name,
            "url": repo.html_url,
            "description": repo.description,
            "stars": repo.stargazers_count,
            "language": repo.language,
            "updated_at": repo.updated_at.isoformat(),
            "cursorrules_url": f"{repo.html_url}/blob/master/.cursorrules",
        }

    def collect_data(self):
        """CursorRulesを含むリポジトリの情報を収集"""
        print("Collecting repository data...")
        repos_data = []

        try:
            # リポジトリの検索
            query = "filename:.cursorrules"
            repos = self.github.search_repositories(
                query=query, sort="stars", order="desc"
            )

            # プログレスバーの設定
            max_repos = int(os.getenv("MAX_REPOSITORIES", 100))
            with tqdm(total=max_repos) as pbar:
                for i, repo in enumerate(repos[:max_repos]):
                    if i >= max_repos:
                        break

                    if not self.check_rate_limit():
                        break

                    try:
                        repo_info = self.get_repo_info(repo)
                        repos_data.append(repo_info)
                        pbar.update(1)
                    except Exception as e:
                        print(f"Error processing repository {repo.full_name}: {e}")
                        continue

        except Exception as e:
            print(f"Error during data collection: {e}")
            return False

        # データの保存
        if repos_data:
            data = {
                "last_updated": datetime.utcnow().isoformat(),
                "repositories": repos_data,
            }

            with open(CURSORRULES_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"Data saved to {CURSORRULES_DATA_FILE}")
            return True

        return False


def main():
    collector = CursorRulesCollector()
    success = collector.collect_data()
    if success:
        print("Data collection completed successfully")
    else:
        print("Data collection failed")
        exit(1)


if __name__ == "__main__":
    main()
