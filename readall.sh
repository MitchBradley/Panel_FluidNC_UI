#!/bin/sh
if test "$PORT" = ""; then
  echo "Usage: PORT=/dev/ttyUSB0 ./read_vfs.sh"
  exit 1
fi
~/.espressif/python_env/idf5.2_py3.10_env/bin/python  \
    -m esptool -p $PORT --chip esp32 -b 921600 \
    --before default_reset --after hard_reset \
    read_flash 0x0000 0x400000 fluidnc.bin
