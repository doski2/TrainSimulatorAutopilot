from alert_system import AlertSystem

asys = AlertSystem()

def broken_check(self, current_data):
    # Simulate the original TypeError by performing an invalid comparison
    if None < 1:
        return None

# Monkeypatch
asys.check_wheelslip = broken_check.__get__(asys, AlertSystem)

alerts = asys.perform_health_check()
print('alerts count:', len(alerts))
for a in alerts:
    print(a.alert_id, a.title)
    print('message:', a.message)
    print('data:', a.data)
    if a.data.get('traceback'):
        print('\nTRACEBACK:\n')
        print(a.data.get('traceback'))
