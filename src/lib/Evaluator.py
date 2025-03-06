import json
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

from lib.Logger import Logger

class Evaluator:
    def __init__(self, usual_files, popular_files):
        self.usual_data = None
        self.popular_data = None

        self.load(usual_files, popular_files)

    def load(self, usual_files, popular_files):
        usual_data = []
        for file in usual_files:
            data = self.__load_json(path=file)
            usual_data.append(data)
        self.usual_data = pd.concat(usual_data, ignore_index=True)

        popular_data = []
        for file in popular_files:
            data = self.__load_json(path=file)
            popular_data.append(data)
        self.popular_data = pd.concat(popular_data, ignore_index=True)

    @staticmethod
    def __load_json(path):
        Logger.debug(f"Loading data from {path}")

        # Try to load JSON file
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except Exception as e:
            Logger.error(f"Error loading file {path}: {e}")
            return pd.DataFrame()

        # Try to load data from JSON file
        records = []
        for repo, metrics in data.items():
            try:
                record = {
                    'repo': repo,
                    'smells': float(metrics['norm_code_smells']),
                    'complexity': float(metrics['norm_cognitive_complexity'])
                }
                records.append(record)
            except Exception as e:
                Logger.error(f"Error processing repository {repo} in {path}: {e}")
        return pd.DataFrame(records)

    def describe(self):
        stats_usual = self.usual_data[['smells', 'complexity']].describe()
        stats_popular = self.popular_data[['smells', 'complexity']].describe()
        return {'usual': stats_usual, 'popular': stats_popular}

    def mann_whitney(self):
        usual_smells = self.usual_data['smells']
        popular_smells = self.popular_data['smells']

        usual_cmplx = self.usual_data['complexity']
        popular_cmplx = self.popular_data['complexity']

        u_smells, p_smells = mannwhitneyu(usual_smells, popular_smells, alternative='two-sided')
        u_cmplx, p_cmplx = mannwhitneyu(usual_cmplx, popular_cmplx, alternative='two-sided')

        return {
            'smells': {'u': u_smells, 'p': p_smells},
            'complexity': {'u': u_cmplx, 'p': p_cmplx}
        }

    def boxplots(self, show:bool = True, save:bool = False):
        data_smells = [self.usual_data['smells'], self.popular_data['smells']]
        data_cmplx = [self.usual_data['complexity'], self.popular_data['complexity']]

        # Prepare code smells diagram
        plt.figure()
        plt.boxplot(data_smells, labels=['Usual', 'Popular'])
        plt.title('Bad Smells (per NCLOC)')
        plt.ylabel('Normed Value')

        # Save and/or show
        if save:
            plt.savefig('./out/smells_boxplot.png', bbox_inches='tight')
        if show:
            plt.show()

        # Prepare complexity diagram
        plt.figure()
        plt.boxplot(data_cmplx, labels=['Usual', 'Popular'])
        plt.title('Cognitive Complexity (per NCLOC)')
        plt.ylabel('Normed Value')

        # Save and/or show
        if save:
            plt.savefig('./out/smells_boxplot.png', bbox_inches='tight')
        if show:
            plt.show()

    def eval(self):
        Logger.message('Descriptive Statistics:', color='blue')
        stats = self.describe()

        if stats:
            usual_count = stats['usual'].loc['count', 'smells']
            popular_count = stats['popular'].loc['count', 'smells']

            # Remove the 'count' row from both DataFrames
            stats['usual'].drop(index='count', inplace=True)
            stats['popular'].drop(index='count', inplace=True)

            Logger.message(f"Usual Repositories (Count: {int(usual_count)}):")
            print(stats['usual'].to_string())
            Logger.br()

            Logger.message(f"Popular Repositories (Count: {int(popular_count)}):")
            print(stats['popular'].to_string())
            Logger.br()

        result = self.mann_whitney()
        Logger.message('Mann-Whitney U-Test Results:', color='blue')
        for metric, res in result.items():
            print(f"{metric}: U-Statistic = {res['u']}, p-Value = {res['p']}")

        self.boxplots()



