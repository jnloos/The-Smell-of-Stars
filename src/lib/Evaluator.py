import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu, linregress

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
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except Exception as e:
            Logger.error(f"Error loading file {path}: {e}")
            return pd.DataFrame()

        records = []
        for repo, metrics in data.items():
            try:
                record = {
                    'repo': repo,
                    'stars': float(metrics['stars']),
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

    @staticmethod
    def __log_regression(x_data, y_data, num_points=200):
        log_x_data = np.log10(x_data)
        slope, intercept, _, _, _ = linregress(log_x_data, y_data)

        log_x_line = np.linspace(log_x_data.min(), log_x_data.max(), num_points)
        y_line = slope * log_x_line + intercept
        x_line = 10 ** log_x_line

        return x_line, y_line, slope, intercept

    def scatter_plots(self, show=True, save=False):
        plt.figure()
        ax1 = plt.gca()
        ax1.set_xscale('log')

        # Draw a scatter plot
        ax1.scatter(self.usual_data['stars'], self.usual_data['smells'], color='blue', label='Usual Repos')
        ax1.scatter(self.popular_data['stars'], self.popular_data['smells'], color='red', label='Popular Repos')

        # Use the logarithmic regression for the best-fit line in log space
        stars_combined = pd.concat([self.usual_data['stars'], self.popular_data['stars']])
        smells_combined = pd.concat([self.usual_data['smells'], self.popular_data['smells']])
        x_line_s, y_line_s, slope_s, intercept_s = Evaluator.__log_regression(stars_combined, smells_combined)
        ax1.plot(x_line_s, y_line_s, color='gray', label='Trend Line')

        ax1.set_title('Stars (log scale) vs. Smells')
        ax1.set_xlabel('Stars (log-scale)')
        ax1.set_ylabel('Bad Smells (normed)')
        ax1.legend()

        if save:
            plt.savefig('./out/stars_vs_smells_logx.png', bbox_inches='tight')
        if show:
            plt.show()

        plt.figure()
        ax2 = plt.gca()
        ax2.set_xscale('log')

        # Draw a scatter plot
        ax2.scatter(self.usual_data['stars'], self.usual_data['complexity'], color='blue', label='Usual Repos')
        ax2.scatter(self.popular_data['stars'], self.popular_data['complexity'], color='red', label='Popular Repos')

        # Use the logarithmic regression for the best-fit line in log space
        stars_combined2 = pd.concat([self.usual_data['stars'], self.popular_data['stars']])
        complexity_combined = pd.concat([self.usual_data['complexity'], self.popular_data['complexity']])
        x_line_c, y_line_c, slope_c, intercept_c = Evaluator.__log_regression(stars_combined2, complexity_combined)
        ax2.plot(x_line_c, y_line_c, color='gray', label='Trend Line')

        ax2.set_title('Stars (log scale) vs. Cognitive Complexity')
        ax2.set_xlabel('Stars (log-scale)')
        ax2.set_ylabel('Cognitive Complexity (normed)')
        ax2.legend()

        if save:
            plt.savefig('./out/stars_vs_complexity_logx.png', bbox_inches='tight')
        if show:
            plt.show()

    def box_plots(self, show: bool = True, save: bool = False):
        data_smells = [self.usual_data['smells'], self.popular_data['smells']]
        data_cmplx = [self.usual_data['complexity'], self.popular_data['complexity']]

        plt.figure()
        bplot_smells = plt.boxplot(data_smells, labels=['Usual', 'Popular'], patch_artist=True)
        plt.title('Bad Smells (per NCLOC)')
        plt.ylabel('Normed Value')

        bplot_smells['boxes'][0].set_facecolor('blue')  # Usual
        bplot_smells['boxes'][1].set_facecolor('red')   # Popular

        for median in bplot_smells['medians']:
            median.set_color('white')
        for whisker in bplot_smells['whiskers']:
            whisker.set_color('black')
        for cap in bplot_smells['caps']:
            cap.set_color('black')

        if save:
            plt.savefig('./out/smells_boxplot.png', bbox_inches='tight')
        if show:
            plt.show()

        plt.figure()
        bplot_cmplx = plt.boxplot(data_cmplx, labels=['Usual', 'Popular'], patch_artist=True)
        plt.title('Cognitive Complexity (per NCLOC)')
        plt.ylabel('Normed Value')

        bplot_cmplx['boxes'][0].set_facecolor('blue')  # Usual
        bplot_cmplx['boxes'][1].set_facecolor('red')   # Popular

        for median in bplot_cmplx['medians']:
            median.set_color('white')
        for whisker in bplot_cmplx['whiskers']:
            whisker.set_color('black')
        for cap in bplot_cmplx['caps']:
            cap.set_color('black')

        if save:
            plt.savefig('./out/complexity_boxplot.png', bbox_inches='tight')
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

        self.box_plots()
        self.scatter_plots()
