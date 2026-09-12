import os
import random
from typing import List, Tuple

def split_sessions(sessions: List[str], train_ratio: float = 0.7, val_ratio: float = 0.15, seed: int = 42) -> Tuple[List[str], List[str], List[str]]:
    """
    Splits data by driving session (directory) to prevent data leakage.
    Randomly splitting overlapping windows would leak future information.
    """
    if not sessions:
        return [], [], []
        
    random.seed(seed)
    shuffled = sessions.copy()
    random.shuffle(shuffled)
    
    n = len(shuffled)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)
    
    # If there are very few sessions, ensure at least one per split if possible
    if n >= 3:
        if train_end == 0: train_end = 1
        if val_end == train_end: val_end = train_end + 1
        if val_end >= n: val_end = n - 1
        
    train_sessions = shuffled[:train_end]
    val_sessions = shuffled[train_end:val_end]
    test_sessions = shuffled[val_end:]
    
    # Fallback for very small datasets (e.g. 1 or 2 sessions)
    if n < 3:
        train_sessions = shuffled
        val_sessions = shuffled
        test_sessions = shuffled
        print("WARNING: Insufficient sessions for strict splitting. Using same sessions for Train/Val/Test. DO NOT DO THIS IN PRODUCTION.")
        
    return train_sessions, val_sessions, test_sessions
