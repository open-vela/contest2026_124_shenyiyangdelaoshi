#!/usr/bin/env python3
"""Read-only checks for this ESP32-P4 flat-build release workflow."""
import argparse
import hashlib
import json
from pathlib import Path


def config(path):
    result = {}
    for line in path.read_text().splitlines():
        if line.startswith('CONFIG_') and '=' in line:
            key, value = line.split('=', 1)
            result[key] = value
        elif line.startswith('# CONFIG_') and line.endswith(' is not set'):
            result[line[2:-11]] = 'n'
    return result


def inspect(root):
    kernel = root / 'nuttx'
    cfg = config(kernel / '.config')
    target = kernel / 'boards/risc-v/esp32p4/esp32p4-function-ev-board/configs/usbnet/defconfig'
    saved = config(target)
    keys = ['CONFIG_ARCH_BOARD', 'CONFIG_INIT_ENTRYPOINT', 'CONFIG_INIT_STACKSIZE',
            'CONFIG_SYSTEM_NSH_STACKSIZE', 'CONFIG_NSH_BUILTIN_AS_COMMAND',
            'CONFIG_MM_KERNEL_HEAP', 'CONFIG_ESPRESSIF_SPIRAM_USER_HEAP',
            'CONFIG_SMARTFS_MAXNAMLEN', 'CONFIG_SYSLOG_CONSOLE']
    findings = []
    for key in keys:
        if key in cfg and key in saved and cfg[key] != saved[key]:
            findings.append({'kind': 'config_mismatch', 'key': key,
                             'actual': cfg[key], 'defconfig': saved[key]})
    if cfg.get('CONFIG_INIT_ENTRYPOINT') == '"nsh_main"' and cfg.get('CONFIG_NSH_BUILTIN_AS_COMMAND') == 'y':
        findings.append({'kind': 'execution_context', 'message': 'Measure INIT task stack; SYSTEM_NSH_STACKSIZE alone is insufficient.'})
    if cfg.get('CONFIG_MM_KERNEL_HEAP') == 'y' and cfg.get('CONFIG_ESPRESSIF_SPIRAM_USER_HEAP') != 'y':
        findings.append({'kind': 'review_heap_ranges', 'message': 'Check actual board heap/kheap ranges before concluding overlap.'})
    artifacts = {}
    for name in ['nuttx', 'nuttx.bin']:
        p = kernel / name
        artifacts[name] = {'exists': p.is_file()}
        if p.is_file():
            artifacts[name].update(bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    return {'scope': 'host static checks only; not a hardware acceptance test',
            'configuration': {k: cfg.get(k, 'unspecified') for k in keys},
            'findings': findings, 'artifacts': artifacts}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workspace', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(inspect(args.workspace), ensure_ascii=False, indent=2))
    except (OSError, ValueError) as e:
        parser.exit(2, f'Input error: {e}\n')
