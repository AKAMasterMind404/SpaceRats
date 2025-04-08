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
        :param file_path: Path to the data file
        :return: DataFrame with the loaded data
        """
        data = []
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:  # Skip empty lines
                    parts = line.split(",")
                    # Convert each part to appropriate type
                    timesteps = int(parts[0])
                    alpha = float(parts[1])
                    bot_number = int(parts[2])
                    is_rat_moving = parts[3] == 'True'
                    data.append((timesteps, alpha, bot_number, is_rat_moving))

        columns = ['timesteps', 'alpha', 'bot_number', 'is_rat_moving']
        return pd.DataFrame(data, columns=columns)

    def _prepare_plot_data(self, movement_condition):
        """
        Prepare data for plotting based on movement condition
        :param movement_condition: True or False
        :return: DataFrame grouped by alpha with mean timesteps
        """
        filtered = self.df[self.df['is_rat_moving'] == movement_condition]
        return filtered.groupby('alpha')['timesteps'].mean().reset_index()

    def plot_moving_rat(self):
        """Plot graph for when rat is moving (is_rat_moving=True)"""
        plot_data = self._prepare_plot_data(True)
        plt.figure(figsize=(10, 6))
        plt.plot(plot_data['alpha'], plot_data['timesteps'],
                 marker='o', linestyle='-', color='blue')
        plt.title('Performance When Rat is Moving')
        plt.xlabel('Alpha Value')
        plt.ylabel('Average Timesteps Taken')
        plt.grid(True)
        plt.xticks([i / 10 for i in range(0, 11)])
        plt.show()

    def plot_stationary_rat(self):
        """Plot graph for when rat is stationary (is_rat_moving=False)"""
        plot_data = self._prepare_plot_data(False)
        plt.figure(figsize=(10, 6))
        plt.plot(plot_data['alpha'], plot_data['timesteps'],
                 marker='o', linestyle='-', color='red')
        plt.title('Performance When Rat is Stationary')
        plt.xlabel('Alpha Value')
        plt.ylabel('Average Timesteps Taken')
        plt.grid(True)
        plt.xticks([i / 10 for i in range(0, 11)])
        plt.show()

    def plot_combined(self):
        """Plot combined graph showing both moving and stationary conditions"""
        moving_data = self._prepare_plot_data(True)
        stationary_data = self._prepare_plot_data(False)

        plt.figure(figsize=(10, 6))
        plt.plot(moving_data['alpha'], moving_data['timesteps'],
                 marker='o', linestyle='-', color='blue', label='Rat Moving')
        plt.plot(stationary_data['alpha'], stationary_data['timesteps'],
                 marker='o', linestyle='-', color='red', label='Rat Stationary')

        plt.title('Performance Comparison: Moving vs Stationary Rat')
        plt.xlabel('Alpha Value')
        plt.ylabel('Average Timesteps Taken')
        plt.grid(True)
        plt.legend()
        plt.xticks([i / 10 for i in range(0, 11)])
        plt.show()
