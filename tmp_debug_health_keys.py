from alert_system import AlertSystem, AlertType

asys = AlertSystem()
keys_to_test = [
    ('speed_violation','max_speed'),
    ('wheelslip','threshold'),
    ('overheating','temperature_threshold'),
    ('performance_degradation','response_time_threshold_ms'),
    ('anomaly_detection','min_samples'),
    ('efficiency_drop','drop_percentage'),
    ('brake_pipe_discrepancy','threshold_psi'),
]

for section,key in keys_to_test:
    print('--- Testing', section, key)
    # backup
    backup = asys.config.get(section, {}).get(key)
    try:
        if section in asys.config:
            asys.config[section][key] = None
        alerts = asys.perform_health_check()
        for a in alerts:
            if a.alert_type == AlertType.SYSTEM_ERROR:
                print('SYSTEM ERROR:', a.data.get('error'))
                if a.data.get('traceback'):
                    print(a.data.get('traceback').splitlines()[:10])
    finally:
        # restore
        if section in asys.config:
            asys.config[section][key] = backup

print('Done')