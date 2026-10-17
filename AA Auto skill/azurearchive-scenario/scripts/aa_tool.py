#!/usr/bin/env python3
"""AAP2 generation, diagnostics and verified native compilation (Python stdlib)."""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

SKILL = Path(__file__).resolve().parents[1]
EMPTY_ID = '00000000-0000-0000-0000-000000000000'


def dump(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_project(path):
    raw = Path(path).read_bytes()
    if not raw.startswith(b'AAP2\n'):
        raise ValueError('AAP2 must start with 41 41 50 32 0A (no BOM or CRLF).')
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise ValueError('Duplicate JSON property: ' + key)
            obj[key] = value
        return obj
    return json.loads(raw[5:].decode('utf-8'), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Invalid JSON number: ' + x)))


def validate(project, require_auto=False, require_title=False):
    errors, warnings = [], []
    def err(path, message):
        errors.append({'path': path, 'message': message})
    def check_title(value, path):
        if not isinstance(value, str):
            err(path, 'Expected title string.')
        elif not value.strip():
            (errors if require_title else warnings).append({
                'path': path, 'message': 'Missing scenario title; fill PreviewTitle and entry.Title before delivery.'})
    def guid(value, path):
        try:
            if not isinstance(value, str) or str(uuid.UUID(value)) != value.lower():
                raise ValueError()
        except (ValueError, AttributeError):
            err(path, 'Expected a canonical GUID string.')
    def integer(value, low, high):
        return type(value) is int and low <= value <= high
    if not isinstance(project, dict):
        return [{'path': '$', 'message': 'Project must be an object.'}], warnings
    guid(project.get('ProjectId'), '$.ProjectId')
    if type(project.get('FormatVersion')) is not int or project.get('FormatVersion') != 2:
        err('$.FormatVersion', 'Expected format version 2.')
    check_title(project.get('PreviewTitle'), '$.PreviewTitle')
    for field in ['PreviewHeader']:
        if not isinstance(project.get(field), str): err('$.' + field, 'Expected string.')
    if not integer(project.get('PreviewBgName'), 0, 0xffffffff):
        err('$.PreviewBgName', 'Expected uint32.')
    if not isinstance(project.get('ProjectName'), str) or not project['ProjectName'].strip():
        err('$.ProjectName', 'Expected a nonempty project name.')
    nodes = project.get('nodes')
    if not isinstance(nodes, list):
        return errors + [{'path': '$.nodes', 'message': 'Expected node array.'}], warnings
    identities, line_ids, option_ids, edges, entries = set(), set(), set(), {}, []
    def check_line(line, path):
        if not isinstance(line, dict):
            err(path, 'Expected ScriptData object.'); return
        line_id = line.get('LineId')
        guid(line_id, path + '.LineId')
        if isinstance(line_id, str):
            if line_id.lower() in line_ids: err(path + '.LineId', 'Duplicate LineId.')
            line_ids.add(line_id.lower())
        for field in ['text', 'popup', 'bgFriendlyName', 'sound', 'voice', 'additionalPrompt', 'placeText']:
            if not isinstance(line.get(field), str):
                err(path + '.' + field, 'Expected string.')
        for field in ['bgEffect', 'bgName', 'transition', 'selectionGroup']:
            if not integer(line.get(field), 0, 0xffffffff):
                err(path + '.' + field, 'Expected uint32.')
        if not integer(line.get('bgmId'), -0x80000000, 0x7fffffff):
            err(path + '.bgmId', 'Expected int32.')
        if type(line.get('isDialogScript')) is not bool:
            err(path + '.isDialogScript', 'Expected boolean.')
        slots = line.get('characters')
        if not isinstance(slots, list) or len(slots) != 6:
            err(path + '.characters', 'Expected exactly six stage records.'); return
        occupied = set()
        for slot, char in enumerate(slots):
            cp = f'{path}.characters[{slot}]'
            if not isinstance(char, dict):
                err(cp, 'Expected character record.'); continue
            if not isinstance(char.get('name'), str):
                err(cp + '.name', 'Expected string.')
            elif char['name']:
                occupied.add(slot)
            face = char.get('faceId')
            if not isinstance(face, str) or len(face) != 2 or not face.isascii() or not face.isdigit():
                err(cp + '.faceId', 'Expected a two digit face ID; capability is checked by runtime.')
            for field, low, high in [('startingPos', 0, 5), ('endingPos', 0, 5), ('displayOrder', 1, 5),
                                     ('emoticon', -1, 19), ('action', 0, 7), ('appear', 0, 6),
                                     ('effect', 0, 0x7fffffff), ('shapeOverride', 0, 0x7fffffff)]:
                if not integer(char.get(field), low, high):
                    err(cp + '.' + field, f'Expected integer in {low}..{high}.')
        speaker = line.get('speakerSlotNum')
        if not integer(speaker, 0, 5):
            err(path + '.speakerSlotNum', 'Expected slot 0..5.')
        elif line.get('isDialogScript') and speaker not in occupied:
            err(path + '.speakerSlotNum', 'Dialogue speaker must occupy the stage slot.')
        highlighted = line.get('highlightedSlotNums')
        if not isinstance(highlighted, list) or any(not integer(s, 0, 5) or s not in occupied for s in highlighted):
            err(path + '.highlightedSlotNums', 'Highlighted slots must be occupied slots.')
        if line.get('bgName') == 0:
            warnings.append({'path': path + '.bgName', 'message': 'Background is explicitly cleared.'})
        if line.get('bgmId') == 0:
            warnings.append({'path': path + '.bgmId', 'message': 'BGM is explicitly cleared.'})
    for i, node in enumerate(nodes):
        path = f'$.nodes[{i}]'
        if not isinstance(node, dict):
            err(path, 'Expected node object.'); continue
        nid = node.get('Guid')
        guid(nid, path + '.Guid')
        if isinstance(nid, str):
            nid = nid.lower()
            if nid in identities: err(path + '.Guid', 'Duplicate node ID.')
            identities.add(nid)
        kind = node.get('Kind')
        if kind not in ['entry', 'dialogue', 'choice', 'exit']:
            err(path + '.Kind', 'Unknown node kind.'); continue
        targets = []
        if kind == 'choice':
            options = node.get('Options')
            if not isinstance(options, list) or not options:
                err(path + '.Options', 'Expected nonempty option array.')
            else:
                local_options = set()
                for k, option in enumerate(options):
                    op = f'{path}.Options[{k}]'
                    if not isinstance(option, dict):
                        err(op, 'Expected option object.'); continue
                    oid = option.get('OptionId'); guid(oid, op + '.OptionId')
                    if isinstance(oid, str):
                        oid = oid.lower()
                        if oid in option_ids: err(op + '.OptionId', 'Duplicate option ID.')
                        option_ids.add(oid); local_options.add(oid)
                    if not isinstance(option.get('Text'), str): err(op + '.Text', 'Expected string.')
                    target = option.get('TargetNodeId'); guid(target, op + '.TargetNodeId')
                    targets.append(target)
                default = node.get('DefaultOptionId')
                if default is None:
                    issue = {'path': path + '.DefaultOptionId',
                             'message': 'No Auto option selected; automatic playback/recording may stop here. '
                                        'Set DefaultOptionId to one OptionId in this choice.'}
                    (errors if require_auto else warnings).append(issue)
                elif not isinstance(default, str) or default.lower() not in local_options:
                    err(path + '.DefaultOptionId', 'Default option must belong to this choice.')
        else:
            targets = node.get('ConnectionsTo')
            if not isinstance(targets, list):
                err(path + '.ConnectionsTo', 'Expected target array.'); targets = []
            for k, target in enumerate(targets): guid(target, f'{path}.ConnectionsTo[{k}]')
        if isinstance(nid, str): edges[nid] = [t.lower() for t in targets if isinstance(t, str)]
        if kind == 'entry':
            entries.append(nid)
            check_title(node.get('Title'), path + '.Title')
        if kind == 'dialogue':
            scripts = node.get('Scripts')
            if not isinstance(scripts, list): err(path + '.Scripts', 'Expected script array.')
            else:
                for k, line in enumerate(scripts): check_line(line, f'{path}.Scripts[{k}]')
        if kind == 'exit':
            if type(node.get('IsEnding')) is not bool: err(path + '.IsEnding', 'Expected boolean.')
            if targets: err(path + '.ConnectionsTo', 'Exit must have no outgoing targets.')
            check_line(node.get('NeScriptDirty'), path + '.NeScriptDirty')
    if len(entries) != 1:
        err('$.nodes', 'Expected exactly one entry node.')
    for nid, targets in edges.items():
        for target in targets:
            if target not in identities: err('node:' + nid, 'Missing branch target: ' + target)
    # Iterative graph walk supports long scenes without hitting Python's recursion limit.
    reachable, visited, active = set(), set(), set()
    for start in edges:
        if start in visited: continue
        stack = [(start, False)]
        while stack:
            node, leaving = stack.pop()
            if leaving:
                active.discard(node); visited.add(node); continue
            if node in active:
                err('node:' + node, 'Cycle detected; compiler requires an acyclic graph.'); continue
            if node in visited or node not in edges: continue
            active.add(node); stack.append((node, True))
            stack.extend((t, False) for t in reversed(edges[node]))
    pending = [entries[0]] if len(entries) == 1 and isinstance(entries[0], str) else []
    while pending:
        node = pending.pop()
        if node in reachable: continue
        reachable.add(node); pending.extend(edges.get(node, []))
    for nid in identities - reachable:
        warnings.append({'path': 'node:' + nid, 'message': 'Unreachable draft is not compiled.'})
    return errors, warnings


def empty_character():
    return dict(name='', faceId='00', startingPos=0, endingPos=0, displayOrder=1,
                emoticon=-1, action=0, effect=0, appear=0, shapeOverride=0)


def name_hash(name):
    spec = importlib.util.spec_from_file_location('aa_xxhash', SKILL / 'references' / 'xxhash32.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module.hash_name(name)


def new_line(line, bg, bgm):
    characters = [empty_character() for _ in range(6)]
    for char in line.get('stage', []):
        slot = char['slot']
        if type(slot) is not int or not 1 <= slot <= 5: raise ValueError('Stage slots must be 1..5.')
        if characters[slot]['name']: raise ValueError('Duplicate occupied stage slot.')
        record = empty_character(); record.update({k: v for k, v in char.items() if k != 'slot'})
        record.update(startingPos=slot, endingPos=char.get('endingPos', slot)); characters[slot] = record
    speaker = line.get('speaker')
    return dict(LineId=str(uuid.uuid4()), text=line.get('text', ''), popup=line.get('popup', ''),
                bgEffect=line.get('bgEffect', 0), bgName=name_hash(bg) if isinstance(bg, str) else bg,
                bgFriendlyName=bg if isinstance(bg, str) else '', sound=line.get('sound', ''),
                voice=line.get('voice', ''), transition=line.get('transition', 0), bgmId=bgm,
                selectionGroup=0, additionalPrompt=line.get('additionalPrompt', ''), characters=characters,
                speakerSlotNum=speaker if speaker is not None else 0, highlightedSlotNums=line.get('highlighted', []),
                isDialogScript=speaker is not None, placeText=line.get('placeText', ''))


def generate(source, target):
    if target.exists(): raise ValueError('generate creates new projects only. Edit existing AAP2 while preserving its IDs.')
    data = json.loads(source.read_text(encoding='utf-8-sig'))
    title = data.get('title')
    if title is None or (isinstance(title, str) and not title.strip()):
        title = data['name']
    lines = []
    bg, bgm = data.get('bg', 'BG_Black'), data.get('bgm', 999)
    for line in data['lines']:
        bg, bgm = line.get('bg', bg), line.get('bgm', bgm)
        lines.append(new_line(line, bg, bgm))
    if not lines: raise ValueError('A new scenario needs at least one line.')
    dialogue, exit_id = str(uuid.uuid4()), str(uuid.uuid4())
    ending = new_line({'text': data.get('ending', '')}, bg, bgm)
    project = dict(LegacySourceVersion='absent', FormatVersion=2, ProjectId=str(uuid.uuid4()),
                   ProjectName=data['name'], PreviewBgName=lines[0]['bgName'], PreviewHeader=data.get('header', ''),
                   PreviewTitle=title, nodes=[
                       dict(Title=title, Header=data.get('header', ''), Guid=EMPTY_ID, ConnectionsTo=[dialogue], X=0, Y=0, Kind='entry'),
                       dict(Scripts=lines, NodeName=None, Guid=dialogue, ConnectionsTo=[exit_id], X=300, Y=0, Kind='dialogue'),
                       dict(IsEnding=True, EndText=data.get('ending', ''), NeHeader='', NeTitle='', NeScriptDirty=ending,
                            Guid=exit_id, ConnectionsTo=[], X=600, Y=0, Kind='exit')])
    errors, warnings = validate(project, require_title=True)
    if errors: raise ValueError(json.dumps(errors, ensure_ascii=False))
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        stream.write(b'AAP2\n' + json.dumps(project, ensure_ascii=False, indent=2, allow_nan=False).encode('utf-8'))
    return dict(ok=True, project=str(target), warnings=warnings)


def discover():
    user = Path(os.environ.get('USERPROFILE', str(Path.home())))
    roots = [user / 'AppData' / 'LocalLow']
    packages = Path(os.environ.get('LOCALAPPDATA', str(user / 'AppData' / 'Local'))) / 'Packages'
    if packages.exists(): roots.extend(sorted(packages.glob('*/LocalCache/LocalLow')))
    candidates = []
    for root in roots:
        aa = root / 'foxxlight' / 'AzureArchive'; data = aa / 'data'
        catalog = aa / 'com.unity.addressables'; cache = root / 'Unity' / 'foxxlight_AzureArchive'
        settings = data / 'settings' / 'user_settings.json'
        custom = {}
        if settings.is_file():
            try:
                config = json.loads(settings.read_text(encoding='utf-8-sig'))
                custom = {k: config.get(k) for k in ['workspacePath', 'cachePath'] if config.get(k)}
            except (ValueError, OSError): custom = {'settings_error': str(settings)}
        if data.exists() or cache.exists() or catalog.exists():
            candidates.append(dict(local_low=str(root), data_root=str(data), data_exists=data.is_dir(),
                                   catalog=str(catalog), catalog_nonempty=catalog.is_dir() and any(p.stat().st_size for p in catalog.glob('catalog*.json')),
                                   cache=str(cache), cache_nonempty=cache.is_dir() and next(cache.iterdir(), None) is not None,
                                   custom_paths=custom))
    exe_candidates = []
    if os.environ.get('AZUREARCHIVE_EXE'): exe_candidates.append(Path(os.environ['AZUREARCHIVE_EXE']))
    exe_candidates.append(Path('E:/BaiduNetdiskDownload/AzureArchive_Win_1.0_beta/AzureArchive.exe'))
    for parent in [Path.cwd(), Path.cwd().parent]:
        exe_candidates.extend(parent.glob('AzureArchive*/AzureArchive.exe'))
    return dict(ok=True, executables=sorted({str(p.resolve()) for p in exe_candidates if p.is_file()}), candidates=candidates)


def select_exe(value):
    candidates = [Path(value)] if value else [Path(p) for p in discover()['executables']]
    if len(candidates) != 1 or not candidates[0].is_file():
        raise ValueError('Specify --exe; no unique AzureArchive executable was found.')
    return candidates[0].resolve()


def select_data_root(value):
    if value:
        path = Path(value).resolve()
        if not path.is_dir() or not (path / 'settings' / 'user_settings.json').is_file():
            raise ValueError('--data-root must identify an existing AzureArchive data directory with user settings.')
        return path
    candidates = [c for c in discover()['candidates'] if c['data_exists']]
    if len(candidates) != 1:
        raise ValueError('Multiple or no data roots found. Use discover and specify --data-root before publishing.')
    if candidates[0]['custom_paths'].get('workspacePath'):
        raise ValueError('Custom workspacePath is configured; confirm the actual --data-root.')
    return Path(candidates[0]['data_root']).resolve()


def install_bridge(exe):
    app = exe.parent
    required = [app / 'BepInEx/core/BepInEx.Unity.IL2CPP.dll', app / 'BepInEx/interop/Assembly-CSharp.dll']
    if not all(p.is_file() for p in required):
        raise ValueError('Native bridge requires this app\'s BepInEx 6 IL2CPP runtime and authoring API. No runtime was installed automatically.')
    source = SKILL / 'assets/compiler/AAKit.CompilerBridge.dll'
    target = app / 'BepInEx/plugins/AAKit.CompilerBridge.dll'
    if not source.is_file(): raise ValueError('Compiler bridge DLL is missing; rebuild with scripts/build_bridge.ps1.')
    if target.exists() and sha(source) == sha(target): return target
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists(): shutil.copy2(target, target.with_name(target.name + '.backup-' + uuid.uuid4().hex))
    temporary = target.with_name(target.name + '.tmp-' + uuid.uuid4().hex)
    shutil.copy2(source, temporary); os.replace(temporary, target)
    return target


def native_request(exe, command, args, job_dir, timeout=90):
    job_dir.mkdir(parents=True, exist_ok=False)
    job = job_dir / 'request.json'
    job.write_text(json.dumps(dict(command=command, args=args), ensure_ascii=False), encoding='utf-8')
    env = os.environ.copy(); env['AA_KIT_NATIVE_JOB'] = str(job)
    # Avoid inherited diagnostic switches activating an old probe or disabling BepInEx.
    for key in ['DOORSTOP_DISABLE', 'AA_KIT_SCHEMA_PROBE', 'AA_KIT_COMPILE_PROBE']: env.pop(key, None)
    cmd = [str(exe)]
    if command != 'play': cmd += ['-batchmode', '-nographics']
    cmd += ['-logFile', str(job_dir / 'player.log')]
    options = dict(cwd=exe.parent, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.name == 'nt' and command != 'play': options['creationflags'] = subprocess.CREATE_NO_WINDOW
    process = subprocess.Popen(cmd, **options)
    response = Path(str(job) + '.response.json'); deadline = time.monotonic() + timeout
    try:
        while time.monotonic() < deadline:
            if response.is_file():
                result = json.loads(response.read_text(encoding='utf-8-sig'))
                if command != 'play':
                    try: process.wait(timeout=5)
                    except subprocess.TimeoutExpired: process.terminate(); process.wait(timeout=5)
                result['job_directory'] = str(job_dir)
                return result
            if process.poll() is not None: raise RuntimeError(f'Native process exited {process.returncode} without response. See {job_dir}.')
            time.sleep(0.2)
        raise TimeoutError(f'Native request timed out after {timeout}s. See {job_dir}.')
    except BaseException:
        # Only terminate the child started here. Never kill a user's existing player.
        if process.poll() is None: process.kill(); process.wait()
        raise


def checked_build(source, build):
    aas, manifest_path = Path(build['scenario']), Path(build['build_manifest'])
    manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    if not aas.is_file() or aas.stat().st_size == 0: raise ValueError('Compiler returned an empty or absent scenario.')
    if manifest.get('source_file_version') != 'sha256:' + sha(source): raise ValueError('Source changed during compilation; build was not published.')
    if sha(aas) != manifest.get('scenario_sha256') or sha(aas) != build.get('scenario_sha256'):
        raise ValueError('Scenario SHA-256 does not match build manifest.')
    resources = Path(build['resources'])
    for file in manifest.get('resource_manifest', {}).get('files', []):
        # File records are verified further by the native compiler; no guessed field schema.
        relative = file.get('path') or file.get('relative_path')
        if relative:
            item = (resources / relative).resolve()
            if not item.is_relative_to(resources.resolve()) or not item.is_file():
                raise ValueError('Invalid or missing compiled resource: ' + str(relative))
    missing = manifest.get('resource_manifest', {}).get('missing_resources', [])
    if missing: raise ValueError('Build has missing resources and was not published: ' + json.dumps(missing, ensure_ascii=False))
    return aas, resources, manifest


def publish(source, build, data_root, name):
    if not name or name in ['.', '..'] or any(c in name for c in '<>:"/\\|?*') or name.endswith((' ', '.')):
        raise ValueError('Unsafe output name for Windows saves directory.')
    reserved = name.split('.')[0].upper()
    if reserved in ['CON', 'PRN', 'AUX', 'NUL'] or reserved in [f'{p}{i}' for p in ['COM', 'LPT'] for i in range(1, 10)]:
        raise ValueError('Reserved Windows output name.')
    aas, resources, manifest = checked_build(source, build)
    saves = data_root / 'saves'; saves.mkdir(parents=True, exist_ok=True)
    targets = [saves / (name + '.aas'), saves / (name + '.build.json'), saves / name]
    if any(p.is_symlink() or (hasattr(p, 'is_junction') and p.is_junction()) for p in [saves] + targets):
        raise ValueError('Publishing through links/junctions is not supported.')
    token = uuid.uuid4().hex
    staging = saves / ('.aa-kit-stage-' + token); staging.mkdir()
    backups = data_root / '.aa-kit-backups' / (time.strftime('%Y%m%d-%H%M%S') + '-' + token)
    moved, committed = [], []
    try:
        shutil.copy2(aas, staging / targets[0].name)
        if resources.is_dir(): shutil.copytree(resources, staging / name)
        else: (staging / name).mkdir()
        result_manifest = copy.deepcopy(manifest)
        result_manifest['scenario'] = targets[0].name; result_manifest['resources'] = name
        (staging / targets[1].name).write_text(json.dumps(result_manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        for target in targets:
            if target.exists():
                backups.mkdir(parents=True, exist_ok=True)
                os.replace(target, backups / target.name); moved.append(target)
        for target in targets:
            os.replace(staging / target.name, target); committed.append(target)
    except BaseException:
        for target in reversed(committed): os.replace(target, staging / target.name)
        for target in reversed(moved): os.replace(backups / target.name, target)
        raise
    finally:
        # Only remove our resolved staging directory, never resources or prior output.
        if staging.resolve().parent != saves.resolve(): raise ValueError('Unexpected staging parent.')
        shutil.rmtree(staging)
    return dict(scenario=str(targets[0]), build_manifest=str(targets[1]), resources=str(targets[2]),
                backup=str(backups) if moved else None)


def compile_project(args):
    source = args.project.resolve(); project = read_project(source)
    errors, warnings = validate(project, require_auto=args.require_auto, require_title=getattr(args, 'require_title', False))
    if errors: return dict(ok=False, stage='static_validation', errors=errors, warnings=warnings)
    exe = select_exe(args.exe)
    data_root = select_data_root(args.data_root) if not args.no_publish else None
    install_bridge(exe)
    work = args.work_dir.resolve() if args.work_dir else source.parent / '.aa-kit-builds'
    job_dir = work / uuid.uuid4().hex
    output = job_dir / 'build'
    result = native_request(exe, 'compile', dict(project=str(source), out=str(output), if_version='sha256:' + sha(source)), job_dir, args.timeout)
    if not result.get('ok'): return result
    _, _, manifest = checked_build(source, result['data'])
    omitted = manifest.get('resource_manifest', {}).get('omitted_missing_voices', [])
    if omitted and getattr(args, 'require_voices', False):
        raise ValueError('Referenced voices were omitted; build was not published: ' + json.dumps(omitted, ensure_ascii=False))
    result['static_warnings'] = warnings
    if omitted:
        result['static_warnings'].append(dict(path='$.voice', message='Missing voices were omitted: ' + json.dumps(omitted, ensure_ascii=False)))
    result['verification'] = dict(static=True, compiled=True, hashes=True, missing_resources=False, playback_reviewed=False)
    if data_root is not None:
        result['published'] = publish(source, result['data'], data_root, args.name or source.stem)
    if args.play:
        scenario = result.get('published', result['data'])['scenario']
        result['playback'] = native_request(exe, 'play', dict(scenario=scenario), work / uuid.uuid4().hex, args.timeout)
        if not result['playback'].get('ok'): result['ok'] = False
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('discover')
    p = sub.add_parser('validate'); p.add_argument('project', type=Path)
    p.add_argument('--require-auto', action='store_true', help='Require one Auto option in every choice for recording.')
    p.add_argument('--require-title', action='store_true', help='Require preview and entry scenario titles.')
    p = sub.add_parser('generate'); p.add_argument('input', type=Path); p.add_argument('project', type=Path)
    p = sub.add_parser('compile'); p.add_argument('project', type=Path)
    p.add_argument('--exe'); p.add_argument('--data-root'); p.add_argument('--name')
    p.add_argument('--no-publish', action='store_true'); p.add_argument('--play', action='store_true')
    p.add_argument('--work-dir', type=Path); p.add_argument('--timeout', type=int, default=90)
    p.add_argument('--require-auto', action='store_true', help='Reject choices without an Auto option before compilation.')
    p.add_argument('--require-title', action='store_true', help='Reject missing scenario titles before compilation.')
    p.add_argument('--require-voices', action='store_true', help='Reject omitted missing voices before publication.')
    args = parser.parse_args()
    try:
        if args.command == 'discover': result = discover()
        elif args.command == 'generate': result = generate(args.input.resolve(), args.project.resolve())
        elif args.command == 'validate':
            errors, warnings = validate(read_project(args.project), require_auto=args.require_auto, require_title=args.require_title); result = dict(ok=not errors, errors=errors, warnings=warnings)
        else:
            if not 15 <= args.timeout <= 3600: raise ValueError('Timeout must be 15..3600 seconds.')
            result = compile_project(args)
        dump(result); return 0 if result.get('ok') else 1
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, TimeoutError) as exc:
        dump(dict(ok=False, error=str(exc))); return 1


if __name__ == '__main__':
    # Keep installed skill directories free of interpreter cache artifacts.
    sys.dont_write_bytecode = True
    sys.exit(main())
