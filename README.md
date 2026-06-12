# 🌿 Luba Manager (HACS Integration)

Smart mowing scheduler for Home Assistant.

## Features
- Zone-based mowing logic
- Weather-aware scheduling
- Queue system
- Custom actions per zone
- Safety gate (rain / cooldown)
- Event-driven architecture

## Installation (HACS)

1. Add this repo to HACS → Integrations
2. Restart Home Assistant
3. Add integration: **Luba Manager**

## Manual install

Copy `custom_components/luba_manager` to HA config.

## Events

- `luba_zone_executed`

## Services

- `luba_manager.plan`
- `luba_manager.run`