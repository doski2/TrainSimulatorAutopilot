"""Script para aplicar etiquetas a issues abiertos basándose en palabras clave.

Uso:
  python .github/scripts/apply_labels_to_existing_issues.py [--confirm] [--include-prs] [--limit N]

Por defecto hace un dry-run y muestra qué etiquetas propondría. Para ejecutar los cambios realice:
  GITHUB_TOKEN=<token_con_permisos> python .github/scripts/apply_labels_to_existing_issues.py --confirm

Notas:
- Usa la misma lógica de coincidencia que 'auto-label-issues.yml'.
- Crea etiquetas que falten con el color configurado.
- Respeta issues abiertos por defecto; puede incluir PRs con --include-prs.
"""

import os
import re
import sys
import argparse
import requests
from typing import Dict, List

GITHUB_API = "https://api.github.com"

LABEL_MAP = {
    'bug': { 're': r"\b(bug|error|fallo|crash|excepci[oó]n)\b", 'color': 'd73a4a', 'description': 'Reporte de fallo o comportamiento incorrecto.'},
    'crítico': { 're': r"\b(cr[ií]tico|critical|bloqueante|blocker)\b", 'color': 'b60205', 'description': 'Fallos que bloquean uso o seguridad.'},
    'prioridad: crítica': { 're': r"\b(prioridad[:\s]*cr[ií]tica|critic[oó]?|urgente|emergencia)\b", 'color': '8b0000', 'description': 'Prioridad crítica — requiere atención inmediata.'},
    'prioridad: alta': { 're': r"\b(prioridad[:\s]*alta|alta prioridad|high priority|priority[:\s]*high|urgente)\b", 'color': 'd93f0b', 'description': 'Prioridad alta — planificar lo antes posible.'},
    'prioridad: media': { 're': r"\b(prioridad[:\s]*media|prioridad media|medium priority)\b", 'color': 'ff9f00', 'description': 'Prioridad media — importante pero no urgente.'},
    'prioridad: baja': { 're': r"\b(prioridad[:\s]*baja|baja prioridad|low priority)\b", 'color': '006b75', 'description': 'Prioridad baja — trabajo de bajo impacto.'},
    'mejora': { 're': r"\b(mejora|feature|enhancement|nuevo|add|añadir)\b", 'color': '0366d6', 'description': 'Solicitud de mejora o nueva característica.'},
    'documentación': { 're': r"\b(doc|documentaci[oó]n|readme|docs|documentation)\b", 'color': 'fbca04', 'description': 'Cambios en docs, README o guías.'},
    'pregunta': { 're': r"\b(pregunta|question|\?)\b", 'color': '7057ff', 'description': 'Dudas o consultas del proyecto.'},
    'ayuda': { 're': r"\b(ayuda|help wanted|help wanted|help)\b", 'color': '0e8a16', 'description': 'Solicitudes de colaboración / help wanted.'},
    'buen-primer-issue': { 're': r"\b(good first issue|buen primer issue|buen-primer-issue)\b", 'color': 'bfe5bf', 'description': 'Tareas aptas para nuevos colaboradores.'},
    'tests': { 're': r"\b(test|pytest|coverage|prueba|tests)\b", 'color': '1b7c83', 'description': 'Relacionado con pruebas o cobertura.'},
    'ci': { 're': r"\b(ci|github actions|circleci|travis|pipeline|workflow)\b", 'color': 'c2e0c6', 'description': 'Problemas o cambios en integración continua.'},
    'telemetría': { 're': r"\b(telemetr|telemetry|lua|capture|getdata|sendcommand|capture)\b", 'color': 'f9d0c4', 'description': 'Issues relacionados con telemetría, capture o scripts Lua.'},
    'windows': { 're': r"\b(windows|win32|win64)\b", 'color': '000000', 'description': 'Problemas o diferencias específicas de Windows.'},
    'seguridad': { 're': r"\b(security|vulnerability|vulnerabilidad|secret|secreto)\b", 'color': '8b0000', 'description': 'Vulnerabilidades o exposición de secretos.'},
    'wontfix': { 're': r"\b(wontfix|won't fix|no reparar|no resolver)\b", 'color': 'ededed', 'description': 'Decisión de no resolver.'},
}


def get_headers(token: str) -> Dict[str, str]:
    return {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'apply-labels-script'
    }


def list_issues(owner: str, repo: str, token: str, include_prs: bool, limit: int):
    headers = get_headers(token)
    per_page = 100
    page = 1
    fetched = 0

    while True:
        params = {'state': 'open', 'per_page': per_page, 'page': page}
        r = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/issues", headers=headers, params=params)
        r.raise_for_status()
        issues = r.json()
        if not issues:
            break
        for issue in issues:
            # Skip PRs unless requested
            if 'pull_request' in issue and not include_prs:
                continue
            yield issue
            fetched += 1
            if limit and fetched >= limit:
                return
        page += 1


def ensure_label_exists(owner: str, repo: str, token: str, name: str, color: str, description: str = ''):
    headers = get_headers(token)
    # Check
    r = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/labels/{requests.utils.quote(name, safe='')}", headers=headers)
    if r.status_code == 404:
        payload = {'name': name, 'color': color, 'description': description}
        cr = requests.post(f"{GITHUB_API}/repos/{owner}/{repo}/labels", headers=headers, json=payload)
        cr.raise_for_status()
        print(f"Label {name} not found - created")
    else:
        r.raise_for_status()


def add_labels_to_issue(owner: str, repo: str, token: str, number: int, labels: List[str]):
    headers = get_headers(token)
    payload = {'labels': labels}
    r = requests.post(f"{GITHUB_API}/repos/{owner}/{repo}/issues/{number}/labels", headers=headers, json=payload)
    r.raise_for_status()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--confirm', action='store_true', help='Aplicar cambios en lugar de dry-run')
    parser.add_argument('--include-prs', action='store_true', help='Incluir Pull Requests además de issues')
    parser.add_argument('--limit', type=int, default=0, help='Límite de issues a procesar (0 = sin límite)')
    args = parser.parse_args()

    token = os.getenv('GITHUB_TOKEN')
    repo_full = os.getenv('GITHUB_REPOSITORY') or os.getenv('REPO')
    if not token:
        print('ERROR: Se requiere GITHUB_TOKEN en el entorno (con permisos issues:write y contents:write para crear labels).')
        sys.exit(2)
    if not repo_full:
        print('ERROR: Se requiere GITHUB_REPOSITORY en el entorno (p.ej. owner/repo).')
        sys.exit(2)

    owner, repo = repo_full.split('/')

    compiled = {name: re.compile(meta['re'], re.I) for name, meta in LABEL_MAP.items()}

    summary = []
    for issue in list_issues(owner, repo, token, args.include_prs, args.limit):
        number = issue['number']
        title = (issue.get('title') or '')
        body = (issue.get('body') or '')
        existing_labels = [l['name'] for l in issue.get('labels', [])]

        to_add = []
        for name, regex in compiled.items():
            try:
                if regex.search(title) or regex.search(body):
                    if name not in existing_labels:
                        to_add.append(name)
            except re.error as e:
                print(f"Regex error for {name}: {e}")

        if not to_add:
            continue

        # Normalizar prioridades: si coinciden varias prioridades, conservar sólo la más severa
        priority_order = ['prioridad: crítica', 'prioridad: alta', 'prioridad: media', 'prioridad: baja']
        matched_priorities = [p for p in priority_order if p in to_add]
        if len(matched_priorities) > 1:
            keep = matched_priorities[0]
            to_add = [l for l in to_add if (l not in priority_order) or l == keep]

        summary.append({'number': number, 'title': title, 'add': to_add})

        if args.confirm:
            # Ensure labels exist
            for l in to_add:
                meta = LABEL_MAP[l]
                ensure_label_exists(owner, repo, token, l, meta['color'], meta.get('description', ''))
            add_labels_to_issue(owner, repo, token, number, to_add)
            print(f"Applied to #{number}: {to_add}")
        else:
            print(f"[DRY-RUN] Would apply to #{number}: {to_add}")

    print('\nSummary:')
    for s in summary:
        print(f"#{s['number']}: {', '.join(s['add'])} - {s['title'][:80]}")

    if not args.confirm:
        print('\nRun the script with --confirm to actually apply labels.')


if __name__ == '__main__':
    main()
