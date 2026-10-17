"""Dubbing invariants; GPU synthesis and native packaging are checked separately."""
import argparse
import copy
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import wave
import sys
sys.dont_write_bytecode = True
import aa_tool as aa
import dub_tool as dub


class DubbingChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = aa.read_project(aa.SKILL/'examples/Schale_Demo.aap2')
        self.source = self.root/'story.aap2'
        self.source.write_bytes(b'AAP2\n'+json.dumps(self.project, ensure_ascii=False).encode())
        refs = self.root/'refs'; refs.mkdir()
        self.wav = refs/'test.wav'
        with wave.open(str(self.wav), 'wb') as w:
            w.setparams((1, 2, 22050, 0, 'NONE', 'not compressed'))
            w.writeframes(struct.pack('<h', 2000)*22050)
        dub.save(refs/'refs.json', [dict(path_name='test', ref_wav=str(self.wav), source_clip='fixture')])
        characters = {line['characters'][line['speakerSlotNum']]['name']: 'test'
                      for line in dub.lines(self.project) if line['isDialogScript']}
        self.cast = self.root/'cast.json'
        dub.save(self.cast, dict(characters=characters))
        self.plan = self.root/'plan.json'
        self.args = argparse.Namespace(project=self.source, cast=self.cast, refs=refs, plan=self.plan, only=None)

    def prepared(self):
        dub.prepare(self.args)
        return dub.load(self.plan)

    def report(self, plan):
        rows = [dict(line_id=j['line_id'], voice=j['voice'], text=j['text'], lang=j['lang'],
                     wav=str(self.wav), sha256=aa.sha(self.wav), qc_flags=[]) for j in plan['jobs']]
        p = self.root/'report.json'
        dub.save(p, dict(plan_sha256=aa.sha(self.plan), lines=rows, listening_reviewed=False))
        return argparse.Namespace(plan=self.plan, report=p, output=self.root/'dubbed.aap2', allow_qc_warnings=False)

    def test_plan_covers_all_branches_and_preserves_existing_voice(self):
        spoken = [line for line in dub.lines(self.project) if line['isDialogScript']]
        spoken[0]['voice'] = 'user_voice'
        self.source.write_bytes(b'AAP2\n'+json.dumps(self.project).encode())
        plan = self.prepared()
        self.assertEqual({j['line_id'] for j in plan['jobs']}, {l['LineId'] for l in spoken[1:]})
        self.assertTrue(any(s['reason']=='existing voice preserved' for s in plan['skipped']))

    def test_missing_cast_fails_before_creating_plan(self):
        dub.save(self.cast, dict(characters={}))
        with self.assertRaisesRegex(ValueError, 'no silent skips'): dub.prepare(self.args)
        self.assertFalse(self.plan.exists())

    def test_line_override_uses_stable_id_and_keeps_subtitles(self):
        spoken = next(l for l in dub.lines(self.project) if l['isDialogScript'])
        lid = spoken['LineId']
        self.args.only = lid
        cast = dub.load(self.cast)
        cast['lines'] = {lid: dict(lang='JA', text='先生、ありがとう。', speaker='test')}
        dub.save(self.cast, cast)
        plan = self.prepared()
        self.assertEqual(len(plan['jobs']), 1)
        self.assertEqual(plan['jobs'][0]['lang'], 'JA')
        args = self.report(plan)
        original_hash = aa.sha(self.source)
        # Preserve arbitrary local resources and manifest fields when adding voices.
        pack = self.source.with_suffix(''); pack.mkdir()
        (pack/'user.txt').write_text('keep')
        dub.save(pack/'manifest.json', dict(VoiceOverrides=[], CustomField='keep'))
        dub.apply(args)
        modified = aa.read_project(args.output)
        expected = copy.deepcopy(self.project)
        next(l for l in dub.lines(expected) if l['LineId']==lid)['voice'] = plan['jobs'][0]['voice']
        self.assertEqual(modified, expected)
        self.assertEqual(aa.sha(self.source), original_hash)
        self.assertEqual((args.output.with_suffix('')/'user.txt').read_text(), 'keep')
        self.assertEqual(dub.load(args.output.with_suffix('')/'manifest.json')['CustomField'], 'keep')
        with self.assertRaises(ValueError): dub.apply(args)

    def test_stale_source_and_changed_audio_rejected(self):
        plan = self.prepared(); args = self.report(plan)
        before = self.source.read_bytes()
        self.source.write_bytes(before+b' ')
        with self.assertRaisesRegex(ValueError, 'Source changed'): dub.apply(args)
        self.source.write_bytes(before)
        self.wav.write_bytes(self.wav.read_bytes()+b'changed')
        with self.assertRaisesRegex(ValueError, 'Audio changed'): dub.apply(args)
        self.assertFalse(args.output.exists())

    def test_missing_coverage_and_qc_fail_without_output(self):
        plan = self.prepared(); args = self.report(plan)
        report = dub.load(args.report); original = copy.deepcopy(report)
        report['lines'].pop(); dub.save(args.report, report)
        with self.assertRaisesRegex(ValueError, 'coverage'): dub.apply(args)
        original['lines'][0]['qc_flags'] = ['long_silent_tail']; dub.save(args.report, original)
        with self.assertRaisesRegex(ValueError, 'QC warnings'): dub.apply(args)
        self.assertFalse(args.output.exists())

    def test_unsafe_voice_identifier_rejected(self):
        plan = self.prepared(); args = self.report(plan)
        plan['jobs'][0]['voice'] = '../escape'
        dub.save(self.plan, plan)
        with self.assertRaisesRegex(ValueError, 'identifiers'): dub.apply(args)

    def test_partial_model_directory_is_not_a_ready_deployment(self):
        model = self.root/'repo/checkpoints/hf_cache/w2v-bert-2.0'
        model.mkdir(parents=True)
        (model/'partial-download.bin').write_bytes(b'not a model')
        with self.assertRaisesRegex(ValueError, 'no automatic download'):
            dub.preflight(self.root/'repo')

    def test_missing_voice_compile_blocks_before_publish(self):
        args = argparse.Namespace(project=self.source, require_auto=True, require_title=True,
            require_voices=True, exe='unused', no_publish=False, data_root='unused', work_dir=self.root,
            timeout=90, name=None, play=False)
        manifest = dict(resource_manifest=dict(omitted_missing_voices=['missing']))
        with patch.object(aa, 'select_exe', return_value=self.root/'exe'), \
             patch.object(aa, 'select_data_root', return_value=self.root), \
             patch.object(aa, 'install_bridge'), \
             patch.object(aa, 'native_request', return_value=dict(ok=True, data={})), \
             patch.object(aa, 'checked_build', return_value=(None, None, manifest)), \
             patch.object(aa, 'publish') as publish:
            with self.assertRaisesRegex(ValueError, 'omitted'): aa.compile_project(args)
            publish.assert_not_called()


if __name__ == '__main__': unittest.main()
