if ["$PORT" = ""]; then
  echo "Usage: PORT=/dev/ttyUSB0 ./read_vfs.sh"
  exit 1
fi
~/.espressif/python_env/idf5.2_py3.10_env/bin/python  \
    -m esptool -p $PORT --chip esp32s3 -b 230400 \
    --before default_reset --after hard_reset \
    read_flash 0x2b0000 0x150000 bin/vfs.bin
