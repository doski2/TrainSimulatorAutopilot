from alert_system import AlertSystem
asys = AlertSystem()
alerts = asys.perform_health_check()
print('alerts len:', len(alerts))
for a in alerts:
    print(a.alert_id, a.title)
    print('error:', a.data.get('error'))
    if a.data.get('traceback'):
        print(a.data.get('traceback'))
