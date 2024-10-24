INDIR=../lvgl_micropython/lib/micropython/ports/esp32/build-ESP32_GENERIC_S3-SPIRAM_OCT
OUTDIR=bin
cp $INDIR/bootloader/bootloader.bin $INDIR/partition_table/partition-table.bin $INDIR/micropython.bin $OUTDIR
