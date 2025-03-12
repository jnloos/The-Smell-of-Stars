### The Smell of Stars
This small study aims to systematically investigate a possible correlation between the popularity of open source projects – measured by the number of stars – and the quality of the source code. The complete report is included as a PDF.

### Prerequisites
- Python 3.6+
- Required Python libraries (install via `pip install -r requirements.txt`)
- A running SonarQube Community Server instance (e.g. with Docker)
- SonarQube CLI installed and accessible in the system's PATH
- A filled copy of the provided `.env` blueprint, including:
  - GitHub API Key: Required for accessing the GitHub API.
  - SonarQube Key: Required for accessing  the running SonarQube instance.

### Python Scripts
This project contains two main scripts in the `./src` directory:
- **crawl.py:** Crawls GitHub repositories based on filter options and analyzes them using SonarQube.
- **eval.py:** Reads the outputs of the crawled repositories and compares their code quality.


