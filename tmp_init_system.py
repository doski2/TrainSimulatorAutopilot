from web_dashboard import initialize_system, system_status, tsc_integration, autopilot_system, multi_loco_integration
print('Calling initialize_system...')
ok = initialize_system()
print('initialize_system returned:', ok)
print('system_status after init:')
print(system_status)
if tsc_integration:
    try:
        print('tsc_integration.ruta_archivo:', tsc_integration.ruta_archivo)
        print('GetData exists:', tsc_integration.archivo_existe())
        print('commands file:', tsc_integration.ruta_archivo_comandos)
    except Exception as e:
        print('Error checking tsc_integration:', e)
else:
    print('tsc_integration None')

if autopilot_system:
    print('autopilot_system exists: sesion_activa=', getattr(autopilot_system,'sesion_activa',None), 'modo_automatico=', getattr(autopilot_system,'modo_automatico',None))
else:
    print('autopilot_system None')

print('multi_loco_integration is', 'present' if multi_loco_integration else 'None')
