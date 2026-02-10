"""
Resume manager - Save/load download state to resume interrupted downloads.
"""

import json
import os
from datetime import date, datetime


STATE_FILE = '.download_state.json'


def _date_to_str(d):
    return d.isoformat()


def _str_to_date(s):
    return date.fromisoformat(s)


def save_state(output_dir, symbol, completed_dates, all_dates):
    """Save current download state to JSON file."""
    state_path = os.path.join(output_dir, STATE_FILE)

    # Load existing state
    state = {}
    if os.path.exists(state_path):
        with open(state_path, 'r') as f:
            state = json.load(f)

    state[symbol] = {
        'completed': [_date_to_str(d) for d in completed_dates],
        'total': [_date_to_str(d) for d in all_dates],
        'updated': datetime.now().isoformat(),
    }

    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)


def load_state(output_dir, symbol):
    """
    Load previous download state.
    Returns set of completed dates, or empty set if no state exists.
    """
    state_path = os.path.join(output_dir, STATE_FILE)

    if not os.path.exists(state_path):
        return set()

    try:
        with open(state_path, 'r') as f:
            state = json.load(f)

        if symbol in state:
            return {_str_to_date(d) for d in state[symbol]['completed']}
    except (json.JSONDecodeError, KeyError):
        pass

    return set()


def clear_state(output_dir, symbol=None):
    """Clear download state after successful completion."""
    state_path = os.path.join(output_dir, STATE_FILE)

    if not os.path.exists(state_path):
        return

    if symbol is None:
        os.remove(state_path)
        return

    try:
        with open(state_path, 'r') as f:
            state = json.load(f)
        if symbol in state:
            del state[symbol]
        if state:
            with open(state_path, 'w') as f:
                json.dump(state, f, indent=2)
        else:
            os.remove(state_path)
    except (json.JSONDecodeError, KeyError):
        pass
