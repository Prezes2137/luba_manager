async def execute_action(hass, action: str, zone: str):

    if not action:
        return

    if action.startswith("script."):
        hass.services.call(
            "script",
            "turn_on",
            {"entity_id": action.split("script.")[1]}
        )

    elif action.startswith("notify."):
        domain = action.split(".")[1]
        hass.services.call("notify", domain, {
            "message": f"Luba zone: {zone}"
        })

    elif action.startswith("shell_command."):
        cmd = action.split(".")[1]
        hass.services.call("shell_command", cmd)

    else:
        hass.bus.async_fire("luba_custom_action", {
            "zone": zone,
            "action": action
        })