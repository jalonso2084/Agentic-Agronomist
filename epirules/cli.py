from __future__ import annotations
import argparse, json, yaml, pandas as pd
from .io import read_weather_csv
from .engine import evaluate_rule_set

def main():
    ap = argparse.ArgumentParser(description='Epidemiological rules checker (late blight)')
    ap.add_argument('--weather', required=True, help='Path to weather CSV')
    ap.add_argument('--rules', required=True, help='Path to rules.yaml')
    ap.add_argument('--rule-set', required=True, choices=['Hutton','Smith','LocalAndes'])
    ap.add_argument('--out', required=True, help='Path to output JSON')
    args = ap.parse_args()

    df = read_weather_csv(args.weather)
    with open(args.rules, 'r', encoding='utf-8') as f:
        rules = yaml.safe_load(f)
    result = evaluate_rule_set(df, rules, args.rule_set)

    # Add simple human summary
    rs = result['result']
    if rs['rule'] == 'LocalAndes':
        summary = f"{rs['rule']} risk: {rs.get('risk_label','n/a')} (days meeting criteria: {len(rs['details']['days_meeting_criteria'])})"
    else:
        summary = f"{rs['rule']} triggered: {rs['triggered']} (run={rs['details']['consecutive_true_max']}/{rs['details']['required_consecutive_days']})"
    result['summary'] = summary

    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

if __name__ == '__main__':
    main()
