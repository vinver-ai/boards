<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Vinver, Inc. -->

# Vinver Board Manifest Schema (v1.0)

Each `.toml` file in `boards/` describes one ESP32 board variant. This document
defines every section, field, and type. The canonical "god board" reference is
[`template.toml`](template.toml).

## Sections Overview

```
[meta]              Board identity and chip info
[capabilities]      SDK public API index
[system]            Core pins, buses, power sensing, buttons
[drivers.*]         Self-contained peripheral configs (18 types)
[custom.*]          Escape hatch for unlisted peripherals
```

---

## `[meta]`

| Field                | Type     | Required | Description                              |
|----------------------|----------|----------|------------------------------------------|
| `id`                 | string   | yes      | Unique board ID, must match filename     |
| `family`             | string   | yes      | Board family (e.g., `esp32`, `lilygo`)   |
| `description`        | string   | yes      | Human-readable board name                |
| `chip`               | enum     | yes      | `esp32` `esp32s2` `esp32s3` `esp32c3` `esp32c6` `esp32h2` |
| `flash_size`         | string   | yes      | Flash size (e.g., `4MB`, `16MB`)         |
| `psram`              | boolean  | yes      | Whether board has PSRAM                  |
| `tier`               | enum     | yes      | `volume` or `gold`                       |
| `manifest_version`   | string   | yes      | Schema version (currently `1.0`)         |
| `min_runtime_version`| string   | yes      | Minimum HAL runtime version              |

---

## `[capabilities]`

The SDK index. Each entry maps a capability name to either a pin or a driver.

**Pin-based capability:**
```toml
led = {pin = "system.led_pin", type = "led"}
```

**Driver-based capability:**
```toml
display = {driver = "drivers.display", type = "display"}
```

**Custom capability:**
```toml
lidar = {driver = "custom.lidar", type = "custom"}
```

### Standard capability types

| Capability   | Source              | Type               |
|--------------|---------------------|--------------------|
| `led`        | `system.led_pin`    | `led`              |
| `button`     | `system.button_pin` | `button`           |
| `buzzer`     | `system.buzzer_pin` | `buzzer`           |
| `dac1`       | `system.dac1_pin`   | `dac`              |
| `dac2`       | `system.dac2_pin`   | `dac`              |
| `rgb_led`    | `system.led_pin`    | `addressable_rgb`  |
| `neopixel`   | `drivers.neopixel`  | `rgb_led`          |
| `display`    | `drivers.display`   | `display`          |
| `camera`     | `drivers.camera`    | `camera`           |
| `audio`      | `drivers.audio`     | `audio`            |
| `touch`      | `drivers.touch`     | `touch`            |
| `lora`       | `drivers.lora`      | `lora`             |
| `gps`        | `drivers.gps`       | `gps`              |
| `pmu`        | `drivers.pmu`       | `pmu`              |
| `sdcard`     | `drivers.sdcard`    | `sdcard`           |
| `ethernet`   | `drivers.ethernet`  | `ethernet`         |
| `can`        | `drivers.can`       | `can`              |
| `rs485`      | `drivers.rs485`     | `rs485`            |
| `nfc`        | `drivers.nfc`       | `nfc`              |
| `imu`        | `drivers.imu`       | `imu`              |
| `rtc`        | `drivers.rtc`       | `rtc`              |
| `env_sensor` | `drivers.env_sensor`| `env_sensor`       |
| `ir`         | `drivers.ir`        | `ir`               |
| `wifi_halow` | `drivers.wifi_halow`| `wifi_halow`       |

---

## `[system]`

Board infrastructure: core pins, buses, power sensing, buttons.

| Field          | Type      | Description                          |
|----------------|-----------|--------------------------------------|
| `led_pin`      | int       | Onboard LED GPIO (-1 = none)         |
| `button_pin`   | int       | Boot/user button GPIO                |
| `buzzer_pin`   | int?      | Buzzer GPIO                          |
| `dac1_pin`     | int?      | DAC channel 1 GPIO                   |
| `dac2_pin`     | int?      | DAC channel 2 GPIO                   |
| `reserved_pins`| int[]     | Flash/PSRAM pins (chip-dependent)    |

### `[system.i2c]` / `[system.i2c1]`

| Field  | Type | Default  | Description       |
|--------|------|----------|-------------------|
| `sda`  | int  | required | SDA GPIO          |
| `scl`  | int  | required | SCL GPIO          |
| `freq` | int  | 400000   | Bus frequency (Hz)|

### `[system.spi]`

| Field  | Type | Description |
|--------|------|-------------|
| `mosi` | int  | MOSI GPIO   |
| `miso` | int  | MISO GPIO   |
| `sck`  | int  | SCK GPIO    |

### `[system.uart]` / `[system.uart1]`

| Field  | Type | Default | Description     |
|--------|------|---------|-----------------|
| `tx`   | int  | required| TX GPIO         |
| `rx`   | int  | required| RX GPIO         |
| `baud` | int  | 115200  | Baud rate       |

### `[system.power]`

Simple ADC/GPIO power sensing (no IC). For PMU ICs, see `drivers.pmu`.

| Field         | Type | Description                |
|---------------|------|----------------------------|
| `battery_adc` | int? | Battery voltage ADC GPIO   |
| `vbus_sense`  | int? | USB power detect GPIO      |
| `vext`        | int? | External power control     |
| `charge_en`   | int? | Charge enable GPIO         |

### `[system.buttons]`

Named buttons beyond the main `button_pin`. Key-value pairs where keys are
button names and values are GPIO numbers.

```toml
[system.buttons]
up   = 13
down = 15
ok   = 11
```

---

## `[drivers.*]` — Standard Drivers

Each driver section is self-contained with all its pins. The HAL reads these
to auto-instantiate and configure hardware.

Common optional fields across drivers:

| Field           | Type    | Description                           |
|-----------------|---------|---------------------------------------|
| `init_priority` | int     | Lower = initializes first (0-100)     |
| `depends_on`    | str[]   | Bus/driver dependencies               |

### `[drivers.neopixel]` — Addressable RGB LED

| Field       | Type | Values              | Description        |
|-------------|------|---------------------|--------------------|
| `type`      | enum | `ws2812` `sk6812`   | LED IC type        |
| `pin`       | int  |                     | Data GPIO          |
| `power_pin` | int? |                     | Power gate GPIO    |
| `num_leds`  | int  |                     | Number of LEDs     |

### `[drivers.display]` — Display

| Field       | Type | Values                                          | Description       |
|-------------|------|-------------------------------------------------|-------------------|
| `type`      | enum | `st7789` `ssd1306` `ili9341` `gc9a01` `sh1106`  | Display IC        |
| `bus`       | enum | `spi` `i2c` `rgb`                                | Bus type          |
| `cs`        | int? |                                                   | Chip select (SPI) |
| `dc`        | int? |                                                   | Data/command (SPI)|
| `width`     | int? |                                                   | Pixels wide       |
| `height`    | int? |                                                   | Pixels tall       |
| `rst`       | int? |                                                   | Reset GPIO        |
| `backlight` | int? |                                                   | Backlight PWM     |
| `power_pin` | int? |                                                   | Power gate GPIO   |
| `addr`      | int? |                                                   | I2C address (hex) |

### `[drivers.camera]` — Camera (DVP parallel)

| Field       | Type | Values                      | Description      |
|-------------|------|-----------------------------|------------------|
| `type`      | enum | `ov2640` `ov5640` `ov3660`  | Sensor IC        |
| `d0`-`d7`   | int? |                             | Data bus GPIOs   |
| `xclk`      | int? |                             | External clock   |
| `pclk`      | int? |                             | Pixel clock      |
| `vsync`     | int? |                             | Vertical sync    |
| `href`      | int? |                             | Horizontal ref   |
| `sccb_sda`  | int? |                             | SCCB data        |
| `sccb_scl`  | int? |                             | SCCB clock       |
| `pwdn`      | int? |                             | Power down       |
| `reset`     | int? |                             | Hardware reset   |

### `[drivers.audio]` — Audio (I2S)

| Field        | Type | Values                              | Description     |
|--------------|------|-------------------------------------|-----------------|
| `type`       | enum | `i2s` `max98357` `es8311` `es7210`  | Audio IC        |
| `bclk`       | int? |                                     | Bit clock       |
| `lrck`       | int? |                                     | Word select     |
| `dout`       | int? |                                     | Data out        |
| `din`        | int? |                                     | Data in         |
| `mclk`       | int? |                                     | Master clock    |
| `speaker_en` | int? |                                     | Amp enable      |

### `[drivers.touch]` — Touch Panel

| Field  | Type | Values                               | Description     |
|--------|------|--------------------------------------|-----------------|
| `type` | enum | `cst816s` `gt911` `ft6336` `ft5x06`  | Touch IC        |
| `bus`  | enum | `i2c`                                 | Bus type        |
| `addr` | int? |                                       | I2C address     |
| `irq`  | int? |                                       | Interrupt GPIO  |
| `rst`  | int? |                                       | Reset GPIO      |

### `[drivers.lora]` — LoRa Radio

| Field  | Type | Values                                     | Description     |
|--------|------|--------------------------------------------|-----------------|
| `type` | enum | `sx1276` `sx1262` `sx1268` `sx1280` `llcc68`| Radio IC       |
| `bus`  | enum | `spi`                                       | Bus type        |
| `cs`   | int  |                                              | Chip select     |
| `rst`  | int  |                                              | Reset GPIO      |
| `irq`  | int  |                                              | Interrupt GPIO  |
| `busy` | int? |                                              | Busy pin (sx126x)|

### `[drivers.wifi_halow]` — WiFi HaLow (802.11ah)

| Field       | Type | Values              | Description      |
|-------------|------|---------------------|------------------|
| `type`      | enum | `mm6108` `nrc7292`  | HaLow IC         |
| `bus`       | enum | `spi`               | Bus type         |
| `cs`        | int  |                     | Chip select      |
| `irq`       | int  |                     | Interrupt GPIO   |
| `rst`       | int  |                     | Reset GPIO       |
| `power_pin` | int? |                     | Power enable     |

### `[drivers.gps]` — GPS Receiver

| Field  | Type | Values                     | Description     |
|--------|------|----------------------------|-----------------|
| `type` | enum | `neo-6m` `neo-m8n` `l76k`  | GPS module      |
| `tx`   | int  |                             | TX GPIO         |
| `rx`   | int  |                             | RX GPIO         |
| `baud` | int  | default: 9600               | UART baud rate  |
| `pps`  | int? |                             | PPS sync GPIO   |

### `[drivers.pmu]` — Power Management IC

| Field  | Type | Values                        | Description     |
|--------|------|-------------------------------|-----------------|
| `type` | enum | `axp192` `axp2101` `ip5306`   | PMU IC          |
| `bus`  | enum | `i2c`                          | Bus type        |
| `addr` | int? |                                | I2C address     |
| `irq`  | int? |                                | Interrupt GPIO  |

### `[drivers.sdcard]` — SD Card

| Field       | Type | Values        | Description        |
|-------------|------|---------------|--------------------|
| `bus`       | enum | `spi` `sdio`  | Interface type     |
| `cs`        | int? |               | Chip select (SPI)  |
| `detect`    | int? |               | Card detect GPIO   |
| `power_pin` | int? |               | Power gate GPIO    |
| `d0`-`d3`   | int? |               | SDIO data lines    |
| `clk`       | int? |               | SDIO clock         |
| `cmd`       | int? |               | SDIO command       |

### `[drivers.ethernet]` — Ethernet

| Field       | Type | Values                              | Description     |
|-------------|------|-------------------------------------|-----------------|
| `type`      | enum | `lan8720` `w5500` `dm9051` `rtl8201`| Ethernet IC     |
| `bus`       | enum | `rmii` `spi`                         | Interface type  |
| `mdc`       | int? |                                      | MDC (RMII)      |
| `mdio`      | int? |                                      | MDIO (RMII)     |
| `phy_addr`  | int? |                                      | PHY address     |
| `cs`        | int? |                                      | Chip select(SPI)|
| `irq`       | int? |                                      | Interrupt GPIO  |
| `power_pin` | int? |                                      | Power enable    |
| `rst`       | int? |                                      | Reset GPIO      |

### `[drivers.can]` — CAN Bus

| Field | Type | Description |
|-------|------|-------------|
| `txd` | int  | TX GPIO     |
| `rxd` | int  | RX GPIO     |

### `[drivers.rs485]` — RS-485

| Field | Type | Description           |
|-------|------|-----------------------|
| `txd` | int  | TX GPIO               |
| `rxd` | int  | RX GPIO               |
| `rts` | int? | Direction control GPIO|

### `[drivers.nfc]` — NFC

| Field  | Type | Values          | Description     |
|--------|------|-----------------|-----------------|
| `type` | enum | `pn532` `rc522` | NFC IC          |
| `bus`  | enum | `spi` `i2c`     | Bus type        |
| `cs`   | int? |                 | Chip select     |
| `irq`  | int? |                 | Tag detect GPIO |

### `[drivers.imu]` — IMU / Accelerometer

| Field  | Type | Values                                      | Description     |
|--------|------|---------------------------------------------|-----------------|
| `type` | enum | `bma423` `mpu6050` `lsm6ds3` `bmi270` `qmi8658` | IMU IC     |
| `bus`  | enum | `i2c` `spi`                                  | Bus type        |
| `addr` | int? |                                              | I2C address     |
| `irq`  | int? |                                              | Interrupt GPIO  |

### `[drivers.rtc]` — Real-Time Clock

| Field  | Type | Values              | Description     |
|--------|------|---------------------|-----------------|
| `type` | enum | `pcf8563` `ds3231`  | RTC IC          |
| `bus`  | enum | `i2c`               | Bus type        |
| `addr` | int? |                     | I2C address     |
| `irq`  | int? |                     | Alarm interrupt |

### `[drivers.env_sensor]` — Environmental Sensor

| Field  | Type | Values                            | Description     |
|--------|------|-----------------------------------|-----------------|
| `type` | enum | `bme280` `sht30` `bmp280` `aht20` | Sensor IC      |
| `bus`  | enum | `i2c` `spi`                        | Bus type        |
| `addr` | int? |                                    | I2C address     |

### `[drivers.ir]` — Infrared

| Field | Type | Description    |
|-------|------|----------------|
| `tx`  | int? | IR TX GPIO     |
| `rx`  | int? | IR RX GPIO     |

---

## `[custom.*]` — Custom Peripherals

Escape hatch for peripherals not covered by standard drivers. The HAL does
**not** auto-instantiate these — it exposes the config for the developer.

Rules:
- Must have a `type` field
- SDK access: `board.custom.<name>`
- Capability type must be `"custom"`

```toml
["custom.lidar"]
type = "vl53l0x"
bus  = "i2c"
int  = 3
shutdown = 4
```

---

## Quality Tiers

| Tier     | Description                                           |
|----------|-------------------------------------------------------|
| `volume` | Auto-extracted from Arduino `pins_arduino.h` headers  |
| `gold`   | Verified against official board schematics             |

Gold boards have been cross-validated by vision models against PDF schematics
and should be considered the authoritative source for pin mappings.
