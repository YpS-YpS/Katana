"""
Katana Game Benchmark Automation Framework - Main Entry Point

This is the main entry point for the Katana benchmark framework.
It parses command line arguments and orchestrates the benchmark execution.
"""
import sys
import time
import argparse
import logging
from pathlib import Path
from colorama import init, Fore, Style

from .factory import GameFactory

# Initialize colorama for colored terminal output
init(autoreset=True)

# Configure logger
# Find the logging configuration section in katana/main.py
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(stream=sys.stdout),  # Specify stdout as the stream
        logging.FileHandler("katana_benchmark.log", encoding="utf-8")  # Specify UTF-8 encoding
    ]
)

logger = logging.getLogger("katana")

def print_banner():
    """Print the Katana framework banner"""
    print(Fore.GREEN + Style.BRIGHT + """
 ██╗  ██╗ █████╗ ████████╗ █████╗ ███╗   ██╗ █████╗ 
 ██║ ██╔╝██╔══██╗╚══██╔══╝██╔══██╗████╗  ██║██╔══██╗
 █████╔╝ ███████║   ██║   ███████║██╔██╗ ██║███████║
 ██╔═██╗ ██╔══██║   ██║   ██╔══██║██║╚██╗██║██╔══██║
 ██║  ██╗██║  ██║   ██║   ██║  ██║██║ ╚████║██║  ██║
 ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
                                                     
 Game Benchmark Automation Framework
    """)

def parse_args():
    """Parse command line arguments
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    # Get available games
    available_games = GameFactory.get_available_games()
    
    parser = argparse.ArgumentParser(description="Katana Game Benchmark Automation Framework")
    
    parser.add_argument("--game", "-g", type=str, choices=available_games,
                      help=f"Game to benchmark: {', '.join(available_games)}")
    
    parser.add_argument("--runs", "-r", type=int, default=None,
                      help="Number of benchmark runs (default from game config)")
    
    parser.add_argument("--cooldown", "-c", type=int, default=None,
                      help="Cooldown between runs in seconds (default from game config)")
    
    parser.add_argument("--list", "-l", action="store_true",
                      help="List available games")
    
    return parser.parse_args()

def prompt_for_game(available_games):
    """Prompt user to select a game
    
    Args:
        available_games (list): List of available games
        
    Returns:
        str: Selected game ID
    """
    print("\n🎮 Available games:")
    for i, game in enumerate(available_games):
        print(f"  {i+1}. {game}")
    
    while True:
        try:
            choice = input("\n🎯 Enter game number to benchmark: ").strip()
            index = int(choice) - 1
            if 0 <= index < len(available_games):
                return available_games[index]
            else:
                print(f"❌ Invalid choice. Please enter a number between 1 and {len(available_games)}.")
        except ValueError:
            print("❌ Please enter a valid number.")

def prompt_for_runs():
    """Prompt user for number of benchmark runs
    
    Returns:
        int: Number of runs
    """
    while True:
        try:
            runs = int(input("📝 Enter number of benchmark runs: ").strip())
            if runs > 0:
                return runs
            else:
                print("❌ Number of runs must be greater than 0.")
        except ValueError:
            print("❌ Please enter a valid number.")

def prompt_for_cooldown():
    """Prompt user for cooldown between runs
    
    Returns:
        int: Cooldown in seconds
    """
    while True:
        try:
            cooldown = int(input("🕒 Enter cooldown between runs (seconds): ").strip())
            if cooldown >= 0:
                return cooldown
            else:
                print("❌ Cooldown must be non-negative.")
        except ValueError:
            print("❌ Please enter a valid number.")

def main():
    """Main entry point"""
    print_banner()
    
    # Parse command line arguments
    args = parse_args()
    
    # List available games if requested
    if args.list:
        available_games = GameFactory.get_available_games()
        print("\n🎮 Available games:")
        for game in available_games:
            print(f"  - {game}")
        return 0
    
    # Get available games
    available_games = GameFactory.get_available_games()
    
    if not available_games:
        print("❌ No game benchmark implementations found.")
        return 1
    
    # Get game to benchmark
    game_id = args.game
    if game_id is None:
        game_id = prompt_for_game(available_games)
    
    print(f"\n🎮 Selected game: {game_id}")
    
    try:
        # Create benchmark instance
        benchmark = GameFactory.create_benchmark(game_id)
        
        # Get benchmark parameters
        runs = args.runs
        if runs is None:
            if hasattr(benchmark, 'configs') and 'default_runs' in benchmark.configs:
                runs = benchmark.configs['default_runs']
                print(f"📌 Using default runs from config: {runs}")
            else:
                runs = prompt_for_runs()
        
        cooldown = args.cooldown
        if cooldown is None:
            if hasattr(benchmark, 'configs') and 'cooldown' in benchmark.configs:
                cooldown = benchmark.configs['cooldown']
                print(f"📌 Using default cooldown from config: {cooldown}s")
            else:
                cooldown = prompt_for_cooldown()
        
        print(f"\n⚙️ Benchmark configuration:")
        print(f"  - Game: {benchmark.game_name}")
        print(f"  - Runs: {runs}")
        print(f"  - Cooldown: {cooldown}s")
        
        print("\n🚀 Starting benchmark series...")
        
        # Run benchmark series
        results = benchmark.run_benchmark_series(run_count=runs, cooldown=cooldown)
        
        print("\n✅ Benchmark completed successfully!")
        print(f"📊 Results saved to the 'results' directory")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Error during benchmark execution: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())