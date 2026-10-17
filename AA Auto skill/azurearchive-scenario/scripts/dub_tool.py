#!/usr/bin/env python3
"""Plan AAP2 dubbing, render with local IndexTTS 2.5, attach project-local voices.

prepare/apply use stdlib; render runs in the existing IndexTTS Python environment.
No model downloads, global overrides, or source overwrites are performed.
"""
import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import sys
import time
import uuid
import wave

import aa_tool as aa

VERSION = '4.0'
KEYS = ['CharacterOverrides', 'VoiceOverrides', 'PopupOverrides', 'SoundOverrides',
        'BgOverrides', 'BgEffectOverrides', 'BgSpineOverrides', 'BgmOverrides']


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def lines(project):
    for node in project['nodes']:
        if node['Kind'] == 'dialogue':
            yield from node['Scripts']


def plain(text):
    # Strip known presentation markup only; never pass extra commands to the TTS.
    text = re.sub(r'<[^>]+>|\[(?:/?(?:color|size|b|i|u)|ruby)[^\]]*\]|\[_ruby\]', '', text)
    return text.replace('\r', '').strip()


def checked_plan(plan):
    if plan.get('version') != VERSION or not plan.get('jobs'):
        raise ValueError('Unsupported or empty dubbing plan.')
    if aa.sha(plan['source']) != plan['source_sha256']:
        raise ValueError('Source changed; prepare a new plan.')
    project = aa.read_project(plan['source'])
    ids = {line['LineId'] for line in lines(project)}
    planned = [job['line_id'] for job in plan['jobs']]
    voices = [job['voice'] for job in plan['jobs']]
    if len(set(planned)) != len(planned) or not set(planned) <= ids:
        raise ValueError('Plan has duplicate or unknown LineIds.')
    if len(set(voices)) != len(voices) or any(not re.fullmatch(r'aa_dub_[0-9a-f]{24}', v) for v in voices):
        raise ValueError('Invalid or duplicate generated voice identifiers.')
    return project


def prepare(args):
    source = args.project.resolve()
    project = aa.read_project(source)
    errors, _ = aa.validate(project)
    if errors:
        raise ValueError('Invalid project: ' + json.dumps(errors, ensure_ascii=False))
    if args.plan.exists():
        raise ValueError('Plan exists; choose a new path.')
    cast = load(args.cast)
    refs_root = args.refs.resolve()
    refs = {r['path_name']: r for r in load(refs_root/'refs.json')}
    selected = set(args.only.split(',')) if args.only else None
    jobs, skipped, unresolved = [], [], []
    for line in lines(project):
        lid = line['LineId']
        if selected is not None and lid not in selected:
            continue
        spec = cast.get('lines', {}).get(lid, {})
        if not isinstance(spec, dict):
            raise ValueError('Line override must be an object: ' + lid)
        if spec.get('skip') or line.get('voice'):
            skipped.append(dict(line_id=lid, reason='explicit skip' if spec.get('skip') else 'existing voice preserved'))
            continue
        slot = line['speakerSlotNum']
        character = line['characters'][slot]['name'] if line.get('isDialogScript') else ''
        speaker = spec.get('speaker', cast.get('characters', {}).get(character))
        if not line.get('isDialogScript') and not speaker:
            skipped.append(dict(line_id=lid, reason='narration without explicit voice'))
            continue
        text = plain(spec.get('text', line['text']))
        if not text:
            skipped.append(dict(line_id=lid, reason='no spoken text'))
            continue
        if speaker not in refs:
            unresolved.append(dict(line_id=lid, character=character, speaker=speaker))
            continue
        ref = refs[speaker]
        path = Path(ref['ref_wav'])
        if not path.is_absolute():
            path = refs_root/path
        if not path.is_file():
            # Allow moving a reference library while preserving its original provenance.
            path = refs_root/(speaker + '.wav')
        if not path.is_file():
            raise ValueError('Missing reference: ' + str(path))
        lang = spec.get('lang', cast.get('lang', 'ZH')).upper()
        if lang not in ('ZH', 'JA', 'EN', 'ES', 'AR'):
            raise ValueError('Unsupported language: ' + lang)
        factor = spec.get('duration_factor', 1.0)
        if not isinstance(factor, (int, float)) or not math.isfinite(factor) or not 0.5 <= factor <= 2:
            raise ValueError('duration_factor must be 0.5..2.')
        job = dict(line_id=lid, character=character, speaker=speaker, text=text, lang=lang,
                   ref_wav=str(path.resolve()), ref_sha256=aa.sha(path),
                   reference_provenance=ref, duration_factor=factor,
                   expect_slow=bool(spec.get('expect_slow', False)))
        identity = json.dumps([project['ProjectId'], lid, text, lang, job['ref_sha256'], factor], ensure_ascii=False)
        job['voice'] = 'aa_dub_' + hashlib.sha256(identity.encode()).hexdigest()[:24]
        jobs.append(job)
    if selected and selected - {line['LineId'] for line in lines(project)}:
        raise ValueError('--only contains unknown LineIds.')
    if unresolved:
        raise ValueError('Resolve cast before rendering (no silent skips): ' + json.dumps(unresolved, ensure_ascii=False))
    if not jobs:
        raise ValueError('No new spoken lines selected.')
    plan = dict(version=VERSION, source=str(source), source_sha256=aa.sha(source),
                title=project['PreviewTitle'], jobs=jobs, skipped=skipped,
                notes='AI-generated voice; listening review required. Text overrides do not change subtitles.')
    args.plan.parent.mkdir(parents=True, exist_ok=True)
    save(args.plan, plan)
    return dict(ok=True, plan=str(args.plan.resolve()), lines=len(jobs), skipped=skipped)


def metrics(path, text, expect_slow=False):
    import numpy as np
    import soundfile as sf
    audio, sr = sf.read(str(path), dtype='float32', always_2d=True)
    if len(audio) == 0 or not np.isfinite(audio).all() or sr <= 0:
        raise ValueError('Invalid or empty audio: ' + str(path))
    mono = audio.mean(axis=1)
    duration = len(mono)/sr
    active = np.flatnonzero(np.abs(mono) > 0.01)
    peak = float(np.max(np.abs(audio)))
    if not len(active):
        raise ValueError('Silent audio: ' + str(path))
    tail = (len(mono)-1-active[-1])/sr
    chars = sum(c.isalnum() for c in text)
    rate = chars/duration
    flags = []
    if tail > 2:
        flags.append('long_silent_tail')
    if chars >= 8 and rate < 2 and not expect_slow:
        flags.append('slow_or_repeating')
    return dict(seconds=duration, sample_rate=sr, peak=peak, silent_tail_s=tail,
                chars_per_second=rate, qc_flags=flags)


def preflight(repo):
    # These are the actual local files consumed by the verified 2.5 deployment,
    # rather than a directory-size heuristic that accepts partial-download blobs.
    required = ['config.yaml', 'gpt.pth', 'codec.pth', 's2mel.pth', 'feat1.pt', 'feat2.pt',
                'wav2vec2bert_stats.pt', 'multilingual_zh_ja_yue_char_del.tiktoken', 'pinyin.vocab',
                'hf_cache/campplus_cn_common.bin', 'hf_cache/w2v-bert-2.0/config.json',
                'hf_cache/w2v-bert-2.0/preprocessor_config.json',
                'hf_cache/bigvgan/config.json', 'hf_cache/bigvgan/bigvgan_generator.pt']
    model = repo/'checkpoints'
    missing = [p for p in required if not (model/p).is_file() or (model/p).stat().st_size == 0]
    if not any((model/'hf_cache/w2v-bert-2.0'/name).is_file() and
               (model/'hf_cache/w2v-bert-2.0'/name).stat().st_size > 0
               for name in ('model.safetensors', 'pytorch_model.bin')):
        missing.append('hf_cache/w2v-bert-2.0/model.safetensors or pytorch_model.bin')
    if missing:
        raise ValueError('Incomplete local IndexTTS 2.5 deployment; no automatic download: ' + ', '.join(missing))


def render(args):
    if not 1 <= args.retries <= 10:
        raise ValueError('--retries must be 1..10.')
    plan_path = args.plan.resolve()
    plan = load(plan_path)
    checked_plan(plan)
    for job in plan['jobs']:
        if aa.sha(job['ref_wav']) != job['ref_sha256']:
            raise ValueError('Reference changed; prepare a new plan.')
    repo = args.repo.resolve()
    preflight(repo)
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    import numpy as np
    import soundfile as sf
    import librosa
    sys.path.insert(0, str(repo))
    os.chdir(repo)
    from indextts.infer_v2_5 import IndexTTS2
    tts = IndexTTS2(cfg_path='checkpoints/config.yaml', model_dir='checkpoints', use_bf16=True)
    report = dict(version=VERSION, plan=str(plan_path), plan_sha256=aa.sha(plan_path),
                  model_repo=str(repo), config_sha256=aa.sha(repo/'checkpoints/config.yaml'),
                  retries=args.retries, gain_db=-4.0, lines=[], listening_reviewed=False)
    pieces, timeline, cursor = [], [], 0.0
    for job in plan['jobs']:
        candidates = []
        for attempt in range(args.retries):
            dest = out/(job['voice'] + f'.candidate-{attempt+1}.wav')
            start = time.monotonic()
            try:
                # Reference carries delivery; deliberately no one-hot emotion vector.
                tts.infer(spk_audio_prompt=job['ref_wav'], text=job['text'], lang=job['lang'],
                          output_path=str(dest), use_random=False,
                          duration_factor=job['duration_factor'], verbose=False)
                info = metrics(dest, job['text'], job['expect_slow'])
                candidates.append(dict(path=str(dest), synth_s=time.monotonic()-start, **info))
            except Exception as exc:
                candidates.append(dict(path=str(dest), error=str(exc)))
        valid = [c for c in candidates if 'error' not in c]
        if not valid:
            save(out/'failed.json', dict(line_id=job['line_id'], candidates=candidates))
            raise ValueError('All candidates failed: ' + job['line_id'])
        best = min(valid, key=lambda c: c['seconds'])
        # Explicit resampling prevents the mixed-rate octave bug recorded in the report.
        audio, sr = librosa.load(best['path'], sr=22050, mono=True)
        if sr != 22050:
            raise ValueError('Unexpected sample rate after resampling.')
        audio = audio * min(1.0, 0.999/max(float(np.max(np.abs(audio))), 1e-9)) * (10**(-4/20))
        dest = out/(job['voice'] + '.wav')
        sf.write(str(dest), audio, sr, subtype='PCM_16')
        info = metrics(dest, job['text'], job['expect_slow'])
        report['lines'].append(dict(line_id=job['line_id'], voice=job['voice'], speaker=job['speaker'],
                                    text=job['text'], lang=job['lang'], wav=str(dest),
                                    sha256=aa.sha(dest), candidates=candidates, **info))
        timeline.append(dict(start_s=cursor, line_id=job['line_id'], seconds=len(audio)/sr))
        pieces.extend([audio, np.zeros(int(sr*0.6), dtype=np.float32)])
        cursor += len(audio)/sr + 0.6
        save(out/'report.json', report)
        print(json.dumps(dict(rendered=job['line_id'], seconds=info['seconds'], qc=info['qc_flags'])), flush=True)
    sf.write(str(out/'_scene_full.wav'), np.concatenate(pieces[:-1]), 22050, subtype='PCM_16')
    save(out/'timeline.json', timeline)
    return dict(ok=True, report=str(out/'report.json'), preview=str(out/'_scene_full.wav'),
                qc_warnings=sum(bool(r['qc_flags']) for r in report['lines']), listening_reviewed=False,
                preview_note='Node-array order, including alternate branches; not an Auto-route playback.')


def apply(args):
    plan_path = args.plan.resolve()
    plan, report = load(plan_path), load(args.report)
    original = checked_plan(plan)
    source = Path(plan['source'])
    if aa.sha(source) != plan['source_sha256'] or aa.sha(plan_path) != report['plan_sha256']:
        raise ValueError('Source/plan changed; refuse stale audio.')
    rows = {r['line_id']: r for r in report['lines']}
    expected = {j['line_id'] for j in plan['jobs']}
    if len(rows) != len(report['lines']) or set(rows) != expected:
        raise ValueError('Rendered coverage does not match plan.')
    if any(r['qc_flags'] for r in rows.values()) and not args.allow_qc_warnings:
        raise ValueError('Audio QC warnings remain; listen and rerender, or explicitly --allow-qc-warnings after review.')
    for job in plan['jobs']:
        row = rows[job['line_id']]
        if row['voice'] != job['voice'] or row['text'] != job['text'] or row['lang'] != job['lang']:
            raise ValueError('Rendered line differs from plan.')
        if aa.sha(row['wav']) != row['sha256']:
            raise ValueError('Audio changed since rendering.')
        with wave.open(row['wav'], 'rb') as wav:
            if wav.getnframes() <= 0 or wav.getframerate() != 22050 or wav.getnchannels() != 1 or wav.getsampwidth() != 2:
                raise ValueError('Expected nonempty mono PCM16 22050 Hz WAV.')
    target = args.output.resolve()
    pack = target.with_suffix('')
    if target.suffix.lower() != '.aap2' or target.exists() or pack.exists() or target == source:
        raise ValueError('Choose a new .aap2 output with an unused companion folder; source is preserved.')
    target.parent.mkdir(parents=True, exist_ok=True)
    stage = target.parent/('.dub-staging-' + uuid.uuid4().hex)
    stage.mkdir()
    staged_pack = stage/pack.name
    original_pack = source.with_suffix('')
    if original_pack.is_dir():
        shutil.copytree(original_pack, staged_pack)
    else:
        staged_pack.mkdir()
    manifest_path = staged_pack/'manifest.json'
    manifest = load(manifest_path) if manifest_path.exists() else {k: [] for k in KEYS}
    voices = manifest.setdefault('VoiceOverrides', [])
    if not isinstance(voices, list):
        raise ValueError('VoiceOverrides must be an array.')
    project = copy.deepcopy(original)
    for line in lines(project):
        if line['LineId'] not in rows:
            continue
        row = rows[line['LineId']]
        relative = 'voices/' + row['voice'] + '.wav'
        if any(Path(str(v).replace('\\', '/')).stem == row['voice'] for v in voices):
            raise ValueError('Voice identifier conflicts with existing pack: ' + row['voice'])
        dest = staged_pack/relative
        if dest.exists():
            raise ValueError('Existing resource would be overwritten: ' + str(dest))
        dest.parent.mkdir(exist_ok=True)
        shutil.copy2(row['wav'], dest)
        voices.append(relative)
        line['voice'] = row['voice']
    save(manifest_path, manifest)
    staged_project = stage/target.name
    staged_project.write_bytes(b'AAP2\n' + json.dumps(project, ensure_ascii=False, indent=2).encode('utf-8'))
    if aa.sha(source) != plan['source_sha256'] or target.exists() or pack.exists():
        raise ValueError('Source or destination changed during attachment.')
    os.rename(staged_pack, pack)
    try:
        os.rename(staged_project, target)
    except BaseException:
        os.rename(pack, staged_pack)
        raise
    stage.rmdir()
    return dict(ok=True, project=str(target), resource_pack=str(pack), voiced_lines=len(rows),
                compiled=False, listening_reviewed=report.get('listening_reviewed', False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('project', type=Path); p.add_argument('--cast', type=Path, required=True)
    p.add_argument('--refs', type=Path, required=True); p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--only', help='Comma-separated LineIds for a pilot or incremental rerender.')
    p = sub.add_parser('render')
    p.add_argument('plan', type=Path); p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True); p.add_argument('--retries', type=int, default=3)
    p = sub.add_parser('apply')
    p.add_argument('plan', type=Path); p.add_argument('--report', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); p.add_argument('--allow-qc-warnings', action='store_true')
    args = parser.parse_args()
    try:
        result = globals()[args.command](args)
        aa.dump(result)
        return 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, ImportError) as exc:
        aa.dump(dict(ok=False, error=str(exc)))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
