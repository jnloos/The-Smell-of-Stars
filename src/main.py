from lib.Crawler import Crawler
from lib.Sonar import Sonar
from lib.Logger import Logger
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Crawl repos
repos = Crawler.init().lang('python').min_stars(400).crawl(10)

scanner = Sonar()
for key, repo in repos.items():
    results = scanner.scan(repo)
    Logger.info(f"Results for {repo.key()}: {results}", color='green')
