from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List
import pandas as pd
from .io import daily_aggregates

@dataclass
class RuleParams:
    name: str
    params: Dict[str, Any]

def _consecutive_true_days(flags: List[bool], min_run: int) -> int:
    run = best = 0
    for f in flags:
        run = run + 1 if f else 0
        if run > best: best = run
    return best

def eval_hutton(daily: pd.DataFrame, p: Dict[str, Any]) -> Dict[str, Any]:
    cond = (daily['min_temp_c'] >= p['min_temp_c']) & (daily['hours_rh_ge_90'] >= p['min_hours_per_day'])
    best_run = _consecutive_true_days(cond.tolist(), p['consecutive_days'])
    triggered = best_run >= p['consecutive_days']
    evidence_days = daily.loc[cond, 'day'].dt.strftime('%Y-%m-%d').tolist()
    return {
        'rule': 'Hutton',
        'triggered': bool(triggered),
        'details': {
            'consecutive_true_max': int(best_run),
            'required_consecutive_days': int(p['consecutive_days']),
            'days_meeting_criteria': evidence_days,
        }
    }

def eval_smith(daily: pd.DataFrame, p: Dict[str, Any]) -> Dict[str, Any]:
    cond = (daily['min_temp_c'] >= p['min_temp_c']) & (daily['hours_rh_ge_90'] >= p['min_hours_per_day'])
    best_run = _consecutive_true_days(cond.tolist(), p['consecutive_days'])
    triggered = best_run >= p['consecutive_days']
    evidence_days = daily.loc[cond, 'day'].dt.strftime('%Y-%m-%d').tolist()
    return {
        'rule': 'Smith',
        'triggered': bool(triggered),
        'details': {
            'consecutive_true_max': int(best_run),
            'required_consecutive_days': int(p['consecutive_days']),
            'days_meeting_criteria': evidence_days,
        }
    }

def eval_local_andes(daily: pd.DataFrame, p: Dict[str, Any]) -> Dict[str, Any]:
    # Day is positive if >= threshold RH hours AND mean temp during those hours >= min_temp_c
    cond = (daily['hours_rh_ge_80'] >= p['min_hours_per_day']) & (daily['mean_temp_when_rh_ge_80'] >= p['min_temp_c'])
    best_run = _consecutive_true_days(cond.tolist(), max(p['consecutive_days_high'], p['consecutive_days_mod']))
    risk = 'Low'
    if best_run >= p['consecutive_days_high']:
        risk = 'High'
    elif best_run >= p['consecutive_days_mod']:
        risk = 'Moderate'
    evidence_days = daily.loc[cond, 'day'].dt.strftime('%Y-%m-%d').tolist()
    return {
        'rule': 'LocalAndes',
        'triggered': risk in ('Moderate','High'),
        'risk_label': risk,
        'details': {
            'consecutive_true_max': int(best_run),
            'days_meeting_criteria': evidence_days,
            'thresholds': {
                'rh_threshold': int(p['rh_threshold']),
                'min_temp_c': float(p['min_temp_c']),
                'min_hours_per_day': int(p['min_hours_per_day'])
            }
        }
    }

def evaluate_rule_set(weather_df: pd.DataFrame, rules: Dict[str, Any], rule_set: str) -> Dict[str, Any]:
    daily = daily_aggregates(weather_df)
    out = {'rule_set': rule_set, 'days': len(daily)}
    if rule_set == 'Hutton':
        out['result'] = eval_hutton(daily, rules['Hutton'])
    elif rule_set == 'Smith':
        out['result'] = eval_smith(daily, rules['Smith'])
    elif rule_set == 'LocalAndes':
        out['result'] = eval_local_andes(daily, rules['LocalAndes'])
    else:
        raise ValueError(f'Unknown rule_set: {rule_set}')
    return out
