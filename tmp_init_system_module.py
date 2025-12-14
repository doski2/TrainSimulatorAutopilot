import web_dashboard
print('Calling initialize_system...')
ok = web_dashboard.initialize_system()
print('initialize_system returned:', ok)
print('system_status after init:')
print(web_dashboard.system_status)
print('tsc_integration:', web_dashboard.tsc_integration)
if web_dashboard.tsc_integration:
    print('GetData exists:', web_dashboard.tsc_integration.archivo_existe())
print('autopilot_system:', web_dashboard.autopilot_system)
print('multi_loco_integration:', web_dashboard.multi_loco_integration)
