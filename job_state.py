"""Job lifecycle state machine.

States:
  SCRAPED       — scraped from external source
  PENDING_REVIEW — awaiting moderation
  APPROVED      — approved by admin/moderator
  PUBLISHED     — visible to users
  ACTIVE        — actively accepting applications
  PAUSED        — temporarily hidden
  FILLED        — position filled
  EXPIRED       — past deadline
  REJECTED      — rejected by moderator
  CLOSED        — manually closed
"""
from datetime import datetime, timezone
from typing import Optional, Dict, List, Tuple

STATES = [
    'SCRAPED', 'PENDING_REVIEW', 'APPROVED', 'PUBLISHED', 'ACTIVE',
    'PAUSED', 'FILLED', 'EXPIRED', 'REJECTED', 'CLOSED'
]

# (new_state, actor) — actor: scraper | moderator | employer | system | any
TRANSITIONS: Dict[str, List[Tuple[str, str]]] = {
    'SCRAPED': [
        ('PENDING_REVIEW', 'scraper'),
        ('REJECTED', 'moderator'),
        ('CLOSED', 'system'),
    ],
    'PENDING_REVIEW': [
        ('APPROVED', 'moderator'),
        ('REJECTED', 'moderator'),
        ('CLOSED', 'system'),
    ],
    'APPROVED': [
        ('PUBLISHED', 'moderator'),
        ('REJECTED', 'moderator'),
        ('CLOSED', 'system'),
    ],
    'PUBLISHED': [
        ('ACTIVE', 'system'),
        ('PAUSED', 'employer'),
        ('CLOSED', 'employer'),
        ('CLOSED', 'system'),
    ],
    'ACTIVE': [
        ('PAUSED', 'employer'),
        ('FILLED', 'employer'),
        ('EXPIRED', 'system'),
        ('CLOSED', 'employer'),
        ('CLOSED', 'system'),
    ],
    'PAUSED': [
        ('ACTIVE', 'employer'),
        ('FILLED', 'employer'),
        ('CLOSED', 'employer'),
        ('CLOSED', 'system'),
    ],
    'FILLED': [
        ('CLOSED', 'system'),
    ],
    'EXPIRED': [
        ('CLOSED', 'system'),
    ],
    'REJECTED': [
        ('PENDING_REVIEW', 'moderator'),
        ('CLOSED', 'system'),
    ],
    'CLOSED': [],  # terminal
}

TERMINAL_STATES = {'CLOSED'}


def is_valid_transition(current: str, new: str, actor: str = 'system') -> bool:
    if current not in TRANSITIONS:
        return False
    for state, allowed_actor in TRANSITIONS[current]:
        if state == new and (allowed_actor == actor or allowed_actor == 'any'):
            return True
    return False


def can_transition(current: str, new: str, actor: str = 'system') -> Tuple[bool, str]:
    if current not in STATES:
        return False, f'Unknown current state: {current}'
    if new not in STATES:
        return False, f'Unknown new state: {new}'
    if current in TERMINAL_STATES:
        return False, f'Cannot transition from terminal state: {current}'
    if not is_valid_transition(current, new, actor):
        return False, f'Invalid transition: {current} -> {new} for actor {actor}'
    return True, ''


def transition_job(job: dict, new_state: str, actor: str = 'system') -> Tuple[dict, str]:
    current = job.get('status', 'SCRAPED')
    ok, err = can_transition(current, new_state, actor)
    if not ok:
        return job, err

    job['status'] = new_state
    job['status_updated_at'] = datetime.now(timezone.utc).isoformat()

    history = job.get('status_history', [])
    history.append({
        'from': current,
        'to': new_state,
        'actor': actor,
        'at': job['status_updated_at'],
    })
    job['status_history'] = history
    return job, ''


def get_allowed_transitions(current: str, actor: str = 'system') -> List[str]:
    if current not in TRANSITIONS:
        return []
    return [s for s, a in TRANSITIONS[current] if a == actor or a == 'any']
