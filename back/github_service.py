import base64
import os
from typing import List, Optional
import httpx
from pathlib import Path


class GitHubService:
    """Service for pushing scan files to GitHub repository."""

    def __init__(self, token: str, owner: str, repo: str, branch: str = "main"):
        """
        Initialize GitHub service.

        Args:
            token: GitHub personal access token
            owner: Repository owner (username or organization)
            repo: Repository name
            branch: Branch name to push to (default: main)
        """
        self.token = token
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.api_base = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def get_file_sha(self, file_path: str) -> Optional[str]:
        """
        Get the SHA of an existing file in the repository.

        Args:
            file_path: Path to file in repository (e.g., 'assets/scans.json')

        Returns:
            SHA string if file exists, None otherwise
        """
        url = f"{self.api_base}/contents/{file_path}"
        params = {"ref": self.branch}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                if response.status_code == 200:
                    return response.json().get("sha")
                return None
            except Exception as e:
                print(f"Error getting SHA for {file_path}: {e}")
                return None

    async def upload_file(self, local_path: str, repo_path: str, commit_message: str) -> bool:
        """
        Upload or update a single file to GitHub.

        Args:
            local_path: Local file path
            repo_path: Path in repository (e.g., 'assets/manga/cover.webp')
            commit_message: Commit message

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read file content
            with open(local_path, 'rb') as f:
                content = f.read()

            # Encode to base64
            content_encoded = base64.b64encode(content).decode('utf-8')

            # Check if file exists and get SHA
            sha = await self.get_file_sha(repo_path)

            # Prepare request
            url = f"{self.api_base}/contents/{repo_path}"
            data = {
                "message": commit_message,
                "content": content_encoded,
                "branch": self.branch
            }

            if sha:
                data["sha"] = sha

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.put(url, headers=self.headers, json=data)

                if response.status_code in [200, 201]:
                    print(f"✓ Uploaded {repo_path}")
                    return True
                else:
                    print(f"✗ Failed to upload {repo_path}: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            print(f"✗ Error uploading {local_path} to {repo_path}: {e}")
            return False

    async def upload_directory(self, local_dir: str, repo_base_path: str, commit_message_prefix: str = "Update") -> int:
        """
        Upload all files in a directory to GitHub.

        Args:
            local_dir: Local directory path
            repo_base_path: Base path in repository (e.g., 'assets')
            commit_message_prefix: Prefix for commit messages

        Returns:
            Number of files successfully uploaded
        """
        uploaded_count = 0

        if not os.path.exists(local_dir):
            print(f"Directory {local_dir} does not exist")
            return 0

        # Walk through directory
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)

                # Calculate relative path from local_dir
                rel_path = os.path.relpath(local_path, local_dir)

                # Convert to repository path
                repo_path = os.path.join(repo_base_path, rel_path).replace('\\', '/')

                # Create commit message
                commit_msg = f"{commit_message_prefix} {rel_path}"

                # Upload file
                if await self.upload_file(local_path, repo_path, commit_msg):
                    uploaded_count += 1

        return uploaded_count

    async def upload_manga(self, manga_dir: str, manga_title: str) -> bool:
        """
        Upload all files for a specific manga to GitHub.

        Args:
            manga_dir: Local directory containing manga files
            manga_title: Title of the manga

        Returns:
            True if at least one file was uploaded successfully
        """
        print(f"\n📤 Uploading manga '{manga_title}' to GitHub...")

        repo_base = f"assets/{manga_title}"
        count = await self.upload_directory(
            manga_dir,
            repo_base,
            f"Update {manga_title}:"
        )

        print(f"✓ Uploaded {count} files for {manga_title}")
        return count > 0

    async def upload_root_json(self, json_path: str) -> bool:
        """
        Upload the root scans.json file to GitHub.

        Args:
            json_path: Local path to scans.json

        Returns:
            True if successful
        """
        print(f"\n📤 Uploading root scans.json to GitHub...")
        return await self.upload_file(
            json_path,
            "assets/scans.json",
            "Update scans.json with new manga entries"
        )

    async def sync_all_assets(self, assets_dir: str) -> bool:
        """
        Sync entire assets directory to GitHub.

        Args:
            assets_dir: Local assets directory path

        Returns:
            True if successful
        """
        print(f"\n📤 Syncing all assets to GitHub...")
        count = await self.upload_directory(
            assets_dir,
            "assets",
            "Update assets:"
        )
        print(f"✓ Synced {count} total files")
        return count > 0
