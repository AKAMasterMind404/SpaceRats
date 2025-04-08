import matplotlib.pyplot as plt
import pandas as pd
import os
from game.auto_game import auto_game


class DataService:
    def __init__(self, isGenerateData: bool, points):
        """
        Initialize by reading data from file
        """
        file_path = os.path.join(os.getcwd(), "report", "data.txt")
        self.df = self._read_data_file(file_path)
        self.points = points
        self.isGenerateData = isGenerateData

    def generate_data(self):
        points = self.points
        file = open(os.getcwd() + "\\report\\data.txt", 'a+')
        for alpha in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1] * points:
            for isRatMoving in [True, False]:
                for bot in [1, 2]:
                    g = auto_game(alpha=alpha, bot_type=bot, isUseIpCells=True, is_rat_moving=isRatMoving)
                    file.write(f"{g.t}, {alpha}, {bot}, {isRatMoving}\n")
                    print(f"{g.t}, {alpha}, {bot}, {isRatMoving}\n")

    def _read_data_file(self, file_path):
        """
        Read data from the specified file
        """
        data = []
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(",")
                    timesteps = int(parts[0])
                    alpha = float(parts[1])
                    bot_number = int(parts[2])
                    is_rat_moving = parts[3] == 'True'
                    data.append((timesteps, alpha, bot_number, is_rat_moving))

        columns = ['timesteps', 'alpha', 'bot_number', 'is_rat_moving']
        return pd.DataFrame(data, columns=columns)

    def _prepare_plot_data(self, movement_condition=None, bot_number=None):
        """
        Prepare data for plotting with optional filters
        """
        filtered = self.df.copy()
        if movement_condition is not None:
            filtered = filtered[filtered['is_rat_moving'] == movement_condition]
        if bot_number is not None:
            filtered = filtered[filtered['bot_number'] == bot_number]
        return filtered.groupby('alpha')['timesteps'].mean().reset_index()

    def plot_moving_rat(self):
        """Plot graph for when rat is moving, comparing bot1 vs bot2"""
        bot1_data = self._prepare_plot_data(True, 1)
        bot2_data = self._prepare_plot_data(True, 2)

        plt.figure(figsize=(10, 6))
        plt.plot(bot1_data['alpha'], bot1_data['timesteps'],
                 marker='o', linestyle='-', color='blue', label='Bot 1')
        plt.plot(bot2_data['alpha'], bot2_data['timesteps'],
                 marker='s', linestyle='--', color='green', label='Bot 2')

        plt.title('Performance When Rat is Moving: Bot 1 vs Bot 2')
        plt.xlabel('Alpha Value')
        plt.ylabel('Average Timesteps Taken')
        plt.grid(True)
        plt.legend()
        plt.xticks([i / 10 for i in range(0, 11)])
        plt.show()

    def plot_stationary_rat(self):
        """Plot graph for when rat is stationary, comparing bot1 vs bot2"""
        bot1_data = self._prepare_plot_data(False, 1)
        bot2_data = self._prepare_plot_data(False, 2)

        plt.figure(figsize=(10, 6))
        plt.plot(bot1_data['alpha'], bot1_data['timesteps'],
                 marker='o', linestyle='-', color='red', label='Bot 1')
        plt.plot(bot2_data['alpha'], bot2_data['timesteps'],
                 marker='s', linestyle='--', color='purple', label='Bot 2')

        plt.title('Performance When Rat is Stationary: Bot 1 vs Bot 2')
        plt.xlabel('Alpha Value')
        plt.ylabel('Average Timesteps Taken')
        plt.grid(True)
        plt.legend()
        plt.xticks([i / 10 for i in range(0, 11)])
        plt.show()

    def plot_combined(self):
        """Plot combined graph with all 4 combinations"""
        # Get all four data combinations
        moving_bot1 = self._prepare_plot_data(True, 1)
        moving_bot2 = self._prepare_plot_data(True, 2)
        stationary_bot1 = self._prepare_plot_data(False, 1)
        stationary_bot2 = self._prepare_plot_data(False, 2)

        plt.figure(figsize=(12, 7))

        # Plot lines with different styles for each combination
        plt.plot(moving_bot1['alpha'], moving_bot1['timesteps'],
                 marker='o', linestyle='-', color='blue', label='Moving Rat, Bot 1')
        plt.plot(moving_bot2['alpha'], moving_bot2['timesteps'],
                 marker='s', linestyle='-', color='cyan', label='Moving Rat, Bot 2')
        plt.plot(stationary_bot1['alpha'], stationary_bot1['timesteps'],
                 marker='o', linestyle='--', color='red', label='Stationary Rat, Bot 1')
        plt.plot(stationary_bot2['alpha'], stationary_bot2['timesteps'],
                 marker='s', linestyle='--', color='orange', label='Stationary Rat, Bot 2')

        plt.title('Performance Comparison: All Conditions')
        plt.xlabel('Alpha Value')
        plt.ylabel('Average Timesteps Taken')
        plt.grid(True)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks([i / 10 for i in range(0, 11)])
        plt.tight_layout()
        plt.show()
