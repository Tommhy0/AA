"""Behavior checks for identity, source boundaries and bounded retrieval."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import character_tool as ct


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


class CharacterTests(unittest.TestCase):
    def setUp(self):
        self.student = dict(jp='テスト',name='测试',aliases=['Test'],base_id=1,profile=None,
                            variants=[dict(id=1,label='测试',aliases=[]),
                                      dict(id=2,label='测试（泳装）',aliases=['テスト（水着）'])])
        self.index = dict(students=[self.student],provenance=dict(repository='https://example.test/repo',
                         commit='abc',file_hashes={}))

    def test_alias_and_variant_identity(self):
        student, variant = ct.resolve('test',self.index)
        self.assertIs(student,self.student)
        self.assertIsNone(variant)
        self.assertEqual(ct.resolve('测试(泳装)',self.index)[1]['id'],2)
        self.assertEqual(ct.resolve('２',self.index)[1]['id'],2)

    def test_unknown_and_ambiguous_names_do_not_guess(self):
        with self.assertRaises(ValueError): ct.resolve('缺失',self.index)
        self.index['students'].append({**self.student,'jp':'另一个'})
        with self.assertRaises(ValueError): ct.resolve('测试',self.index)

    def test_multiline_and_teacher_choices(self):
        records = ct.parse_dialogue(['**テスト**: 一行','续行','','> **先生（選択肢）**: 老师选择'], 'bond')
        self.assertEqual(len(records),1)
        self.assertEqual(records[0]['text'],'一行\n续行')
        self.assertEqual((records[0]['line'],records[0]['end']),(1,2))

    def test_momo_answers_marked_uncertain_until_next_section(self):
        rows = ct.parse_dialogue(['## Group 1','**テスト**: 日常','','## Answer (0)',
                                 '**テスト**: 可疑回答','','## Group 2','**テスト**: 下一段'], 'momo')
        self.assertEqual([r['uncertain'] for r in rows],[False,True,False])

    def test_same_folder_variants_filtered_and_results_bounded(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = root/'絆ストーリー'/'テスト';folder.mkdir(parents=True)
            for cid in (1,2):
                raw = f'---\ncharacter_id: {cid}\n---\n\n**テスト**: 同一台词\n\n**テスト**: 同一台词\n\n**テスト**: 新反应\n'
                path=folder/f'{cid}.md';path.write_text(raw,encoding='utf-8',newline='\n')
                self.index['provenance']['file_hashes'][path.relative_to(root).as_posix()]=digest(raw)
            rows=ct.search(self.index,self.student,root,category='bond',character_id=2,limit=1)
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]['metadata']['character_id'],'2')
            self.assertTrue(rows[0]['snapshot_match'])
            self.assertIn('/blob/abc/',rows[0]['url'])
            rows=ct.search(self.index,self.student,root,category='bond',character_id=2,limit=10)
            self.assertEqual(len(rows),2)

    def test_changed_corpus_does_not_return_old_pinned_link(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);folder=root/'絆ストーリー';folder.mkdir()
            path=folder/'test.md';path.write_text('**テスト**: 改后的台词',encoding='utf-8')
            self.index['provenance']['file_hashes']['絆ストーリー/test.md']=digest('旧版本')
            row=ct.search(self.index,self.student,root,category='bond')[0]
            self.assertFalse(row['snapshot_match'])
            self.assertIsNone(row['url'])

    def test_momo_uncertain_answers_excluded_from_search(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);folder=root/'モモトーク';folder.mkdir()
            (folder/'1_テスト.md').write_text('## Answer (0)\n**テスト**: 错误归属\n\n## Group 2\n**テスト**: 学生正文',encoding='utf-8')
            rows=ct.search(self.index,self.student,root,category='momo',character_id=1)
            self.assertEqual([r['text'] for r in rows],['学生正文'])

    def test_explicit_missing_corpus_is_not_silently_replaced(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError): ct.corpus_root(str(Path(temp)/'missing'))

    def test_bundled_identities_are_unambiguous(self):
        index=ct.load_index()
        for student in index['students']:
            self.assertEqual(ct.resolve(student['jp'],index)[0]['jp'],student['jp'])
            for variant in student['variants']:
                self.assertEqual(ct.resolve(str(variant['id']),index)[0]['jp'],student['jp'])

    def test_bundled_card_sources_are_not_template_placeholders(self):
        index=ct.load_index()
        cards=[s for s in index['students'] if s['profile']]
        self.assertEqual(len(cards),72)
        for student in cards:
            self.assertEqual({e['label'] for e in student['evidence']} & {'P','L','B','R'},{'P','L','B','R'})
            self.assertEqual(next(e for e in student['evidence'] if e['label']=='B')['character_id'],student['base_id'])
            self.assertTrue((ct.INDEX.parent/student['profile']).is_file())


if __name__ == '__main__':
    unittest.main()
