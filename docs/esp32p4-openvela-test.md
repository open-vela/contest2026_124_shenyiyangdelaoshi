# ESP32-P4 openvela Port Build and Test

## 1. Environment

Workspace paths used for this port:

```text
openvela workspace: /home/test/ai_completion/openvela-esp32p4
contest repo:        /home/test/ai_completion/openvela-esp32p4/contest2026_124_shenyiyangdelaoshi
NuttX tree:          /home/test/ai_completion/openvela-esp32p4/nuttx
```

Activate the prepared build environment:

```bash
source /home/test/ai_completion/openvela-esp32p4-env.sh
cd "$OPENVELA_HOME"
```

Check the toolchain:

```bash
openvela-esp32p4-check
```

Expected key output:

```text
riscv-none-elf-gcc (xPack GNU RISC-V Embedded GCC x86_64) 14.2.0
esptool v5.3.1
```

## 2. Source Baseline

The ESP32-P4 port is based on openvela PR 342:

```text
https://github.com/open-vela/nuttx/pull/342
```

Local NuttX branch:

```bash
cd "$OPENVELA_HOME/nuttx"
git switch work-esp32p4-port
```

The build uses a local cache of Espressif HAL to avoid network access during
the build:

```text
/home/test/ai_completion/openvela-esp32p4/nxtmpdir/esp-hal-3rdparty
```

If the cache is missing, restore it from the previous working Apache NuttX
ESP32-P4 port:

```bash
mkdir -p "$OPENVELA_HOME/nxtmpdir"
touch "$OPENVELA_HOME/nxtmpdir/.keep"
cp -a /home/test/esp32p4-nuttx/nuttx/arch/risc-v/src/esp32p4/esp-hal-3rdparty \
  "$OPENVELA_HOME/nxtmpdir/esp-hal-3rdparty"
```

## 3. Build

Build the USB console NSH image:

```bash
source /home/test/ai_completion/openvela-esp32p4-env.sh
cd "$OPENVELA_HOME"
./build.sh esp32p4-function-ev-board:usbconsole -j1
```

Do not use the full path form for this smoke build:

```text
boards/risc-v/esp32p4/esp32p4-function-ev-board/configs/usbconsole
```

That form builds the image, but the current `build.sh` path parser can fail
during the final `savedefconfig` copy step. The board-name form above completes
cleanly.

The selected config disables UART0 and routes the console through the board USB
serial/JTAG interface:

```text
# CONFIG_ESPRESSIF_UART0 is not set
CONFIG_ESPRESSIF_USBSERIAL=y
CONFIG_SYSTEM_NSH=y
CONFIG_EXAMPLES_HELLO=y
```

Successful build output includes:

```text
LD: nuttx
MKIMAGE: NuttX binary
Successfully created ESP32-P4 image.
Generated: nuttx.bin
```

Generated files:

```text
/home/test/ai_completion/openvela-esp32p4/nuttx/nuttx
/home/test/ai_completion/openvela-esp32p4/nuttx/nuttx.bin
/home/test/ai_completion/openvela-esp32p4/nuttx/nuttx.hex
```

Verified local artifact sizes:

```text
nuttx      378K
nuttx.bin  224K
nuttx.hex  404K
```

## 4. Flash

Put the ESP32-P4-Function-EV-Board into download mode and identify the serial
port. Common Linux device names are `/dev/ttyACM0`, `/dev/ttyUSB0`, or another
`/dev/ttyACM*` / `/dev/ttyUSB*` device.

Flash `nuttx.bin` at offset `0x2000`:

```bash
source /home/test/ai_completion/openvela-esp32p4-env.sh
cd "$OPENVELA_HOME/nuttx"
"$ESPTOOL" -c esp32p4 -p /dev/ttyACM0 -b 921600 write_flash 0x2000 nuttx.bin
```

Important: ESP32-P4 boots this image from flash offset `0x2000`. Flashing at
`0x0` causes ROM boot failures such as `invalid header`.

## 5. USB Console Test

For the `usbconsole` config, no USB-TTL adapter is needed. Use the same board
USB connection for flashing and for the NSH console. After flashing or reset,
Linux may re-enumerate the board as a different `/dev/ttyACM*` device.

Check the available ports:

```bash
ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```

Open a serial console:

```bash
minicom -D /dev/ttyACM0 -b 115200
```

or:

```bash
picocom -b 115200 /dev/ttyACM0
```

Reset the board. A successful boot reaches the NSH prompt:

```text
nsh>
```

Basic commands:

```text
help
uname -a
free
ps
mount
hello
```

Run the scheduler/libc smoke test:

```text
ostest
```

Note: `ostest` is not enabled in the local `usbconsole` and `usbnet` smoke
configs unless `CONFIG_TESTING_OSTEST=y` is added.

The PR baseline reports NSH, `ostest`, PSRAM, LCD, and touch verified on real
ESP32-P4-Function-EV-Board hardware.

## 6. Ethernet over USB Console

For Ethernet testing without a USB-TTL adapter, use the local `usbnet` config.
It keeps USB serial/JTAG as the console and enables ESP32-P4 EMAC, DHCP,
`ping`, and `iperf`:

```bash
source /home/test/ai_completion/openvela-esp32p4-env.sh
cd "$OPENVELA_HOME"
./build.sh esp32p4-function-ev-board:usbnet -j1
```

Verified local artifact sizes for the Ethernet image:

```text
nuttx      763K
nuttx.bin  375K
nuttx.hex  928K
```

Current verified Ethernet image:

```text
/home/test/ai_completion/openvela-esp32p4/nuttx/nuttx.bin
size: 383924 bytes
time: 2026-09-10 21:06:32 +0800
```

Key enabled config items:

```text
# CONFIG_ESPRESSIF_UART0 is not set
CONFIG_ESPRESSIF_USBSERIAL=y
CONFIG_ESPRESSIF_EMAC=y
CONFIG_NET=y
CONFIG_NET_ETHERNET=y
CONFIG_NETINIT_DHCPC=y
CONFIG_NSH_NETINIT=y
# CONFIG_NSH_ARCHINIT is not set
CONFIG_SYSTEM_EMACINIT=y
CONFIG_SYSTEM_DHCPC_RENEW=y
CONFIG_SYSTEM_PING=y
CONFIG_NETUTILS_IPERF=y
```

Do not enable `CONFIG_BOARD_LATE_INITIALIZE` or `CONFIG_NSH_ARCHINIT` for the
USB-console Ethernet smoke image. A 2026-09-10 20:53 build that initialized
board bringup from `board_late_initialize()` and a 2026-09-10 21:01 build that
used `CONFIG_NSH_ARCHINIT=y` both failed to reach NSH reliably on the local
board. The 2026-09-10 21:06 image defers EMAC bringup to a manual `emacinit`
command so the USB console can reach `nsh>` first.

If the board is already running the bad early-initialization image and the
serial console only shows the ROM banner or reports read errors, close the
terminal, hold the download/BOOT button as required by the board, tap RESET,
check the current `/dev/ttyACM*` or `/dev/ttyUSB*` name, and flash the new
`nuttx.bin` over it.

After flashing `nuttx.bin`, open the USB console first. Confirm NSH is alive
before touching Ethernet:

```text
help
hello
emacinit
```

Then initialize Ethernet manually and check whether `eth0` appears:

```text
emacinit
mkdir /proc
mount -t procfs /proc
ifconfig
```

If the board booted before the Ethernet cable or DHCP server was ready, renew
the address:

```text
renew eth0
ifconfig
```

Basic network checks:

```text
ping 192.168.1.1
ping 8.8.8.8
```

Replace `192.168.1.1` with the actual gateway shown by your network.

For throughput testing, start an iperf server on a PC connected to the same
LAN:

```bash
iperf -s
```

Then run the client on NSH, replacing the IP with the PC address:

```text
iperf -c 192.168.1.100
```

## 7. Current Local Patch

One compatibility patch was needed when building this PR against the current
openvela workspace:

```text
nuttx/include/nuttx/net/usrsock.h
```

Reason: the minimal NSH config has `CONFIG_NET` disabled, but an always-included
usrsock RPMSG header compiled an inline helper that called `net_sem_timedwait2`.
The local fix keeps the network path unchanged when `CONFIG_NET=y`, and uses
normal semaphore waits when `CONFIG_NET` is disabled.

The local Ethernet-over-USB-console config also needs the ESP32-P4 EMAC Kconfig
entries to be visible from:

```text
nuttx/arch/risc-v/src/esp32p4/Kconfig
```

Reason: this PR carries ESP32-P4 EMAC sources and an `ethernet` defconfig, but
the EMAC Kconfig symbol was not reachable from the active ESP32-P4 Kconfig
include path in this workspace.

## 8. Rebuild and Clean

Incremental rebuild:

```bash
source /home/test/ai_completion/openvela-esp32p4-env.sh
cd "$OPENVELA_HOME"
./build.sh esp32p4-function-ev-board:usbnet -j8
```

Clean this board config:

```bash
source /home/test/ai_completion/openvela-esp32p4-env.sh
cd "$OPENVELA_HOME"
./build.sh esp32p4-function-ev-board:usbnet distclean
```

After `distclean`, keep the HAL cache available under `nxtmpdir` before the
next build.
