"""Check progressive documentation structure and local link/resource boundaries."""
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


def links(path: Path):
    fence = None
    for line in path.read_text(encoding='utf-8').splitlines():
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            token = marker.group(1)[0]
            fence = token if fence is None else None if fence == token else fence
            continue
        if fence is not None:
            continue
        for match in re.finditer(r'\[[^\]\n]*\]\((<[^>]+>|[^)\s]+)(?:\s+"[^"]*")?\)', line):
            target = match.group(1).strip('<>')
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                continue
            yield (path.parent / unquote(url.path)).resolve(), target


def check_links(paths, *, boundary: Path | None = None):
    problems = []
    for path in paths:
        for target, literal in links(path):
            if not target.exists():
                problems.append(f'{path}: missing local link {literal}')
            elif boundary is not None and not target.is_relative_to(boundary.resolve()):
                problems.append(f'{path}: skill link escapes packaged collection: {literal}')
    return problems


def check_skill_tree(root: Path):
    problems = check_links(root.rglob('*.md'), boundary=root)
    index = root / 'README.md'
    if not index.is_file():
        problems.append('Skills are missing the routing index README.md')
    routed = {target for target, _ in links(index)} if index.is_file() else set()
    for entry in sorted(root.glob('*/SKILL.md')):
        if entry.resolve() not in routed:
            problems.append(f'{entry}: skill missing from routing index')
        text = entry.read_text(encoding='utf-8')
        pieces = text.split('---', 2)
        if len(pieces) != 3 or pieces[0].strip():
            problems.append(f'{entry}: missing YAML frontmatter')
            continue
        try:
            data = yaml.safe_load(pieces[1])
        except yaml.YAMLError:
            problems.append(f'{entry}: invalid YAML frontmatter')
            continue
        if not isinstance(data, dict) or data.get('name') != entry.parent.name:
            problems.append(f'{entry}: skill name must match its directory')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', entry.parent.name) or len(entry.parent.name) > 64:
            problems.append(f'{entry}: invalid skill name')
        description = data.get('description') if isinstance(data, dict) else None
        if not isinstance(description, str) or not 1 <= len(description) <= 240:
            problems.append(f'{entry}: discovery description must be 1..240 characters')
        metadata = data.get('metadata', {}) if isinstance(data, dict) else {}
        if not isinstance(metadata, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in metadata.items()):
            problems.append(f'{entry}: metadata must map string keys to string values')
        if len(pieces[2].split()) > 400 or len(pieces[2]) > 3000:
            problems.append(f'{entry}: task entry exceeds 400 words or 3000 characters; move details to references/')
        if 'references/' not in pieces[2]:
            problems.append(f'{entry}: missing task-specific reference routing')
        ui_path = entry.parent / 'agents/openai.yaml'
        if ui_path.is_file():
            try:
                ui = yaml.safe_load(ui_path.read_text(encoding='utf-8'))
                interface = ui.get('interface') if isinstance(ui, dict) else None
                if not isinstance(interface, dict) or any(not isinstance(interface.get(key), str) or not interface[key].strip()
                        for key in ('display_name', 'short_description', 'default_prompt')):
                    problems.append(f'{ui_path}: missing UI strings')
                elif len(interface['short_description']) > 64 or f'${entry.parent.name}' not in interface['default_prompt']:
                    problems.append(f'{ui_path}: short description exceeds 64 characters or prompt lacks skill name')
            except yaml.YAMLError:
                problems.append(f'{ui_path}: invalid YAML')
    return problems


def check_repository(root: Path):
    import json
    problems = check_skill_tree(root / 'skills')
    paths = [root / filename for filename in ('README.md', 'AGENTS.md')]
    paths.extend(root / name for name in ('CLAUDE.md', 'GEMINI.md', 'CONTRIBUTING.md')
                 if (root / name).is_file())
    paths.extend((root / 'docs').rglob('*.md'))
    paths.extend((root / 'knowledge').rglob('*.md'))
    problems.extend(check_links(paths))
    if len((root / 'AGENTS.md').read_text(encoding='utf-8')) > 2000:
        problems.append('AGENTS.md exceeds 2000 characters; move details to on-demand docs')
    if (root / 'CLAUDE.md').is_file() and (root / 'CLAUDE.md').read_text(encoding='utf-8') != '@AGENTS.md\n':
        problems.append('CLAUDE.md must import the common entry once without duplicated instructions')
    manifests = ['plugin.json', 'gemini-extension.json', '.claude-plugin/plugin.json',
                 '.codex-plugin/plugin.json', '.cursor-plugin/plugin.json',
                 '.claude-plugin/marketplace.json', '.cursor-plugin/marketplace.json',
                 '.agents/plugins/marketplace.json']
    def descriptions(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in ('description', 'longDescription', 'shortDescription') and isinstance(child, str):
                    yield child
                else:
                    yield from descriptions(child)
        elif isinstance(value, list):
            for child in value:
                yield from descriptions(child)
    for name in manifests:
        if any(len(text) > 160 for text in descriptions(json.loads((root / name).read_text(encoding='utf-8')))):
            problems.append(f'{name}: discovery description exceeds 160 characters')
    return problems


def main():
    root = Path(__file__).resolve().parents[1]
    problems = check_repository(root)
    for problem in problems:
        print(f'FAIL: {problem}')
    if problems:
        raise SystemExit(1)
    print('Documentation: links, skill metadata, packaged paths and context budgets passed.')


if __name__ == '__main__':
    main()
