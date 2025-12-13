# Verificar que los elementos de frenos existen en el HTML

with open("web/templates/index.html", encoding="utf-8") as f:
    html_content = f.read()

# Elementos de frenos que deben existir
brake_elements = [
    "brake-pipe-value",
    "loco-brake-value",
    "train-brake-value",
    "brake-pipe-tail-value",
    "brake-pipe-tail-presence",
    "loco-brake-displayed-value",
    "brake-pressure-status",
]

print("Verificando elementos de frenos en el HTML:")
for element_id in brake_elements:
    if f'id="{element_id}"' in html_content:
        print(f"✅ {element_id} - ENCONTRADO")
    else:
        print(f"❌ {element_id} - NO ENCONTRADO")

print("\nVerificando elementos de telemetría principales:")
main_elements = [
    "speed-value",
    "rpm-value",
    "amperage-value",
    "wheelslip-value",
    "tractive-effort-value",
    "next-speed-limit-value",
    "next-speed-distance-value",
]

for element_id in main_elements:
    if f'id="{element_id}"' in html_content:
        print(f"✅ {element_id} - ENCONTRADO")
    else:
        print(f"❌ {element_id} - NO ENCONTRADO")
