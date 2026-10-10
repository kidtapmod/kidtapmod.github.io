"""Check exact reset bytes and updates over a reused runtime bundle."""
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reset_overlay import apply_reset_overlay, reset_files, verify_reset_archive
from start_web import apply_root_updates
ROOT = Path(__file__).resolve().parents[1]

class ResetDeploymentTests(unittest.TestCase):
    def test_exact_reset_in_android_and_ios_archives(self):
        with tempfile.TemporaryDirectory() as temp:
            resource = Path(temp)
            apply_reset_overlay(resource, '1.64.1')
            for prefix in ('com.garena.game.kgvn/files/Resources/1.64.1/', 'Resources/1.64.1/'):
                stream = io.BytesIO()
                with zipfile.ZipFile(stream, 'w') as archive:
                    for name, path in reset_files('1.64.1').items():
                        self.assertEqual((resource / name).read_bytes(), path.read_bytes())
                        archive.write(resource / name, prefix + name)
                with zipfile.ZipFile(stream) as archive:
                    verify_reset_archive(archive, prefix, '1.64.1')

    def test_reused_bundle_gets_assets_and_reset_and_preserves_jobs(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            (target / 'web_jobs').mkdir()
            keep = target / 'web_jobs/existing.txt'
            keep.write_text('keep')
            apply_root_updates(target)
            self.assertEqual((target / 'web_index.html').read_bytes(), (ROOT / 'web_index.html').read_bytes())
            for name, path in reset_files('1.64.1').items():
                self.assertEqual((target / 'ResetFiles/1.64.1' / name).read_bytes(), path.read_bytes())
                self.assertEqual((target / 'Resources_1/1.64.1' / name).read_bytes(), (ROOT / 'Resources_1/1.64.1' / name).read_bytes())
            self.assertTrue((target / 'assets/roles/28.png').is_file())
            self.assertEqual(keep.read_text(), 'keep')

if __name__ == '__main__':
    unittest.main()
