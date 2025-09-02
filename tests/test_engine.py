from epirules.io import read_weather_csv, daily_aggregates
from epirules.engine import evaluate_rule_set
import yaml, pathlib

def test_hutton_triggers(tmp_path):
    weather = pathlib.Path(__file__).parent.parent / 'sample_data' / 'sample_weather.csv'
    df = read_weather_csv(str(weather))
    rules = yaml.safe_load((pathlib.Path(__file__).parent.parent / 'rules.yaml').read_text())
    out = evaluate_rule_set(df, rules, 'Hutton')
    assert out['result']['rule'] == 'Hutton'
    assert out['result']['triggered'] is True
    assert out['result']['details']['required_consecutive_days'] == 2

def test_smith_not_triggered(tmp_path):
    weather = pathlib.Path(__file__).parent.parent / 'sample_data' / 'sample_weather.csv'
    df = read_weather_csv(str(weather))
    rules = yaml.safe_load((pathlib.Path(__file__).parent.parent / 'rules.yaml').read_text())
    out = evaluate_rule_set(df, rules, 'Smith')
    assert out['result']['rule'] == 'Smith'
    assert out['result']['triggered'] is False

def test_local_andes_labels(tmp_path):
    weather = pathlib.Path(__file__).parent.parent / 'sample_data' / 'sample_weather.csv'
    df = read_weather_csv(str(weather))
    rules = yaml.safe_load((pathlib.Path(__file__).parent.parent / 'rules.yaml').read_text())
    out = evaluate_rule_set(df, rules, 'LocalAndes')
    assert out['result']['rule'] == 'LocalAndes'
    assert out['result']['risk_label'] in ('Low','Moderate','High')
