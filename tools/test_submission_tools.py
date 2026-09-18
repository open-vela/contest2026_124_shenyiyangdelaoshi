#!/usr/bin/env python3
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = load('release', ROOT/'skills/esp32p4-openvela-bringup-debug/scripts/check_release.py')
exporter = load('exporter', ROOT/'tools/export_codex_contest.py')


class SubmissionToolsTest(unittest.TestCase):
    def test_config_readonly_and_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            kernel=root/'nuttx'
            target=kernel/'boards/risc-v/esp32p4/esp32p4-function-ev-board/configs/usbnet/defconfig'
            target.parent.mkdir(parents=True)
            target.write_text('CONFIG_SMARTFS_MAXNAMLEN=48\n')
            cfg=kernel/'.config'
            original='CONFIG_SMARTFS_MAXNAMLEN=16\n# CONFIG_MM_KERNEL_HEAP is not set\n'
            cfg.write_text(original)
            result=release.inspect(root)
            self.assertEqual(result['configuration']['CONFIG_MM_KERNEL_HEAP'],'n')
            self.assertEqual(result['findings'][0]['kind'],'config_mismatch')
            self.assertFalse(result['artifacts']['nuttx.bin']['exists'])
            self.assertEqual(cfg.read_text(),original)

    def test_export_excludes_private_instructions_and_reasoning(self):
        for kind,role in [('message','system'),('message','developer'),('reasoning','assistant')]:
            raw={'type':'response_item','payload':{'type':kind,'role':role,'content':[{'type':'output_text','text':'private'}]}}
            self.assertIsNone(exporter.convert(raw))

    def test_export_preserves_public_message(self):
        raw={'type':'response_item','payload':{'type':'message','role':'user','content':[{'type':'input_text','text':'nsh> free\nactual output'}]}}
        self.assertEqual(exporter.convert(raw),{'role':'user','text':'nsh> free\nactual output'})

    def test_redaction_and_hash_preservation(self):
        counts=[0]
        token='Aa9bCc8dEe7fGg6hIi5jKk4lMm3n'
        sha='d8b6cdd16e46cc0a0cef14e6e94a5702bf6da6c4cada3000e93e6b8eeefabae7'
        out=exporter.scrub({'key':token,'hash':sha,'nested':['Bearer '+token]},counts)
        self.assertNotIn(token,str(out))
        self.assertEqual(out['hash'],sha)
        self.assertGreater(counts[0],0)


if __name__=='__main__':
    unittest.main()
