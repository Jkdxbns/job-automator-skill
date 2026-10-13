---
name: reference-hardware-inventory
description: "Justin's owned boards/sensors (as of 2026-09-10) — check before proposing any project hardware or purchases"
metadata: 
  node_type: memory
  type: reference
  originSessionId: b3517308-bd3c-4152-a8c8-4d1c22446930
  modified: 2026-09-11T03:09:04.030Z
---

Owned as of 2026-09-10 (Justin's own list):

- **Boards:** BeagleBone Black, STM32 Nucleo-L476RG, Arduino Uno, Arduino Nano, ESP8266, Jetson Orin Nano Super, Raspberry Pi Pico
- **Sensors/modules:** MPU6050, ADXL345, fingerprint sensor, LCD matrix, VL53L0X, GPS M10, TF-Luna, I2C multiplexer, CAN modules (type unconfirmed: MCP2515 controller board vs bare transceiver)
- **Also:** a lot of robotic-arm and drone electronics, including motors

**How to apply:**
- Propose owned parts first. Only suggest buying something that isn't on this list.
- The Arduinos are 5 V logic, so never wire them to BBB or Pi GPIO/UART.
- The Pico (running the `debugprobe` firmware) is the 3.3 V serial console fallback.
- The Jetson has gigabit Ethernet and is aarch64. See [[reference-jetson-ssh]]. In the telemetry gateway it is the k3s arm64 logger node on Ethernet; see [[project-telemetry-gateway]].
