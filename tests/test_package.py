"""Exercise the real package validator in disposable package copies."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('SKILL.md', 'README.md', 'CHANGELOG.md', '.claude-plugin',
                     '.cursor-plugin', 'scripts', 'references'):
            source = ROOT / name
            target = self.root / name
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)

    def validate(self):
        return subprocess.run(
            [sys.executable, str(self.root / 'scripts/validate-package.py')],
            capture_output=True, text=True, encoding='utf-8',
        )

    def test_original_package_passes(self):
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_duplicate_skill_pattern_is_rejected(self):
        with (self.root / 'SKILL.md').open('a', encoding='utf-8') as stream:
            stream.write('\n### 26. Re-explaining what the reader knows\n')
        result = self.validate()
        self.assertNotEqual(result.returncode, 0, 'Duplicate SKILL pattern passed')
        self.assertIn('Duplicate SKILL.md pattern number', result.stderr)

    def test_duplicate_readme_pattern_is_rejected(self):
        path = self.root / 'README.md'
        row = next(line for line in path.read_text(encoding='utf-8').splitlines()
                   if line.startswith('| 26 |'))
        with path.open('a', encoding='utf-8') as stream:
            stream.write('\n' + row + '\n')
        result = self.validate()
        self.assertNotEqual(result.returncode, 0, 'Duplicate README pattern passed')
        self.assertIn('Duplicate README.md pattern number', result.stderr)

    def mutate(self, name, old, new):
        path = self.root / name
        text = path.read_text(encoding='utf-8')
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding='utf-8')

    def test_pattern_gap_is_rejected(self):
        self.mutate('SKILL.md', '### 26.', '### 28.')
        self.assertNotEqual(self.validate().returncode, 0)

    def test_version_mismatch_is_rejected(self):
        path = self.root / '.cursor-plugin/plugin.json'
        manifest = json.loads(path.read_text(encoding='utf-8'))
        major, minor, patch = map(int, manifest['version'].split('.'))
        manifest['version'] = f'{major + 1}.{minor}.{patch}'
        path.write_text(json.dumps(manifest), encoding='utf-8')
        self.assertNotEqual(self.validate().returncode, 0)

    def test_invalid_section_reference_is_rejected(self):
        self.mutate('SKILL.md', '§1', '§999')
        self.assertNotEqual(self.validate().returncode, 0)

    def test_readme_renamed_pattern_is_rejected(self):
        self.mutate('README.md', '**Not X but Y**', '**Changed name**')
        self.assertNotEqual(self.validate().returncode, 0)


    def test_missing_linked_reference_is_rejected(self):
        for name in ('preservation-examples.md', 'preservation-cases.json', 'evaluation.md'):
            with self.subTest(reference=name):
                path = self.root / 'references' / name
                original = path.read_bytes()
                path.unlink()
                try:
                    result = self.validate()
                    self.assertNotEqual(result.returncode, 0, 'Missing reference passed')
                    self.assertIn('Missing linked reference', result.stderr)
                finally:
                    path.write_bytes(original)


if __name__ == '__main__':
    unittest.main()
