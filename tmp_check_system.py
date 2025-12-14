import os
from web_dashboard import system_status, last_telemetry, tsc_integration, autopilot_system, multi_loco_integration
print('system_status snapshot:')
print(system_status)
print('\nlast_telemetry present:', bool(last_telemetry))
if tsc_integration:
    try:
        print('tsc_integration.ruta_archivo:', getattr(tsc_integration, 'ruta_archivo', None))
        print('GetData exists:', tsc_integration.archivo_existe())
        print('tsc_integration.ruta_archivo_comandos:', getattr(tsc_integration, 'ruta_archivo_comandos', None))
    except Exception as e:
        print('Error inspecting tsc_integration:', e)
else:
    print('tsc_integration is None')

if autopilot_system:
    try:
        print('\nautopilot_system session active:', autopilot_system.sesion_activa)
        print('autopilot_system modo_automatico:', autopilot_system.modo_automatico)
    except Exception as e:
        print('Error inspecting autopilot_system:', e)
else:
    print('autopilot_system is None')

if multi_loco_integration:
    print('\nmulti_loco_integration exists')
else:
    print('\nmulti_loco_integration is None')
