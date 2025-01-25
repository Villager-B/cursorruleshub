import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List

from dotenv import load_dotenv
from github import Github, GithubException
from github.Repository import Repository
from tqdm import tqdm

# 環境変数の読み込み
load_dotenv()

# 基本設定
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("GitHub Token is not set in .env file")

# データ保存設定
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CURSORRULES_DATA_FILE = os.path.join(DATA_DIR, "cursorrules_data.json")

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 検索クエリの定義
SEARCH_QUERIES = [
    "filename:.cursorrules",
    ".cursorrules in:path",
    "extension:cursorrules",
]


class CursorRulesCollector:
    def __init__(self):
        self.token = GITHUB_TOKEN
        self.api_url = os.getenv("GITHUB_API_URL", "https://api.github.com")
        self.github = Github(self.token)
        self.ensure_data_directory()
        self.processed_repos = set()  # 重複を防ぐためのセット

    def ensure_data_directory(self):
        """データディレクトリが存在しない場合は作成"""
        os.makedirs(DATA_DIR, exist_ok=True)

    def check_rate_limit(self) -> bool:
        """APIのレート制限をチェックする"""
        try:
            rate_limit = self.github.get_rate_limit()
            remaining = rate_limit.search.remaining
            reset_time = rate_limit.search.reset
            limit = rate_limit.search.limit

            logger.info(
                f"API Rate Limit - Remaining: {remaining}/{limit}, Reset: {reset_time}"
            )

            if remaining <= 5:  # 検索APIの制限は厳しいので、余裕を持たせる
                wait_time = (reset_time - datetime.now()).total_seconds()
                if wait_time > 0:
                    logger.warning(
                        f"Rate limit reached. Waiting for {wait_time:.2f} seconds"
                    )
                    time.sleep(wait_time + 1)  # 1秒の余裕を持たせる
                    return self.check_rate_limit()  # 再帰的にチェック
            return True
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return False

    def get_repo_info(self, repo: Repository) -> Dict:
        """リポジトリの情報を取得"""
        try:
            return {
                "name": repo.full_name,
                "url": repo.html_url,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "language": repo.language,
                "updated_at": repo.updated_at.isoformat(),
                "cursorrules_url": f"{repo.html_url}/blob/master/.cursorrules",
            }
        except Exception as e:
            logger.error(f"Error getting repo info for {repo.full_name}: {e}")
            raise

    def search_repositories(self, query: str) -> List[Repository]:
        """指定されたクエリでリポジトリを検索"""
        try:
            logger.info(f"Searching with query: {query}")
            repos = self.github.search_repositories(
                query=query, sort="stars", order="desc"
            )
            total_count = repos.totalCount
            logger.info(f"Found {total_count} repositories for query: {query}")
            return repos
        except GithubException as e:
            logger.error(f"GitHub API error during search: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            return []

    def collect_data(self) -> bool:
        """CursorRulesを含むリポジトリの情報を収集"""
        print("Collecting repository data...")
        repos_data = []
        max_repos = int(os.getenv("MAX_REPOSITORIES", 100))

        try:
            with tqdm(total=max_repos) as pbar:
                for query in SEARCH_QUERIES:
                    if len(repos_data) >= max_repos:
                        logger.info("Reached maximum repository limit")
                        break

                    if not self.check_rate_limit():
                        logger.error("Rate limit check failed")
                        break

                    repos = self.search_repositories(query)
                    for repo in repos:
                        if len(repos_data) >= max_repos:
                            break

                        if repo.full_name in self.processed_repos:
                            logger.debug(
                                f"Skipping duplicate repository: {repo.full_name}"
                            )
                            continue

                        try:
                            repo_info = self.get_repo_info(repo)
                            repos_data.append(repo_info)
                            self.processed_repos.add(repo.full_name)
                            pbar.update(1)
                            logger.debug(f"Successfully processed: {repo.full_name}")
                        except Exception as e:
                            logger.error(
                                f"Error processing repository {repo.full_name}: {e}"
                            )
                            continue

            if not repos_data:
                logger.warning("No repositories found")
                return False

            # スター数でソート
            repos_data.sort(key=lambda x: x["stars"], reverse=True)

            # データの保存
            data = {
                "last_updated": datetime.utcnow().isoformat(),
                "repositories": repos_data,
            }

            with open(CURSORRULES_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(
                f"Successfully saved {len(repos_data)} repositories to {CURSORRULES_DATA_FILE}"
            )
            return True

        except Exception as e:
            logger.error(f"Error during data collection: {e}", exc_info=True)
            return False


def main():
    try:
        collector = CursorRulesCollector()
        success = collector.collect_data()
        if success:
            print("Data collection completed successfully")
            exit(0)
        else:
            print("Data collection failed")
            exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()
