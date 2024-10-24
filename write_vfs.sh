if ["$PORT" = ""]; then
  echo "Usage: PORT=/dev/ttyUSB0 ./write_vfs.sh"
  exit 1
fi
~/.espressif/python_env/idf5.2_py3.10_env/bin/python  \
    -m esptool -p $PORT --chip esp32s3 -b 230400 \
    --before default_reset --after hard_reset \
    write_flash \
    --flash_mode dio --flash_size 4MB --flash_freq 80m \
    0x2b0000 bin/vfs.bin
popd
 
