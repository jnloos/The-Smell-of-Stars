import json
import os
import queue
from multiprocessing import Process, Manager
from dotenv import load_dotenv

from lib.Crawler import Crawler
from lib.Logger import Logger
from lib.Sonar import Sonar

def worker(repo_queue, scan_results, results_lock, failed_repos):
    sonar = Sonar()
    while True:
        try:
            repo, attempt = repo_queue.get_nowait()
        except queue.Empty:
            break

        attempt += 1
        result = sonar.scan(repo)

        if len(result) > 0:
            with results_lock:
                scan_results[repo.key()] = result
            Logger.info(f"Evaluated repository {repo.key()} with result: {result}")
        else:
            if attempt < 3:
                Logger.error(f"Failed to evaluate repository {repo.key()} on attempt {attempt}. Re-adding to queue.")
                repo_queue.put((repo, attempt + 1))
            else:
                Logger.error(f"Failed to evaluate repository {repo.key()} after {attempt} attempts.")
                failed_repos.append(repo.key())

def main():
    # Load .env file
    load_dotenv()

    # Print introduction
    Logger.message('"The smell of Stars" — Repository Crawler (© Jan-Niclas Loosen)', color='blue')
    sonar_credit = 'SonarQube Community Edition (https://www.sonarsource.com)'
    github_credit = 'GitHub REST API (https://docs.github.com/en/rest)'
    Logger.message(f"Uses: {sonar_credit} and {github_credit}.").br()

    # Configuration dialog
    Logger.message('Please configure the desired filter options.', 'blue')
    to_crawl = Logger.input('Number of repositories to crawl', cast=int)
    lang = Logger.input('Programming language to consider', cast=str)
    min_stars = Logger.input('Min number of stars:', default=0, cast=int)
    max_stars = Logger.input('Max number of stars:', default=-1, default_alias='unconstrained', cast=int)
    if max_stars < 0:
        max_stars = None

    Logger.br().message('Please specify the file in which the results will be stored.', 'blue')
    rel_path = './out/results/' + Logger.input('Name of the file in ./out/results/', cast=str)
    abs_path = os.path.abspath(rel_path)

    Logger.br().message('All inputs are done. The Repository Crawler is now processing...', 'blue')

    # Crawl repositories
    repos, num = Crawler.init().lang(lang).max_stars(max_stars).min_stars(min_stars).crawl(to_crawl)

    # Set up a Manager for sharing data between processes
    with Manager() as manager:
        scan_results = manager.dict()
        failed_repos = manager.list()
        results_lock = manager.Lock()
        repo_queue = manager.Queue()

        # Enqueue repo and attempt
        for repo in repos.values():
            repo_queue.put((repo, 0))
        num_processes = int(os.getenv('WORKING_THREADS', 4))
        Logger.debug(f"Spawning {num_processes} processes to process the queue.")

        processes = []
        for _ in range(num_processes):
            p = Process(target=worker, args=(repo_queue, scan_results, results_lock, failed_repos))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        if len(failed_repos) > 0:
            Logger.error(f"Evaluation failed for {len(failed_repos)} repositories: {', '.join(failed_repos)}")
        if len(scan_results) > 0:
            Logger.info(f"Evaluation succeeded for {len(scan_results)} repositories.", 'green')

        # Store results in the desired file
        with open(abs_path, "w") as file:
            json.dump(dict(scan_results), file, indent=4)

    # Exit dialog and summary
    Logger.br().message(f"The Repository Crawler is done.", color='blue')
    Logger.message(f"All results have been saved to {abs_path}.")

if __name__ == "__main__":
    main()
