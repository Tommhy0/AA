"""Behavior checks; native compilation is tested separately against the real player."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys
sys.dont_write_bytecode = True
import aa_tool as aa


class AuthoringChecks(unittest.TestCase):
    def setUp(self):
        self.project = aa.read_project(aa.SKILL / 'examples/Schale_Demo.aap2')

    def test_demo_and_real_branch_targets(self):
        self.assertFalse(aa.validate(self.project)[0])
        choice = next(n for n in self.project['nodes'] if n['Kind'] == 'choice')
        choice['Options'][0]['TargetNodeId'] = '12345678-0000-0000-0000-000000000000'
        self.assertTrue(any('Missing branch target' in e['message'] for e in aa.validate(self.project)[0]))

    def test_recording_requires_auto_and_rejects_foreign_option(self):
        choice = next(n for n in self.project['nodes'] if n['Kind'] == 'choice')
        chosen = choice['Options'][0]['OptionId']
        choice['DefaultOptionId'] = None
        errors, warnings = aa.validate(self.project)
        self.assertFalse(errors)
        self.assertTrue(any(w['path'].endswith('DefaultOptionId') for w in warnings))
        self.assertTrue(any(e['path'].endswith('DefaultOptionId') for e in aa.validate(self.project, require_auto=True)[0]))
        choice['DefaultOptionId'] = chosen.upper()
        self.assertFalse(aa.validate(self.project, require_auto=True)[0])
        choice['DefaultOptionId'] = '12345678-0000-0000-0000-000000000000'
        self.assertTrue(any(e['path'].endswith('DefaultOptionId') for e in aa.validate(self.project, require_auto=True)[0]))

    def test_recording_checks_every_choice_and_allows_no_choices(self):
        choice = next(n for n in self.project['nodes'] if n['Kind'] == 'choice')
        another = copy.deepcopy(choice)
        another['Guid'] = 'a1000009-0000-0000-0000-000000000009'
        for index, option in enumerate(another['Options'],1):
            option['OptionId'] = f'b900000{index}-0000-0000-0000-00000000000{index}'
        another['DefaultOptionId'] = None
        # Put a second choice on the actual route, preserving the original branch targets.
        target = choice['Options'][0]['TargetNodeId']
        for option in choice['Options']: option['TargetNodeId'] = another['Guid']
        self.project['nodes'].append(another)
        errors = aa.validate(self.project, require_auto=True)[0]
        self.assertEqual(len(errors),1)
        self.assertTrue(errors[0]['path'].endswith('DefaultOptionId'))
        # An interactive-only project without choice nodes needs no Auto marker.
        predecessor = next(n for n in self.project['nodes'] if choice['Guid'] in n.get('ConnectionsTo',[]))
        predecessor['ConnectionsTo'] = [target]
        self.project['nodes'] = [n for n in self.project['nodes'] if n['Kind']!='choice']
        self.assertFalse(aa.validate(self.project, require_auto=True)[0])

    def test_recording_compile_rejects_missing_auto_before_native_launch(self):
        choice = next(n for n in self.project['nodes'] if n['Kind'] == 'choice')
        choice['DefaultOptionId'] = None
        args = aa.argparse.Namespace(project=aa.SKILL/'examples/Schale_Demo.aap2', require_auto=True)
        with patch.object(aa, 'read_project', return_value=self.project), patch.object(aa, 'select_exe') as launch:
            result = aa.compile_project(args)
        self.assertFalse(result['ok'])
        self.assertEqual(result['stage'],'static_validation')
        launch.assert_not_called()

    def test_cycle_and_case_insensitive_identity(self):
        dialogue = next(n for n in self.project['nodes'] if n['Kind'] == 'dialogue')
        dialogue['ConnectionsTo'] = [dialogue['Guid']]
        self.assertTrue(any('Cycle' in e['message'] for e in aa.validate(self.project)[0]))
        duplicate = copy.deepcopy(dialogue); duplicate['Guid'] = duplicate['Guid'].upper()
        self.project['nodes'].append(duplicate)
        self.assertTrue(any('Duplicate node ID' in e['message'] for e in aa.validate(self.project)[0]))

    def test_occupied_speaker_and_malformed_types(self):
        line = next(n for n in self.project['nodes'] if n['Kind'] == 'dialogue')['Scripts'][1]
        line['speakerSlotNum'] = 4
        line['LineId'] = ['invalid']
        line['bgName'] = True
        errors = aa.validate(self.project)[0]
        self.assertTrue(any('occupy' in e['message'] for e in errors))
        self.assertTrue(any(e['path'].endswith('bgName') for e in errors))
        self.assertTrue(any(e['path'].endswith('LineId') for e in errors))

    def test_marker_and_duplicate_json_rejected(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            path = Path(directory) / 'bad.aap2'
            for raw in [b'\xef\xbb\xbfAAP2\n{}', b'AAP2\r\n{}', b'AAP2\n{"a":1,"a":2}']:
                path.write_bytes(raw)
                with self.assertRaises(ValueError): aa.read_project(path)

    def test_generator_refuses_existing_and_sets_scene(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root = Path(directory); source = root / 'input.json'; target = root / 'new.aap2'
            source.write_text(json.dumps(dict(name='Example', bg='BG_MainOffice', bgm=37,
                                             lines=[dict(text='one'), dict(text='two')])), encoding='utf8')
            aa.generate(source, target); original = target.read_bytes()
            project = aa.read_project(target)
            self.assertFalse(aa.validate(project)[0])
            lines = project['nodes'][1]['Scripts']
            self.assertEqual([(x['bgName'], x['bgmId']) for x in lines], [(1046815759, 37)] * 2)
            with self.assertRaises(ValueError): aa.generate(source, target)
            self.assertEqual(original, target.read_bytes())


class PublishingChecks(unittest.TestCase):
    def test_hash_mismatch_and_failed_publish_keep_old_output(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root = Path(directory); source = root / 'source.aap2'; source.write_bytes(b'source')
            build_dir = root / 'build'; build_dir.mkdir()
            aas = build_dir / 'scenario.aas'; aas.write_bytes(b'new scenario')
            resources = build_dir / 'scenario'; resources.mkdir()
            (resources / 'resource.txt').write_bytes(b'new resource')
            manifest = dict(source_file_version='sha256:' + aa.sha(source), scenario_sha256=aa.sha(aas),
                            scenario='scenario.aas', resources='scenario', resource_manifest=dict(files=[], missing_resources=[]))
            mp = build_dir / 'build.json'; mp.write_text(json.dumps(manifest), encoding='utf8')
            build = dict(scenario=str(aas), build_manifest=str(mp), resources=str(resources), scenario_sha256=aa.sha(aas))
            data = root / 'data'; saves = data / 'saves'; saves.mkdir(parents=True)
            (saves / 'Example.aas').write_bytes(b'old scenario')
            (saves / 'Example.build.json').write_bytes(b'old manifest')
            (saves / 'Example').mkdir(); (saves / 'Example/resource.txt').write_bytes(b'old resource')
            original_replace = aa.os.replace; calls = [0]
            def failing_replace(src, dst):
                calls[0] += 1
                if calls[0] == 5: raise OSError('Injected publication failure')
                return original_replace(src, dst)
            with patch.object(aa.os, 'replace', side_effect=failing_replace):
                with self.assertRaises(OSError): aa.publish(source, build, data, 'Example')
            self.assertEqual((saves / 'Example.aas').read_bytes(), b'old scenario')
            self.assertEqual((saves / 'Example.build.json').read_bytes(), b'old manifest')
            self.assertEqual((saves / 'Example/resource.txt').read_bytes(), b'old resource')
            aas.write_bytes(b'tampered')
            with self.assertRaises(ValueError): aa.publish(source, build, data, 'Example')
            self.assertEqual((saves / 'Example.aas').read_bytes(), b'old scenario')

    def test_success_backs_up_and_rewrites_manifest(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root = Path(directory); source = root / 'source'; source.write_bytes(b'source')
            aas = root / 'scenario.aas'; aas.write_bytes(b'new')
            manifest = dict(source_file_version='sha256:' + aa.sha(source), scenario_sha256=aa.sha(aas),
                            scenario='scenario.aas', resources='scenario', resource_manifest=dict(files=[], missing_resources=[]))
            mp = root / 'build.json'; mp.write_text(json.dumps(manifest), encoding='utf8')
            data = root / 'data'; saves = data / 'saves'; saves.mkdir(parents=True)
            (saves / 'Example.aas').write_bytes(b'old')
            build = dict(scenario=str(aas), build_manifest=str(mp), resources=str(root / 'missing-resource-dir'), scenario_sha256=aa.sha(aas))
            result = aa.publish(source, build, data, 'Example')
            self.assertEqual((Path(result['backup']) / 'Example.aas').read_bytes(), b'old')
            self.assertEqual((saves / 'Example.aas').read_bytes(), b'new')
            self.assertEqual(json.loads(Path(result['build_manifest']).read_text())['scenario'], 'Example.aas')


if __name__ == '__main__': unittest.main()
