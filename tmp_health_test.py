from alert_system import AlertSystem
asys = AlertSystem()
asys.config['performance_degradation']['response_time_threshold_ms'] = None
alerts = asys.perform_health_check()
print('alerts count:', len(alerts))
for a in alerts:
    print(a.alert_id, a.title, a.data.get('error'))
