# esp3d-homeassistant

Esp3d (or any serial wifi equivalent) integration with home assistant

<img width="200" alt="image" src="https://github.com/dbuezas/esp3d-homeassistant/assets/777196/ccb69055-0e8b-41cd-bbea-6f7d19376f05">
<img width="400" alt="image" src="https://github.com/dbuezas/esp3d-homeassistant/assets/777196/b614e39b-cb4f-47c1-9ac5-994e5acee072">
<img width="200" alt="image" src="https://github.com/dbuezas/esp3d-homeassistant/assets/777196/f019ab7f-a9ea-4cdb-80f2-0e4ced05e15c">


# Requirements

- Marlin firmware
- Serial to wifi adapter (like esp3d with telnet enabled)

## Auto updates require this marlin features:

- AUTO_REPORT_TEMPERATURES
- AUTO_REPORT_POSITION
- AUTO_REPORT_SD_STATUS

# Installation

<!-- ### Option 1: [HACS](https://hacs.xyz/) Link

1. Click [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=dbuezas&category=integration&repository=esp3d-homeassistant)
2. Restart Home Assistant -->

# Configuration

- Go to Settings > Integrations
- Click + ADD INTEGRATION and search for esp3d

### Option 1: [HACS](https://hacs.xyz/)

1. Or `HACS` > `Integrations` > `⋮` > `Custom Repositories`
2. `Repository`: paste the url of this repo
3. `Category`: Integration
4. Click `Add`
5. Close `Custom Repositories` modal
6. Click `+ EXPLORE & DOWNLOAD REPOSITORIES`
7. Search for `esp3d`
8. Click `Download`
9. Restart _Home Assistant_

### Option 2: Manual copy

1. Copy the `esp3d` folder inside `custom_components` of this repo to `/config/custom_components` in your Home Assistant instance
2. Restart _Home Assistant_


# Card example configs

## Movement & Temperature controls

<details>
  <summary>Controls</summary>

### Requires

- (optional) [card-mod](https://github.com/thomasloven/lovelace-card-mod)

```yaml
type: vertical-stack
cards:
  - square: false
    columns: 4
    type: grid
    cards:
      - show_name: true
        show_icon: true
        type: button
        name: Preheat
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        entity: sensor.ultimaker_nozzle
        icon: mdi:heat-wave
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              M104 S200
              M140 S50
      - type: button
        name: Cool down
        entity: sensor.ultimaker_nozzle
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        icon: mdi:snowflake-alert
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              M104 S0
              M140 S0
      - type: glance
        entities:
          - entity: binary_sensor.ultimaker_busy
            name: Busy
      - type: button
        entity: switch.3d_printer_tuya_plug_5_switch
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        name: Power
        icon: mdi:power
  - type: glance
    entities:
      - entity: sensor.ultimaker_nozzle
        name: Nozzle
      - entity: number.ultimaker_nozzle
        name: Target
      - entity: sensor.ultimaker_bed
        name: Bed
      - entity: number.ultimaker_bed
        name: Target
      - type: button
        name: Autofetch
        tap_action:
          action: toggle
        entity: switch.ultimaker_fetch_temperatures
  - square: false
    columns: 4
    type: grid
    cards:
      - type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        name: Home X
        entity: sensor.ultimaker_nozzle
        icon: mdi:axis-y-arrow
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: G28 X
      - type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        name: Home Y
        entity: sensor.ultimaker_nozzle
        icon: mdi:axis-x-arrow
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: G28 Y
      - type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        name: Home Z
        entity: sensor.ultimaker_nozzle
        icon: mdi:axis-z-arrow
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: G28 Z
      - type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        name: Home
        entity: sensor.ultimaker_nozzle
        icon: mdi:home
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: G28
  - square: true
    columns: 4
    type: grid
    cards:
      - type: button
        style: "ha-card { visibility: hidden}"
      - type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        entity: sensor.ultimaker_nozzle
        icon: mdi:arrow-up-bold
        name: " "
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |-
              G91
              G1 Y+10
              G90
      - type: button
        style: "ha-card { visibility: hidden}"
      - type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        name: Z -10
        entity: sensor.ultimaker_nozzle
        icon: mdi:arrow-up-bold-outline
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |-
              G91
              G1 Z-10
              G90
  - square: true
    columns: 4
    type: grid
    cards:
      - type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        name: " "
        entity: sensor.ultimaker_nozzle
        icon: mdi:arrow-left-bold
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |-
              G91
              G1 X-10
              G90
      - type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        name: " "
        entity: sensor.ultimaker_nozzle
        icon: mdi:circle
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: G1 X100 Y100
      - type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        name: " "
        entity: sensor.ultimaker_nozzle
        icon: mdi:arrow-right-bold
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |-
              G91
              G1 X+10
              G90
      - type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        entity: sensor.ultimaker_nozzle
        name: Motors Off
        icon: mdi:hand-back-left-off-outline
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: M84
  - square: true
    columns: 4
    type: grid
    cards:
      - type: button
        style: "ha-card { visibility: hidden}"
      - type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        name: " "
        entity: sensor.ultimaker_nozzle
        icon: mdi:arrow-down-bold
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |-
              G91 
              G1 Y-10 
              G90
      - type: button
        style: "ha-card { visibility: hidden}"
      - type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        name: Z +10
        entity: sensor.ultimaker_nozzle
        icon: mdi:arrow-down-bold-outline
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |-
              G91 
              G1 Z+10 
              G90
  - square: false
    columns: 4
    type: grid
    cards:
      - show_icon: false
        name: 10mm/s
        type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        entity: sensor.ultimaker_nozzle
        icon: mdi:home
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: G1 F600
      - show_icon: false
        name: 50mm/s
        type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        entity: sensor.ultimaker_nozzle
        icon: mdi:home
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: G1 F3000
      - show_icon: false
        name: 100mm/s
        type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        entity: sensor.ultimaker_nozzle
        icon: mdi:home
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: G1 F6000
      - show_icon: false
        name: 200mm/s
        type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        entity: sensor.ultimaker_nozzle
        icon: mdi:home
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: G1 F12000
  - square: false
    columns: 4
    type: grid
    cards:
      - show_icon: false
        name: 500mm/s²
        type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        entity: sensor.ultimaker_nozzle
        icon: mdi:home
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: M204 T500
      - show_icon: false
        name: 1000mm/s²
        type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        entity: sensor.ultimaker_nozzle
        icon: mdi:home
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: M204 T1000
      - show_icon: false
        name: 5000mm/s²
        type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        entity: sensor.ultimaker_nozzle
        icon: mdi:home
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: M204 T5000
      - show_icon: false
        name: 10000mm/s²
        type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        entity: sensor.ultimaker_nozzle
        icon: mdi:home
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: M204 T10000
  - square: false
    columns: 4
    type: grid
    cards:
      - show_icon: false
        name: E-10
        type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        entity: sensor.ultimaker_nozzle
        icon: mdi:home
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              G91
              G1 E-10 F400
              G90
      - show_icon: false
        name: E-1
        type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        entity: sensor.ultimaker_nozzle
        icon: mdi:home
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              G91
              G1 E-1 F400
              G90
      - show_icon: false
        name: E+1
        type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        entity: sensor.ultimaker_nozzle
        icon: mdi:home
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              G91
              G1 E+1 F400
              G90
      - show_icon: false
        name: E+10
        type: button
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        entity: sensor.ultimaker_nozzle
        icon: mdi:home
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              G91
              G1 E+10 F400
              G90
  - type: glance
    entities:
      - entity: sensor.ultimaker_x
        name: X
      - entity: sensor.ultimaker_y
        name: "Y"
      - entity: sensor.ultimaker_z
        name: Z
      - entity: sensor.ultimaker_e
        name: E
      - type: button
        name: Autofetch
        tap_action:
          action: toggle
        entity: switch.ultimaker_fetch_positions
```

</details>

<img width="200" alt="image" src="https://github.com/dbuezas/esp3d-homeassistant/assets/777196/ccb69055-0e8b-41cd-bbea-6f7d19376f05">

---

## Gcode, file and status controls

<details>
  <summary>Status card</summary>

### Requires

- (optional) [card-mod](https://github.com/thomasloven/lovelace-card-mod)

```yaml
type: vertical-stack
cards:
  - type: entity
    entity: sensor.ultimaker_notification
  - type: entities
    entities:
      - input_text.gcode_to_send
      - script.send_gcode
  - type: glance
    entities:
      - entity: sensor.ultimaker_current_byte
        name: Current
      - entity: sensor.ultimaker_total_bytes
        name: Total
      - entity: sensor.ultimaker_print_progress
        name: Progress
      - type: button
        name: Autofetch
        tap_action:
          action: toggle
        entity: switch.ultimaker_fetch_print_status
  - type: entities
    style: >
      {{'ha-card { opacity:.5; pointer-events: none }' if
      states('binary_sensor.ultimaker_is_printing') | bool == true else ''}}
    entities:
      - select.ultimaker_file_selector
  - square: false
    columns: 4
    type: grid
    cards:
      - show_name: true
        show_icon: true
        type: button
        name: Init card
        entity: sensor.ultimaker_nozzle
        icon: mdi:sd
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              M21
      - show_name: true
        show_icon: true
        type: button
        name: SD list
        entity: sensor.ultimaker_nozzle
        icon: mdi:feature-search-outline
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              M20 L
      - show_name: true
        show_icon: true
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        type: button
        name: Print
        entity: sensor.ultimaker_nozzle
        icon: mdi:play
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              M24
      - show_name: true
        show_icon: true
        type: button
        name: STOP
        entity: sensor.ultimaker_nozzle
        icon: mdi:stop
        tap_action:
          action: call-service
          confirmation:
            text: Are you sure to stop?
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              M524 ; Abort SD print
              M77 ; Stop print timer
              M18 ; Disable steppers
      - show_name: true
        show_icon: true
        type: button
        name: Break & Continue
        entity: sensor.ultimaker_nozzle
        icon: mdi:play-protected-content
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              M108
      - show_name: true
        show_icon: true
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        type: button
        name: Change filament
        entity: sensor.ultimaker_nozzle
        icon: mdi:reload
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              M104 S200
              M600 R200
      - show_name: true
        show_icon: true
        type: button
        name: Fetch mesh
        entity: sensor.ultimaker_nozzle
        icon: mdi:grid
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              M420 V
      - show_name: true
        show_icon: true
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        type: button
        name: Load filament
        entity: sensor.ultimaker_nozzle
        icon: mdi:login
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              M701
      - show_name: true
        show_icon: true
        style: >-
          {{'ha-card { opacity:.5; pointer-events: none }' if
          states('binary_sensor.ultimaker_is_printing') | bool else ''}}
        type: button
        name: Unload filament
        entity: sensor.ultimaker_nozzle
        icon: mdi:logout
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              M702
  - square: false
    columns: 4
    type: grid
    cards:
      - show_name: false
        show_icon: true
        type: button
        entity: sensor.ultimaker_nozzle
        icon: mdi:arrow-left
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              G1 X0 F18000
      - show_name: false
        show_icon: true
        type: button
        entity: sensor.ultimaker_nozzle
        icon: mdi:arrow-right
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              G1 X200 F18000
      - show_name: false
        show_icon: true
        type: button
        entity: sensor.ultimaker_nozzle
        icon: mdi:arrow-up
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              G1 Y200 F18000
      - show_name: false
        show_icon: true
        type: button
        entity: sensor.ultimaker_nozzle
        icon: mdi:arrow-down
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              G1 Y0 F18000
      - show_name: false
        show_icon: true
        type: button
        entity: sensor.ultimaker_nozzle
        icon: mdi:arrow-up-down
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              G1 Y0 F1200
              G1 Y200 F1200
              G1 Y0 F1200
              G1 Y200 F1200
              G1 Y0 F1200
              G1 Y200 F1200
              G1 Y0 F1200
              G1 Y200 F1200
              G1 Y0 F1200
              G1 Y200 F1200
              G1 Y0 F1200
              G1 Y200 F1200
              G1 Y0 F1200
              G1 Y200 F1200
              G1 Y0 F1200
              G1 Y200 F1200
              G1 Y0 F1200
              G1 Y200 F1200
              G1 Y0 F1200
              G1 Y200 F1200
      - show_name: false
        show_icon: true
        type: button
        entity: sensor.ultimaker_nozzle
        icon: mdi:arrow-left-right
        tap_action:
          action: call-service
          service: esp3d.send_gcode
          target:
            device_id: 5b5929effa7b6fcff77688017dee3d24
          data:
            gcode: |
              G1 X0 F1200
              G1 X200 F1200
              G1 X0 F1200
              G1 X200 F1200
              G1 X0 F1200
              G1 X200 F1200
              G1 X0 F1200
              G1 X200 F1200
              G1 X0 F1200
              G1 X200 F1200
              G1 X0 F1200
              G1 X200 F1200
              G1 X0 F1200
              G1 X200 F1200
              G1 X0 F1200
              G1 X200 F1200
              G1 X0 F1200
              G1 X200 F1200
              G1 X0 F1200
              G1 X200 F1200
```

</details>

<img width="200" alt="image" src="https://github.com/dbuezas/esp3d-homeassistant/assets/777196/f019ab7f-a9ea-4cdb-80f2-0e4ced05e15c">

---

## Bed level & printed object visualisation

<details>
  <summary>3d visualization</summary>
  
  ### Requires

- [plotly-graph-card](https://github.com/dbuezas/lovelace-plotly-graph-card)

```yaml
type: custom:plotly-graph
entities:
  - entity: binary_sensor.ultimaker_mesh
    internal: true
    attribute: x
    filters:
      - filter: "y"
      - store_var: x
  - entity: binary_sensor.ultimaker_mesh
    internal: true
    attribute: "y"
    filters:
      - filter: "y"
      - store_var: "y"
  - entity: binary_sensor.ultimaker_mesh
    internal: true
    attribute: z
    filters:
      - filter: "y"
      - store_var: z
    fn: |
      $ex {
        const indexes = [0];
        for (let i = 1; i< vars.z.ys.length;i++){
          const last = JSON.stringify(vars.z.ys[i-1]);
          const curr = JSON.stringify(vars.z.ys[i]);
          if (curr != last) indexes.push(i);
        }
        vars.xs = vars.x.ys.filter((_,i)=>indexes.includes(i)).map(ys=>ys.map((y, _,{length})=>y*200/(length-1)));
        vars.ys = vars.y.ys.filter((_,i)=>indexes.includes(i)).map(ys=>ys.map((y, _,{length})=>y*200/(length-1)));
        vars.zs = vars.z.ys.filter((_,i)=>indexes.includes(i)) 
      }
  - entity: ""
    type: surface
    name: third
    showlegend: true
    colorscale: Hot
    x: $ex vars.xs.at(-1)
    "y": $ex vars.ys.at(-1)
    z: $ex vars.zs.at(-1)
  - entity: ""
    opacity: 0.3
    showscale: false
    type: surface
    name: third
    showlegend: true
    colorscale: Greens
    x: $ex vars.x.ys.at(-2)
    "y": $ex vars.y.ys.at(-2)
    z: $ex vars.z.ys.at(-2)
  - entity: sensor.ultimaker_x
    internal: true
    filters:
      - resample: 2s
      - store_var: xx
  - entity: sensor.ultimaker_y
    internal: true
    filters:
      - resample: 2s
      - store_var: yy
  - entity: sensor.ultimaker_z
    internal: true
    filters:
      - resample: 2s
      - store_var: zz
  - entity: ""
    type: scatter3d
    mode: markers
    showlegend: true
    marker:
      size2: 2
      size: |
        $ex vars.xx.ys.map((_,i,all)=>i==all.length-1?10:2)
      color: >-
        $ex vars.xx.ys.map((_,i,all)=>i==all.length-1?"red":"rgba(50, 50, 217,
        0.3)")
    line:
      color: rgba(50, 50, 217, 0.3)
      width: 1
    fn: |
      $ex {
        vars.min_i = vars.zz.ys.findLastIndex((z,i, zs) => zs[i-1]-1>=z)
        if (vars.min_i==-1)vars.min_i=0; 
      }
    x: $ex vars.xx.ys.slice(vars.min_i)
    "y": $ex vars.yy.ys.slice(vars.min_i)
    z: $ex vars.zz.ys.slice(vars.min_i)
refresh_interval: auto
hours_to_show: 6h
raw_plotly_config: true
layout:
  margin:
    t: 0
    l: 0
    r: 0
    b: 0
  height: 500
  scene:
    annotations:
      - x: $fn ({ vars }) => vars.xx.ys.at(-1)
        "y": $fn ({ vars }) => vars.yy.ys.at(-1)
        z: $fn ({ vars }) => vars.zz.ys.at(-1)
        text: now
        showarrow: tru
        arrowhead: 1
    aspectratio:
      x: 1
      "y": 1
      z: 1
    xaxis:
      title: X
      domain:
        - 0
        - 1
      range:
        - 0
        - 200
    yaxis:
      title: "Y"
      domain:
        - 0
        - 1
      range:
        - 0
        - 200
    zaxis:
      title: Z
      domain:
        - 0
        - 1
      range:
        - -1
        - 200
```
</details>

<img width="400" alt="image" src="https://github.com/dbuezas/esp3d-homeassistant/assets/777196/b614e39b-cb4f-47c1-9ac5-994e5acee072">

---
## Text to speech notification when print finished

<details>
  <summary>Print finish phone notification</summary>

```yaml
alias: Notify 3d print ready
description: ""
trigger:
  - platform: numeric_state
    entity_id:
      - sensor.ultimaker_print_progress
    above: .99
condition: []
action:
  - service: notify.mobile_app_pixel_7
    data:
      message: TTS
      data:
        tts_text: Printer Finishing
        ttl: 0
        priority: high
mode: single
```
</details>

--

## Phone progredd notification 

<details>
  <summary>Progress notification</summary>

  ```yaml
alias: Notify print progress
description: Notify print progress
trigger:
  - platform: state
    entity_id:
      - sensor.ultimaker_progress
condition: []
action:
  - service: notify.mobile_app_pixel_7
    data:
      message: |
        {{ trigger.to_state.state }}% complete
      data:
        notification_icon: mdi:printer-3d
        tag: print_progress
        clickAction: /lovelace/ultimaker
        sticky: true
mode: single
```
</details>
