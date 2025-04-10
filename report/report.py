import multiprocessing
from tqdm import tqdm
import os
import matplotlib.pyplot as plt
import pandas as pd
from game.auto_game import auto_game

def worker(args):
    """Standalone worker function for parallel processing"""
    try:
        alpha, bot, is_rat_moving = args
        g = auto_game(alpha=alpha, bot_type=bot, isUseIpCells=True, is_rat_moving=is_rat_moving)
        return f"{g.t},{alpha},{bot},{is_rat_moving}\n"
    except Exception as e:
        print(f"Error with {args}: {str(e)}")
        return ""

class DataService:
    def __init__(self, isGenerateData: bool, points: int):
        """
        Initialize data service
        :param isGenerateData: True to generate data, False to plot
        :param points: Number of runs per parameter combination
        """
        self.points = points
        self.isGenerateData = isGenerateData

        # Initialize empty dataframe
        self.df = pd.DataFrame(columns=['timesteps', 'alpha', 'bot_number', 'is_rat_moving'])

        # Only load data if not generating new data
        if not isGenerateData:
            file_path = os.path.join("report", "data.txt")
            if os.path.exists(file_path):
                self.df = self._read_data_file(file_path)

    def generateDataParalelly(self):
        """Generate data in parallel and save to file"""
        params = [(round(a / 10, 1), b, m)
                  for a in range(11)  # 0.0 to 1.0 in 0.1 increments
                  for b in [1, 2]  # Both bots
                  for m in [True, False]  # Both movement states
                  for _ in range(self.points)]  # Number of runs

        # Ensure report directory exists
        os.makedirs("report", exist_ok=True)
        file_path = os.path.join("report", "data.txt")

        # Run simulations in parallel
        with multiprocessing.Pool() as pool, \
                open(file_path, "a+") as f:

            # Process results as they complete
            for result in tqdm(pool.imap(worker, params),
                               total=len(params),
                               desc="Running simulations"):
                if result:  # Only write successful results
                    f.write(result)
                    f.flush()

    def _read_data_file(self, file_path):
        """Read data from file into DataFrame"""
        data = []
        with open(file_path, 'r') as file:
            next(file)  # Skip header
            for line in file:
                line = line.strip()
                if line:
                    try:
                        t, alpha, bot, moving = line.split(',')
                        data.append((
                            int(t.strip()),
                            float(alpha.strip()),
                            int(bot.strip()),
                            moving.strip() == 'True'
                        ))
                    except ValueError:
                        continue

        return pd.DataFrame(data, columns=['timesteps', 'alpha', 'bot_number', 'is_rat_moving'])

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
                    is_rat_moving = parts[3].strip() == 'True'
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
