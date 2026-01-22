# circuitpython_ble_keyboard

## disable JLink Mass storage device
- `JLinkExe -device NRF52840_XXAA -if SWD -speed 4000 -autoconnect 1`
- `MSDDisable`

## flash prebuild custom firmware
- `nrfjprog -f nrf52 --eraseall`
- `nrfjprog -f nrf52 --program prebuild_firmware/s140_nrf52_6.1.1_softdevice.hex --sectorerase --reset`
- `nrfjprog -f nrf52 --program prebuild_firmware/pca10056_bootloader-0.9.2-39-g0147d71-dirty_nosd.hex --sectoranduicrerase --verify --reset`
- `nrfjprog -f nrf52 --program prebuild_firmware/firmware.hex --sectorerase`
- `nrfjprog -f nrf52 --erasepage 0xFF000`
- `nrfjprog -f nrf52 --memwr 0xFF000 --val 0x00000001`
- `nrfjprog -f nrf52 --reset`

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


## get libs manually
- `pip3 install circup`
- `circup --path ./extra install asyncio`
- `circup --path ./extra install adafruit_ble`
- `circup --path ./extra install adafruit_bus_device`
- `circup --path ./extra install adafruit_hid`
- `circup --path ./extra install neopixel`
- `circup --path ./extra install simpleio`

## install libs manually
- `sudo mount /dev/sdc1 /mnt/usb`
- `sudo cp ./extras/lib /mnt/usb/ -rf`
- `sudo umount /mnt/usb`
