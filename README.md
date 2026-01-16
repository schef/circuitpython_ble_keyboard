# circuitpython_ble_keyboard

## flash prebuild custom firmware
- `nrfjprog -f nrf52 --eraseall`
- `nrfjprog --program prebuild_firmware/s140_nrf52_6.1.1_softdevice.hex -f nrf52 --sectorerase --reset`
- `nrfjprog --program prebuild_firmware/pca10056_bootloader-0.9.2-39-g0147d71-dirty_nosd.hex --sectoranduicrerase -f nrf52 --reset`
- `nrfjprog --program prebuild_firmware/firmware.hex --sectorerase -f nrf52`

## build custom bootloader
- `git clone https://github.com/adafruit/Adafruit_nRF52_Bootloader`
- `cd Adafruit_nRF52_Bootloader`
- `python -m venv .venv`
- `source .venv/bin/activate`
- `pip install intelhex`
- `git submodule update --init --recursive`
- check `custom_board.diff`
- `nvim src/boards/pca10056/board.h`
- `nrfjprog -f nrf52 --eraseall`
- `make BOARD=pca10056 clean`
- `make BOARD=pca10056 sd`
- `make BOARD=pca10056 flash`

## build custom firmware
- `git clone https://github.com/adafruit/circuitpython`
- `cd circuitpython`
- `python -m venv .venv`
- `source .venv/bin/activate`
- `cd ports/nordic`
- `make fetch-port-submodules`
- `pip3 install -r requirements-dev.txt`
- `cd ../../`
- `pip3 install -r requirements-dev.txt`
- `make -C mpy-cross`
- `cd ports/nordic`
- `make BOARD=pca10056 clean`
- `make BOARD=pca10056 flash`

## install libs automaticly
- `pip3 install circup`
- `circup install asyncio`
- `circup install adafruit_ble`
- `circup install adafruit_bus_device`
- `circup install adafruit_hid`
- `circup install neopixel`
- `circup install simpleio`


## install libs manually
- `pip3 install circup`
- `circup --path ./extra install asyncio`
- `circup --path ./extra install adafruit_ble`
- `circup --path ./extra install adafruit_bus_device`
- `circup --path ./extra install adafruit_hid`
- `circup --path ./extra install neopixel`
- `circup --path ./extra install simpleio`
- `sudo mount /dev/sdc1 /mnt/usb`
- `sudo cp ./extras/lib /mnt/usb/ -rf`
- `sudo umount /mnt/usb`
