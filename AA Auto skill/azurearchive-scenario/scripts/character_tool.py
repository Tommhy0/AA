#!/usr/bin/env python3
"""Read evidence-backed student cards; bounded, explicitly requested corpus search."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import quote

SKILL = Path(__file__).resolve().parents[1]
INDEX = SKILL / 'references' / 'characters' / 'index.json'
CATEGORIES = {'bond': '絆ストーリー', 'main': '主線', 'event': 'イベント',
              'club': 'グループストーリー', 'momo': 'モモトーク',
              'profile': 'キャラクターデータ', 'mini': 'ミニストーリー'}
HEADER = re.compile(r'^\*\*(.+?)\*\*:\s*(.*)$')


def normalized(value):
    return unicodedata.normalize('NFKC', str(value)).strip().casefold()


def load_index():
    return json.loads(INDEX.read_text(encoding='utf-8'))


def resolve(query, index):
    query = normalized(query)
    found = []
    for student in index['students']:
        aliases = [student['jp'], student['name'], *student.get('aliases', [])]
        variant = None
        if query not in {normalized(a) for a in aliases}:
            matches = [v for v in student['variants'] if query in
                       {normalized(a) for a in [v['id'], v['label'], *v.get('aliases', [])]}]
            if not matches:
                continue
            if len(matches) > 1:
                raise ValueError('Ambiguous variant; use the exact character ID.')
            variant = matches[0]
        found.append((student, variant))
    if len(found) != 1:
        raise ValueError('Unknown or ambiguous student; use list or an exact character ID.')
    return found[0]


def corpus_root(explicit=None):
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    elif os.environ.get('AZUREARCHIVE_CHARACTER_CORPUS'):
        candidates.append(Path(os.environ['AZUREARCHIVE_CHARACTER_CORPUS']))
    else:
        # Discover portable workspace caches without embedding this user's home path.
        for origin in [Path.cwd(), SKILL]:
            for folder in [origin, *origin.parents]:
                candidates.append(folder / '.aa-character-cache' / 'ba-storybook' / 'ba-stories')
    for candidate in candidates:
        if (candidate / 'ba-stories').is_dir():
            candidate = candidate / 'ba-stories'
        if (candidate / 'キャラクターデータ').is_dir():
            return candidate.resolve()
    raise ValueError('Corpus unavailable. Set --corpus or AZUREARCHIVE_CHARACTER_CORPUS. '
                     'Bundled cards remain usable offline; do not invent missing evidence.')


def metadata(lines, path):
    result = {}
    if lines and lines[0] == '---':
        for line in lines[1:]:
            if line == '---':
                break
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip().strip('"')
    if 'character_id' not in result and path.parent.name in ('モモトーク', 'キャラクターデータ'):
        match = re.match(r'(\d+)_', path.name)
        if match:
            result['character_id'] = match.group(1)
    return result


def parse_dialogue(lines, category):
    """Keep multiline turns; exclude player choices and uncertain MomoTalk Answer sections."""
    records, uncertain = [], False
    i = 0
    while i < len(lines):
        line = lines[i]
        if category == 'momo' and line.startswith('## '):
            uncertain = bool(re.match(r'^## Answer\b', line))
        match = HEADER.match(line)
        if not match:
            i += 1
            continue
        start, pieces = i, [match.group(2)]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(('*', '>', '#', '---')):
            pieces.append(lines[i])
            i += 1
        records.append(dict(speaker=match.group(1), text='\n'.join(pieces),
                            line=start + 1, end=i, uncertain=uncertain))
    return records


def parse_profile(lines, jp):
    records, section = [], ''
    for i, line in enumerate(lines):
        if line.startswith('### '):
            section = line[4:]
        elif line.startswith('## '):
            section = ''
        elif line.strip() and section in ('自己紹介', 'UILobby', 'UILobbySpecial', 'Cafe'):
            records.append(dict(speaker=jp, text=line.removeprefix('- '), line=i+1, end=i+1,
                                uncertain=False, type='profile' if section == '自己紹介' else 'lobby'))
    return records


def source_url(index, relative, start, end):
    provenance = index['provenance']
    return (provenance['repository'] + '/blob/' + provenance['commit'] + '/ba-stories/' +
            quote(relative, safe='/') + f'#L{start}-L{end}')


def search(index, student, root, keyword='', category=None, character_id=None, limit=6, context=3):
    results = []
    categories = [category] if category else list(CATEGORIES)
    for kind in categories:
        folder = root / CATEGORIES[kind]
        if not folder.is_dir():
            continue
        for path in sorted(folder.rglob('*.md')):
            if path.name == 'README.md' or path.name.startswith('_'):
                continue
            lines = path.read_text(encoding='utf-8').splitlines()
            meta = metadata(lines, path)
            if character_id is not None and meta.get('character_id') != str(character_id):
                continue
            if kind == 'profile':
                if meta.get('title') != student['jp']:
                    continue
                records = parse_profile(lines, student['jp'])
            else:
                records = parse_dialogue(lines, kind)
            seen = set()
            for row in records:
                if row['uncertain'] or row['speaker'] != student['jp']:
                    continue
                if keyword and normalized(keyword) not in normalized(row['text']):
                    continue
                if row['text'] in seen:
                    continue
                seen.add(row['text'])
                relative = path.relative_to(root).as_posix()
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                expected = index['provenance'].get('file_hashes',{}).get(relative)
                snapshot_match = expected is not None and digest == expected
                results.append(dict(category=kind, source=relative, line=row['line'], end=row['end'],
                                    text=row['text'], metadata=meta,
                                    context_before=lines[max(0,row['line']-1-context):row['line']-1],
                                    context_after=lines[row['end']:row['end']+context],
                                    url=source_url(index,relative,row['line'],row['end']) if snapshot_match else None,
                                    sha256=digest,snapshot_match=snapshot_match))
                if len(results) >= limit:
                    return results
    return results


def verify(index, root):
    errors, count = [], 0
    for student in index['students']:
        if not student.get('profile'):
            continue
        card = (INDEX.parent / student['profile']).resolve()
        if not card.is_relative_to(INDEX.parent.resolve()) or not card.is_file():
            errors.append('Missing/unsafe card: ' + student['jp'])
        for source in student['evidence']:
            count += 1
            path = (root / source['path']).resolve()
            if not path.is_relative_to(root.resolve()) or not path.is_file():
                errors.append('Missing/unsafe evidence: ' + source['path'])
                continue
            raw = path.read_bytes()
            lines = raw.decode('utf-8').splitlines()
            if hashlib.sha256(raw).hexdigest() != source['sha256']:
                errors.append('Changed source: ' + source['path'])
            if not 1 <= source['start'] <= source['end'] <= len(lines):
                errors.append('Invalid line range: ' + source['path'])
            else:
                excerpt = '\n'.join(lines[source['start']-1:source['end']])
                if hashlib.sha256(excerpt.encode('utf-8')).hexdigest() != source['range_sha256']:
                    errors.append('Changed evidence range: ' + source['path'])
            if source.get('character_id') and metadata(lines,path).get('character_id') != str(source['character_id']):
                errors.append('Wrong character variant: ' + source['path'])
    return dict(ok=not errors, cards=sum(bool(s.get('profile')) for s in index['students']),
                evidence_ranges=count, errors=errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    listing = sub.add_parser('list')
    listing.add_argument('--query', default='')
    card = sub.add_parser('profile')
    card.add_argument('student')
    query = sub.add_parser('search')
    query.add_argument('student')
    query.add_argument('--keyword', default='')
    query.add_argument('--category', choices=CATEGORIES)
    query.add_argument('--character-id', type=int)
    query.add_argument('--corpus')
    query.add_argument('--limit', type=int, choices=range(1,21), default=6)
    query.add_argument('--context', type=int, choices=range(0,7), default=3)
    checking = sub.add_parser('verify')
    checking.add_argument('--corpus')
    args = parser.parse_args()
    try:
        index = load_index()
        if args.command == 'list':
            rows = [s for s in index['students'] if not args.query or
                    any(normalized(args.query) in normalized(a) for a in
                        [s['name'],s['jp'],*s['aliases'],*[v['label'] for v in s['variants']]])]
            output = [dict(name=s['name'],jp=s['jp'],coverage=s['coverage'],profile=s['profile'],
                           variants=[dict(id=v['id'],label=v['label']) for v in s['variants']]) for s in rows]
        elif args.command == 'profile':
            student, variant = resolve(args.student,index)
            if not student['profile']:
                output = dict(status='index_only',student=student['name'],
                              selected_variant=variant, next='No curated card. Use bounded search; do not invent a personality.')
            else:
                print((INDEX.parent/student['profile']).read_text(encoding='utf-8'))
                if variant and variant['id'] != student['base_id']:
                    print('\n注意：所选版本为 ' + variant['label'] + '。上文是基础档案；该衣装/阶段尚未单独归纳，按需查证。')
                return 0
        elif args.command == 'search':
            student, variant = resolve(args.student,index)
            bound_id = args.character_id if args.character_id is not None else (variant['id'] if variant else None)
            if bound_id is not None and bound_id not in [v['id'] for v in student['variants']]:
                raise ValueError('character-id does not belong to the requested student.')
            output = dict(student=student['name'],character_id_filter=bound_id,
                          results=search(index,student,corpus_root(args.corpus),args.keyword,
                                         args.category,bound_id,args.limit,args.context),
                          note='Bounded retrieval, not an OOC verdict. Check speaker attribution, branch and story stage; '
                               'MomoTalk Answer sections excluded. Unfiltered results may mix costumes/timelines. '
                               'Pinned URLs refer to the recorded snapshot; changed local files require rechecking.')
        else:
            output = verify(index,corpus_root(args.corpus))
        print(json.dumps(output,ensure_ascii=False,indent=2))
        return 1 if isinstance(output,dict) and output.get('ok') is False else 0
    except (ValueError,OSError,json.JSONDecodeError) as exc:
        print(json.dumps(dict(ok=False,error=str(exc)),ensure_ascii=False),file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
