"""Terminal color utilities for enhanced output presentation"""

import sys
from datetime import datetime
from typing import Optional

class Colors:
    """ANSI color codes for terminal output"""
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    STRIKETHROUGH = '\033[9m'
    
    # Reset
    RESET = '\033[0m'
    
    # Common combinations
    SUCCESS = BRIGHT_GREEN + BOLD
    ERROR = BRIGHT_RED + BOLD
    WARNING = BRIGHT_YELLOW + BOLD
    INFO = BRIGHT_BLUE + BOLD
    HEADER = BRIGHT_MAGENTA + BOLD
    SUBHEADER = CYAN + BOLD
    TIMESTAMP = BRIGHT_BLACK
    
def colored_print(text: str, color: str = Colors.WHITE, style: str = "", end: str = "\n"):
    """Print colored text to terminal"""
    if sys.stdout.isatty():  # Only apply colors if output is a terminal
        print(f"{style}{color}{text}{Colors.RESET}", end=end)
    else:
        print(text, end=end)

def print_header(text: str, char: str = "═"):
    """Print a formatted header with separator lines"""
    border = char * len(text)
    colored_print(f"\n{border}", Colors.HEADER)
    colored_print(f"{text}", Colors.HEADER)
    colored_print(f"{border}", Colors.HEADER)

def print_step(step_name: str, status: str = "STARTING", timestamp: Optional[str] = None):
    """Print a processing step with status"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%H:%M:%S")
    
    status_colors = {
        "STARTING": Colors.BRIGHT_YELLOW,
        "RUNNING": Colors.BRIGHT_BLUE,
        "COMPLETED": Colors.SUCCESS,
        "FAILED": Colors.ERROR,
        "SKIPPED": Colors.BRIGHT_BLACK
    }
    
    color = status_colors.get(status.upper(), Colors.WHITE)
    colored_print(f"[{timestamp}] ", Colors.TIMESTAMP, end="")
    colored_print(f"[{status:>9}] ", color, Colors.BOLD, end="")
    colored_print(f"{step_name}", Colors.WHITE)

def print_agent_activity(agent_name: str, action: str, details: str = "", duration: Optional[float] = None):
    """Print agent activity with formatting"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
    
    # Agent name colors
    agent_colors = {
        "generation_agent": Colors.BRIGHT_GREEN,
        "reflection_agent": Colors.BRIGHT_BLUE,
        "ranking_agent": Colors.BRIGHT_YELLOW,
        "evolution_agent": Colors.BRIGHT_MAGENTA,
        "proximity_agent": Colors.BRIGHT_CYAN,
        "meta_review_agent": Colors.BRIGHT_RED
    }
    
    color = agent_colors.get(agent_name, Colors.WHITE)
    
    colored_print(f"  [{timestamp}] ", Colors.TIMESTAMP, end="")
    colored_print(f"🤖 {agent_name.upper().replace('_', ' ')}: ", color, Colors.BOLD, end="")
    colored_print(f"{action}", Colors.WHITE, end="")
    
    if details:
        colored_print(f" - {details}", Colors.BRIGHT_BLACK)
    else:
        colored_print("")
    
    if duration is not None:
        colored_print(f"    ⏱️  Duration: {duration:.2f}s", Colors.TIMESTAMP)

def print_progress_bar(current: int, total: int, prefix: str = "", suffix: str = "", length: int = 30):
    """Print a progress bar"""
    percent = (current / total) * 100 if total > 0 else 0
    filled_length = int(length * current // total) if total > 0 else 0
    bar = '█' * filled_length + '░' * (length - filled_length)
    
    colored_print(f"\r{prefix} |", Colors.WHITE, end="")
    colored_print(f"{bar}", Colors.BRIGHT_GREEN, end="")
    colored_print(f"| {percent:5.1f}% {suffix}", Colors.WHITE, end="")
    
    if current == total:
        print()  # New line when complete

def print_hypothesis_summary(hypothesis_id: str, title: str, scores: dict):
    """Print a formatted hypothesis summary"""
    colored_print(f"  📋 Hypothesis {hypothesis_id[:8]}...", Colors.BRIGHT_CYAN, Colors.BOLD)
    colored_print(f"     Title: {title[:60]}{'...' if len(title) > 60 else ''}", Colors.WHITE)
    
    score_text = " | ".join([
        f"Novelty: {scores.get('novelty', 0):.2f}",
        f"Feasibility: {scores.get('feasibility', 0):.2f}",
        f"Confidence: {scores.get('confidence', 0):.2f}"
    ])
    colored_print(f"     Scores: {score_text}", Colors.BRIGHT_BLACK)

def print_error(message: str, details: str = ""):
    """Print an error message"""
    colored_print(f"❌ ERROR: {message}", Colors.ERROR)
    if details:
        colored_print(f"   Details: {details}", Colors.BRIGHT_BLACK)

def print_success(message: str, details: str = ""):
    """Print a success message"""
    colored_print(f"✅ SUCCESS: {message}", Colors.SUCCESS)
    if details:
        colored_print(f"   {details}", Colors.BRIGHT_GREEN)

def print_warning(message: str, details: str = ""):
    """Print a warning message"""
    colored_print(f"⚠️  WARNING: {message}", Colors.WARNING)
    if details:
        colored_print(f"   {details}", Colors.BRIGHT_YELLOW)

def print_info(message: str, details: str = ""):
    """Print an info message"""
    colored_print(f"ℹ️  INFO: {message}", Colors.INFO)
    if details:
        colored_print(f"   {details}", Colors.BRIGHT_BLUE)

def print_separator(char: str = "─", length: int = 80):
    """Print a separator line"""
    colored_print(char * length, Colors.BRIGHT_BLACK)