import os
import subprocess
import time

import requests

from lib.Repository import Repository
from lib.Logger import Logger


class Sonar:
    # SonarQube credentials
    sonar_url = None
    sonar_token = None

    def __init__(self):
        self.sonar_url = os.getenv("SONARQUBE_URL")
        self.sonar_token = os.getenv("SONARQUBE_TOKEN")

    def __sonar_qube_scan(self, repo: Repository) -> None:
        sources = repo.path()
        if not sources:
            Logger.error("Repository path not found. Please download the repository first.")
            return

        # Add exclusions for file extensions that require compilation.
        exclusions = (
            "**/*.java,**/*.cs,**/*.cpp,**/*.cc,**/*.cxx,**/*.c,**/*.scala,"
            "**/*.kt,**/*.kts,**/*.swift,**/*.m,**/*.mm,**/*.rs,**/*.vb,**/*.vbs"
        )

        command = (
            f'sonar-scanner '
            f'-Dsonar.projectKey="{repo.key()}" '
            f'-Dsonar.projectName="{repo.name}" '
            f'-Dsonar.sources="{repo.path()}" '
            f'-Dsonar.projectBaseDir="{repo.path()}" '
            f'-Dsonar.host.url="{self.sonar_url}" '
            f'-Dsonar.login="{self.sonar_token}" '
            f'-Dsonar.exclusions="{exclusions}"'
        )

        Logger.debug(f"Running sonar-scanner for project {repo.key()} with exclusions: {exclusions}")
        try:
            subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=repo.path()
            )
        except subprocess.CalledProcessError as e:
            Logger.error(f"Error running sonar-scanner: {e}")

    def __sonar_qube_info(self, repo: Repository) -> dict:
        Logger.debug(f"Fetching evaluated metrics for project {repo.key()}...")

        max_wait = 120
        interval = 5
        waited = 0
        url = f"{self.sonar_url}/api/measures/component"
        measures_params = {
            "component": repo.key(),
            "metricKeys": "ncloc,cognitive_complexity,code_smells"
        }

        measures = []
        while waited < max_wait:
            response = requests.get(url, params=measures_params, auth=(self.sonar_token, ""))
            result = response.json()
            measures = result.get("component", {}).get("measures", [])
            if measures:
                break
            time.sleep(interval)
            waited += interval

        result = {}
        if measures:
            for measure in measures:
                metric_key = measure.get("metric")
                value = measure.get("value", "0")
                result[metric_key] = value
        else:
            Logger.error(f"No measures found for project {repo.key()} after polling.")

        return result

    def __sonar_qube_clean(self, repo: Repository) -> None:
        Logger.debug(f"Clearing previous SonarQube project {repo.key()}")
        url = f"{self.sonar_url}/api/projects/delete"
        params = {"project": repo.key()}
        response = requests.post(url, params=params, auth=(self.sonar_token, ""))

        if response.status_code not in (200, 204):
            Logger.error(f"Error deleting project {repo.key()}: {response.status_code}")

    def scan(self, repo: Repository) -> dict:
        # Download and scan repository
        repo.download()
        self.__sonar_qube_scan(repo)

        # Evaluate repository
        result = self.__sonar_qube_info(repo)
        if len(result) == 0:
            return result

        # Include normalized metrics (per NCLOC) and stars
        summary = {'stars': repo.stars}
        summary.update(result)
        ncloc = float(summary.get('ncloc', 0))
        if ncloc > 0:
            code_smells = float(summary.get('code_smells', 0))
            cognitive_complexity = float(summary.get('cognitive_complexity', 0))
            summary['norm_code_smells'] = str(code_smells / ncloc)
            summary['norm_cognitive_complexity'] = str(cognitive_complexity / ncloc)
        else:
            summary['norm_code_smells'] = '0'
            summary['norm_cognitive_complexity'] = '0'

        # Clean files and project
        repo.clean()
        self.__sonar_qube_clean(repo)

        return summary

