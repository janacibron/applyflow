"""Application lifecycle state machine.

States:
  DRAFT      — created, not yet sent
  SENT       — submitted to employer
  VIEWED     — employer opened it
  RESPONDED  — employer replied
  INTERVIEW  — interview scheduled
  OFFER      — offer received
  HIRED      — accepted offer
  REJECTED   — employer declined
  WITHDRAWN  — user withdrew
  CLOSED     — expired or manually closed

Each transition specifies which actor may trigger it.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, List, Tuple

STATES = [
    'DRAFT', 'SENT', 'VIEWED', 'RESPONDED', 'INTERVIEW',
    'OFFER', 'HIRED', 'REJECTED', 'WITHDRAWN', 'CLOSED'
]

# (new_state, actor) — actor: user | employer | system | any
TRANSITIONS: Dict[str, List[Tuple[str, str]]] = {
    'DRAFT': [
        ('SENT', 'user'),
        ('CLOSED', 'user'),
        ('CLOSED', 'system'),
    ],
    'SENT': [
        ('VIEWED', 'employer'),
        ('RESPONDED', 'employer'),
        ('REJECTED', 'employer'),
        ('WITHDRAWN', 'user'),
        ('CLOSED', 'system'),
    ],
    'VIEWED': [
        ('RESPONDED', 'employer'),
        ('REJECTED', 'employer'),
        ('WITHDRAWN', 'user'),
        ('CLOSED', 'system'),
    ],
    'RESPONDED': [
        ('INTERVIEW', 'employer'),
        ('REJECTED', 'employer'),
        ('WITHDRAWN', 'user'),
        ('CLOSED', 'system'),
    ],
    'INTERVIEW': [
        ('OFFER', 'employer'),
        ('REJECTED', 'employer'),
        ('WITHDRAWN', 'user'),
        ('CLOSED', 'system'),
    ],
    'OFFER': [
        ('HIRED', 'user'),
        ('REJECTED', 'user'),
        ('WITHDRAWN', 'user'),
        ('CLOSED', 'system'),
    ],
    'HIRED': [],  # terminal
    'REJECTED': [
        ('CLOSED', 'user'),
        ('CLOSED', 'system'),
    ],
    'WITHDRAWN': [
        ('CLOSED', 'user'),
        ('CLOSED', 'system'),
    ],
    'CLOSED': [],  # terminal
}

TERMINAL_STATES = {'HIRED', 'CLOSED'}


def is_valid_transition(current: str, new: str, actor: str = 'user') -> bool:
    """Check if a transition is valid."""
    if current not in TRANSITIONS:
        return False
    allowed = TRANSITIONS[current]
    for state, allowed_actor in allowed:
        if state == new and (allowed_actor == actor or allowed_actor == 'any'):
            return True
    return False


def can_transition(current: str, new: str, actor: str = 'user') -> Tuple[bool, str]:
    """Return (ok, reason)."""
    if current not in STATES:
        return False, f'Unknown current state: {current}'
    if new not in STATES:
        return False, f'Unknown new state: {new}'
    if current in TERMINAL_STATES:
        return False, f'Cannot transition from terminal state: {current}'
    if not is_valid_transition(current, new, actor):
        return False, f'Invalid transition: {current} -> {new} for actor {actor}'
    return True, ''


def transition_application(app: dict, new_state: str, actor: str = 'user',
                           reason: Optional[str] = None) -> Tuple[dict, str]:
    """Apply a transition. Returns (updated_app, error)."""
    current = app.get('status', 'DRAFT')
    ok, err = can_transition(current, new_state, actor)
    if not ok:
        return app, err

    app['status'] = new_state
    app['status_updated_at'] = datetime.now(timezone.utc).isoformat()

    history = app.get('status_history', [])
    entry = {
        'from': current,
        'to': new_state,
        'actor': actor,
        'at': app['status_updated_at'],
    }
    if reason:
        entry['reason'] = reason
    history.append(entry)
    app['status_history'] = history

    if new_state == 'REJECTED' and reason:
        app['rejection_reason'] = reason
    if new_state == 'WITHDRAWN' and reason:
        app['withdrawal_reason'] = reason

    return app, ''


def get_allowed_transitions(current: str, actor: str = 'user') -> List[str]:
    """Get list of states reachable from current for actor."""
    if current not in TRANSITIONS:
        return []
    return [s for s, a in TRANSITIONS[current] if a == actor or a == 'any']
