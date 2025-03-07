import os
import shutil
import stat
import subprocess

from lib.Logger import Logger

class Repository:
    # Repository information
    url = None
    name = None
    author = None
    lang = None
    stars = 0

    # Download status
    __download_status = False

    def __init__(self, url: str = None, name: str = None, author: str = None, stars: int = 0, lang: str = None):
        self.url = url
        self.name = name
        self.author = author
        self.stars = stars
        self.lang = lang

    def key(self):
        return f"{self.author}:{self.name}"

    def download(self) -> None:
        if not self.__download_status:
            repo_path = self.__destination()

            # Clear path, if it is already existing
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)

            # Create directory and download repository
            os.makedirs(os.path.dirname(repo_path), exist_ok=True)
            try:
                command = f"git clone {self.url} {repo_path}"
                subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                Logger.debug(f"Repository cloned to {repo_path}")
                self.__download_status = True
            except subprocess.CalledProcessError as e:
                Logger.error(f"Error downloading repository {self.name}: {e}")

    def __destination(self):
        base_dir = os.path.abspath("out/repos")
        file = self.key().replace(':', '-')
        return os.path.join(base_dir, file)

    def path(self) -> str | None:
        if self.__download_status:
            return self.__destination()
        return None

    def handle_remove_readonly(self, func, path, exc_info):
        os.chmod(self.path(), stat.S_IWRITE)
        func(path)

    @staticmethod
    def __fix_perms(func, path, exc_info):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def clean(self) -> None:
        repo_path = self.__destination()
        if os.path.exists(repo_path):
            try:
                shutil.rmtree(repo_path, onerror=self.__fix_perms)
                Logger.debug(f"Repository cleaned: {repo_path}")
            except Exception as e:
                Logger.error(f"Error cleaning repository {repo_path}: {e}")
            self.__download_status = False

