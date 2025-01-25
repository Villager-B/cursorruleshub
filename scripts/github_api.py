import json
import os
from datetime import datetime

from config import (
    CURSORRULES_DATA_FILE,
    DATA_DIR,
    GITHUB_TOKEN,
    MAX_TOTAL_ITEMS,
    SEARCH_QUERY,
)
from github import Github
from github.Repository import Repository
from tqdm import tqdm


class CursorRulesCollector:
    def __init__(self):
        self.github = Github(GITHUB_TOKEN)
        self.ensure_data_directory()

    def ensure_data_directory(self):
        """データディレクトリが存在しない場合は作成"""
        os.makedirs(DATA_DIR, exist_ok=True)

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
            repos = self.github.search_code(
                query=SEARCH_QUERY,
                sort="indexed",
                order="desc",
            )

            # プログレスバーの設定
            total_items = min(repos.totalCount, MAX_TOTAL_ITEMS)
            with tqdm(total=total_items) as pbar:
                for i, repo_file in enumerate(repos):
                    if i >= MAX_TOTAL_ITEMS:
                        break

                    try:
                        repo_info = self.get_repo_info(repo_file.repository)
                        repos_data.append(repo_info)
                        pbar.update(1)
                    except Exception as e:
                        print(
                            f"Error processing repository {repo_file.repository.full_name}: {e}"
                        )
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
