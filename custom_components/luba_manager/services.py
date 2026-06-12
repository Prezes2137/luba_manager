async def execute_action(hass, action: str, zone: str):

    if not action:
        return

    action = action.strip()

    if action == "test_notify":
        await hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "Luba Manager",
                "message": f"Test trigger for zone: {zone}",
            },
            blocking=True,
        )
        return

    if action.startswith("script."):
        await hass.services.async_call(
            "script",
            "turn_on",
            {"entity_id": action},
            blocking=True,
        )

    elif action.startswith("notify."):
        notify_service = action.split(".", 1)[1]
        await hass.services.async_call(
            "notify",
            notify_service,
            {"message": f"Luba zone: {zone}"},
            blocking=True,
        )

    elif action.startswith("shell_command."):
        shell_service = action.split(".", 1)[1]
        await hass.services.async_call(
            "shell_command",
            shell_service,
            blocking=True,
        )

    else:
        hass.bus.async_fire("luba_custom_action", {
            "zone": zone,
            "action": action
        })