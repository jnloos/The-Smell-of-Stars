import os
from dotenv import load_dotenv

from lib.Logger import Logger
from lib.Evaluator import Evaluator

def main():
    # Load .env file
    load_dotenv()

    # Print introduction
    Logger.message('Code Quality Evaluator (© Jan-Niclas Loosen)', color='blue').br()

    # Configuration dialog
    Logger.message('Please provide the JSON files containing "Usual" repositories.', color='blue')
    usual_input = Logger.input('Paths (comma-separated)', cast=str)
    Logger.br()
    Logger.message("Please provide the JSON files containing 'Popular' repositories.", color='blue')
    popular_input = Logger.input('Paths (comma-separated)', cast=str)
    Logger.br()

    # Split each input only by comma
    usual_files = [f.strip() for f in usual_input.split(',')]
    popular_files = [f.strip() for f in popular_input.split(',')]

    evaluator = Evaluator(usual_files, popular_files)
    evaluator.eval()

if __name__ == "__main__":
    main()
