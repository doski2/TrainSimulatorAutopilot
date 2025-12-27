import os


def test_prometheus_configs_exist_and_contain_expected_entries():
    base = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'prometheus')
    prom = os.path.join(base, 'prometheus.yml')
    rules = os.path.join(base, 'rules.yml')

    assert os.path.exists(prom), "prometheus.yml should exist"
    assert os.path.exists(rules), "rules.yml should exist"

    with open(prom, encoding='utf-8') as fh:
        content = fh.read()
    assert 'scrape_configs' in content
    assert 'train_simulator_autopilot' in content

    with open(rules, encoding='utf-8') as fh:
        rules_content = fh.read()
    assert 'groups' in rules_content
    assert 'HighIADecisionLatency' in rules_content
