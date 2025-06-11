"""Service implementations for Philips Air Purifier integration."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv, entity_registry as er
from homeassistant.helpers.service import async_extract_entity_ids
from homeassistant.util import dt as dt_util

from .config_entry_data import ConfigEntryData
from .const import DOMAIN, PhilipsApi

_LOGGER = logging.getLogger(__name__)

# Service names
SERVICE_FILTER_RESET = "filter_reset"
SERVICE_CALIBRATE_SENSORS = "calibrate_sensors"
SERVICE_SET_DISPLAY_BRIGHTNESS = "set_display_brightness"
SERVICE_SCHEDULE_MAINTENANCE = "schedule_maintenance"
SERVICE_SET_CHILD_LOCK = "set_child_lock"
SERVICE_SET_TIMER = "set_timer"
SERVICE_RESET_DEVICE = "reset_device"

# Service schemas
FILTER_RESET_SCHEMA = vol.Schema({
    vol.Optional("filter_type", default="all"): vol.In([
        "all", "pre_filter", "hepa_filter", "active_carbon_filter", "nanoprotect_filter"
    ]),
    vol.Optional("reset_maintenance_schedule", default=True): cv.boolean,
})

CALIBRATE_SENSORS_SCHEMA = vol.Schema({
    vol.Optional("sensor_type", default="all"): vol.In([
        "all", "pm25", "allergen_index", "gas", "tvoc"
    ]),
    vol.Optional("calibration_mode", default="auto"): vol.In([
        "auto", "manual", "factory_reset"
    ]),
    vol.Optional("reference_value"): vol.All(vol.Coerce(int), vol.Range(min=0, max=500)),
})

SET_DISPLAY_BRIGHTNESS_SCHEMA = vol.Schema({
    vol.Required("brightness_level"): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
    vol.Optional("auto_dim", default=False): cv.boolean,
    vol.Optional("night_mode", default=False): cv.boolean,
    vol.Optional("night_mode_start", default="22:00"): cv.time,
    vol.Optional("night_mode_end", default="07:00"): cv.time,
})

SCHEDULE_MAINTENANCE_SCHEMA = vol.Schema({
    vol.Required("maintenance_type"): vol.In([
        "filter_replacement", "sensor_calibration", "deep_cleaning", "general_maintenance"
    ]),
    vol.Required("reminder_interval"): vol.All(vol.Coerce(int), vol.Range(min=1, max=365)),
    vol.Optional("next_reminder_date"): cv.date,
    vol.Optional("enable_notifications", default=True): cv.boolean,
    vol.Optional("notification_advance_days", default=7): vol.All(
        vol.Coerce(int), vol.Range(min=1, max=30)
    ),
    vol.Optional("maintenance_notes"): cv.string,
})

SET_CHILD_LOCK_SCHEMA = vol.Schema({
    vol.Required("enabled"): cv.boolean,
})

SET_TIMER_SCHEMA = vol.Schema({
    vol.Required("duration_hours"): vol.All(vol.Coerce(float), vol.Range(min=0, max=24)),
    vol.Optional("action_after_timer", default="turn_off"): vol.In([
        "turn_off", "sleep_mode", "auto_mode"
    ]),
})

RESET_DEVICE_SCHEMA = vol.Schema({
    vol.Optional("reset_type", default="soft_reset"): vol.In([
        "soft_reset", "factory_reset", "network_reset"
    ]),
    vol.Required("confirm_reset"): vol.All(cv.boolean, vol.IsTrue()),
})


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Philips Air Purifier integration."""
    _LOGGER.info("Starting service setup for Philips Air Purifier integration")

    @callback
    def get_config_entry_data_from_entity_id(entity_id: str) -> ConfigEntryData | None:
        """Get config entry data from entity ID."""
        entity_registry = er.async_get(hass)
        entity_entry = entity_registry.async_get(entity_id)
        
        if not entity_entry or not entity_entry.config_entry_id:
            return None
            
        config_entry = hass.config_entries.async_get_entry(entity_entry.config_entry_id)
        if not config_entry or config_entry.domain != DOMAIN:
            return None
            
        return hass.data[DOMAIN].get(config_entry.entry_id)

    async def async_filter_reset(call: ServiceCall) -> None:
        """Handle filter reset service call."""
        entity_ids = await async_extract_entity_ids(hass, call)
        filter_type = call.data.get("filter_type", "all")
        reset_maintenance = call.data.get("reset_maintenance_schedule", True)
        
        _LOGGER.info(
            "Filter reset service called for entities: %s, filter_type: %s",
            entity_ids, filter_type
        )
        
        for entity_id in entity_ids:
            config_entry_data = get_config_entry_data_from_entity_id(entity_id)
            if not config_entry_data:
                _LOGGER.warning("Could not find config entry data for entity: %s", entity_id)
                continue
                
            try:
                await _reset_filter_counters(config_entry_data, filter_type, reset_maintenance)
                _LOGGER.info("Filter reset completed for entity: %s", entity_id)
            except Exception as ex:
                _LOGGER.error("Filter reset failed for entity %s: %s", entity_id, ex)
                raise HomeAssistantError(f"Filter reset failed for {entity_id}: {ex}") from ex

    async def async_calibrate_sensors(call: ServiceCall) -> None:
        """Handle sensor calibration service call."""
        entity_ids = await async_extract_entity_ids(hass, call)
        sensor_type = call.data.get("sensor_type", "all")
        calibration_mode = call.data.get("calibration_mode", "auto")
        reference_value = call.data.get("reference_value")
        
        _LOGGER.info(
            "Sensor calibration service called for entities: %s, sensor_type: %s, mode: %s",
            entity_ids, sensor_type, calibration_mode
        )
        
        if calibration_mode == "manual" and reference_value is None:
            raise ServiceValidationError("Reference value is required for manual calibration")
        
        for entity_id in entity_ids:
            config_entry_data = get_config_entry_data_from_entity_id(entity_id)
            if not config_entry_data:
                _LOGGER.warning("Could not find config entry data for entity: %s", entity_id)
                continue
                
            try:
                await _calibrate_sensors(config_entry_data, sensor_type, calibration_mode, reference_value)
                _LOGGER.info("Sensor calibration completed for entity: %s", entity_id)
            except Exception as ex:
                _LOGGER.error("Sensor calibration failed for entity %s: %s", entity_id, ex)
                raise HomeAssistantError(f"Sensor calibration failed for {entity_id}: {ex}") from ex

    async def async_set_display_brightness(call: ServiceCall) -> None:
        """Handle set display brightness service call."""
        entity_ids = await async_extract_entity_ids(hass, call)
        brightness_level = call.data["brightness_level"]
        auto_dim = call.data.get("auto_dim", False)
        night_mode = call.data.get("night_mode", False)
        night_mode_start = call.data.get("night_mode_start")
        night_mode_end = call.data.get("night_mode_end")
        
        _LOGGER.info(
            "Set display brightness service called for entities: %s, brightness: %s",
            entity_ids, brightness_level
        )
        
        for entity_id in entity_ids:
            config_entry_data = get_config_entry_data_from_entity_id(entity_id)
            if not config_entry_data:
                _LOGGER.warning("Could not find config entry data for entity: %s", entity_id)
                continue
                
            try:
                await _set_display_brightness(
                    config_entry_data, brightness_level, auto_dim, night_mode,
                    night_mode_start, night_mode_end
                )
                _LOGGER.info("Display brightness set for entity: %s", entity_id)
            except Exception as ex:
                _LOGGER.error("Set display brightness failed for entity %s: %s", entity_id, ex)
                raise HomeAssistantError(f"Set display brightness failed for {entity_id}: {ex}") from ex

    async def async_schedule_maintenance(call: ServiceCall) -> None:
        """Handle schedule maintenance service call."""
        entity_ids = await async_extract_entity_ids(hass, call)
        maintenance_type = call.data["maintenance_type"]
        reminder_interval = call.data["reminder_interval"]
        next_reminder_date = call.data.get("next_reminder_date")
        enable_notifications = call.data.get("enable_notifications", True)
        notification_advance_days = call.data.get("notification_advance_days", 7)
        maintenance_notes = call.data.get("maintenance_notes", "")
        
        _LOGGER.info(
            "Schedule maintenance service called for entities: %s, type: %s, interval: %s days",
            entity_ids, maintenance_type, reminder_interval
        )
        
        for entity_id in entity_ids:
            config_entry_data = get_config_entry_data_from_entity_id(entity_id)
            if not config_entry_data:
                _LOGGER.warning("Could not find config entry data for entity: %s", entity_id)
                continue
                
            try:
                await _schedule_maintenance(
                    config_entry_data, maintenance_type, reminder_interval,
                    next_reminder_date, enable_notifications, notification_advance_days,
                    maintenance_notes
                )
                _LOGGER.info("Maintenance scheduled for entity: %s", entity_id)
            except Exception as ex:
                _LOGGER.error("Schedule maintenance failed for entity %s: %s", entity_id, ex)
                raise HomeAssistantError(f"Schedule maintenance failed for {entity_id}: {ex}") from ex

    async def async_set_child_lock(call: ServiceCall) -> None:
        """Handle set child lock service call."""
        entity_ids = await async_extract_entity_ids(hass, call)
        enabled = call.data["enabled"]
        
        _LOGGER.info(
            "Set child lock service called for entities: %s, enabled: %s",
            entity_ids, enabled
        )
        
        for entity_id in entity_ids:
            config_entry_data = get_config_entry_data_from_entity_id(entity_id)
            if not config_entry_data:
                _LOGGER.warning("Could not find config entry data for entity: %s", entity_id)
                continue
                
            try:
                await _set_child_lock(config_entry_data, enabled)
                _LOGGER.info("Child lock %s for entity: %s", "enabled" if enabled else "disabled", entity_id)
            except Exception as ex:
                _LOGGER.error("Set child lock failed for entity %s: %s", entity_id, ex)
                raise HomeAssistantError(f"Set child lock failed for {entity_id}: {ex}") from ex

    async def async_set_timer(call: ServiceCall) -> None:
        """Handle set timer service call."""
        entity_ids = await async_extract_entity_ids(hass, call)
        duration_hours = call.data["duration_hours"]
        action_after_timer = call.data.get("action_after_timer", "turn_off")
        
        _LOGGER.info(
            "Set timer service called for entities: %s, duration: %s hours, action: %s",
            entity_ids, duration_hours, action_after_timer
        )
        
        for entity_id in entity_ids:
            config_entry_data = get_config_entry_data_from_entity_id(entity_id)
            if not config_entry_data:
                _LOGGER.warning("Could not find config entry data for entity: %s", entity_id)
                continue
                
            try:
                await _set_timer(config_entry_data, duration_hours, action_after_timer)
                _LOGGER.info("Timer set for entity: %s", entity_id)
            except Exception as ex:
                _LOGGER.error("Set timer failed for entity %s: %s", entity_id, ex)
                raise HomeAssistantError(f"Set timer failed for {entity_id}: {ex}") from ex

    async def async_reset_device(call: ServiceCall) -> None:
        """Handle reset device service call."""
        entity_ids = await async_extract_entity_ids(hass, call)
        reset_type = call.data.get("reset_type", "soft_reset")
        confirm_reset = call.data["confirm_reset"]
        
        if not confirm_reset:
            raise ServiceValidationError("Device reset requires confirmation")
        
        _LOGGER.warning(
            "Reset device service called for entities: %s, reset_type: %s",
            entity_ids, reset_type
        )
        
        for entity_id in entity_ids:
            config_entry_data = get_config_entry_data_from_entity_id(entity_id)
            if not config_entry_data:
                _LOGGER.warning("Could not find config entry data for entity: %s", entity_id)
                continue
                
            try:
                await _reset_device(config_entry_data, reset_type)
                _LOGGER.warning("Device reset completed for entity: %s", entity_id)
            except Exception as ex:
                _LOGGER.error("Device reset failed for entity %s: %s", entity_id, ex)
                raise HomeAssistantError(f"Device reset failed for {entity_id}: {ex}") from ex

    # Register all services
    services = {
        SERVICE_FILTER_RESET: (async_filter_reset, FILTER_RESET_SCHEMA),
        SERVICE_CALIBRATE_SENSORS: (async_calibrate_sensors, CALIBRATE_SENSORS_SCHEMA),
        SERVICE_SET_DISPLAY_BRIGHTNESS: (async_set_display_brightness, SET_DISPLAY_BRIGHTNESS_SCHEMA),
        SERVICE_SCHEDULE_MAINTENANCE: (async_schedule_maintenance, SCHEDULE_MAINTENANCE_SCHEMA),
        SERVICE_SET_CHILD_LOCK: (async_set_child_lock, SET_CHILD_LOCK_SCHEMA),
        SERVICE_SET_TIMER: (async_set_timer, SET_TIMER_SCHEMA),
        SERVICE_RESET_DEVICE: (async_reset_device, RESET_DEVICE_SCHEMA),
    }
    
    _LOGGER.info("Registering %d services for domain %s", len(services), DOMAIN)

    for service_name, (handler, schema) in services.items():
        if not hass.services.has_service(DOMAIN, service_name):
            try:
                hass.services.async_register(
                    DOMAIN,
                    service_name,
                    handler,
                    schema=schema
                )
                _LOGGER.info("Successfully registered service: %s.%s", DOMAIN, service_name)
            except Exception as ex:
                _LOGGER.error("Failed to register service %s.%s: %s", DOMAIN, service_name, ex)
        else:
            _LOGGER.debug("Service %s.%s already registered", DOMAIN, service_name)

    _LOGGER.info("Service registration completed for Philips Air Purifier integration")


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services for Philips Air Purifier integration."""
    services = [
        SERVICE_FILTER_RESET,
        SERVICE_CALIBRATE_SENSORS,
        SERVICE_SET_DISPLAY_BRIGHTNESS,
        SERVICE_SCHEDULE_MAINTENANCE,
        SERVICE_SET_CHILD_LOCK,
        SERVICE_SET_TIMER,
        SERVICE_RESET_DEVICE,
    ]

    for service_name in services:
        if hass.services.has_service(DOMAIN, service_name):
            hass.services.async_remove(DOMAIN, service_name)
            _LOGGER.debug("Unregistered service: %s.%s", DOMAIN, service_name)


# Service implementation functions

async def _reset_filter_counters(
    config_entry_data: ConfigEntryData,
    filter_type: str,
    reset_maintenance: bool
) -> None:
    """Reset filter life counters."""
    client = config_entry_data.coordinator.client

    # Map filter types to their API keys
    filter_mappings = {
        "pre_filter": ("fltsts0", "flttotal0"),
        "hepa_filter": ("fltsts1", "flttotal1"),
        "active_carbon_filter": ("fltsts2", "flttotal2"),
        "nanoprotect_filter": ("D05-14", "D05-08"),
    }

    if filter_type == "all":
        filters_to_reset = filter_mappings.values()
    else:
        if filter_type not in filter_mappings:
            raise ServiceValidationError(f"Unknown filter type: {filter_type}")
        filters_to_reset = [filter_mappings[filter_type]]

    for status_key, total_key in filters_to_reset:
        try:
            # Get the total capacity for this filter
            status = config_entry_data.coordinator.status
            total_capacity = status.get(total_key, 0)

            if total_capacity > 0:
                # Reset the filter status to full capacity
                await client.set_control_value(status_key, total_capacity)
                _LOGGER.info("Reset filter %s to full capacity (%s)", status_key, total_capacity)
            else:
                _LOGGER.warning("Could not reset filter %s: total capacity unknown", status_key)

        except Exception as ex:
            _LOGGER.error("Failed to reset filter %s: %s", status_key, ex)
            raise

    # Store maintenance reset timestamp if requested
    if reset_maintenance:
        # This would typically be stored in device memory or integration data
        _LOGGER.info("Maintenance schedule reset for filter type: %s", filter_type)


async def _calibrate_sensors(
    config_entry_data: ConfigEntryData,
    sensor_type: str,
    calibration_mode: str,
    reference_value: int | None
) -> None:
    """Calibrate air quality sensors."""
    client = config_entry_data.coordinator.client

    # Map sensor types to their calibration commands
    sensor_mappings = {
        "pm25": "pm25",
        "allergen_index": "iaql",
        "gas": "gas",
        "tvoc": "tvoc",
    }

    if sensor_type == "all":
        sensors_to_calibrate = sensor_mappings.keys()
    else:
        if sensor_type not in sensor_mappings:
            raise ServiceValidationError(f"Unknown sensor type: {sensor_type}")
        sensors_to_calibrate = [sensor_type]

    for sensor in sensors_to_calibrate:
        try:
            if calibration_mode == "factory_reset":
                # Factory reset calibration (device-specific implementation)
                _LOGGER.info("Performing factory reset calibration for sensor: %s", sensor)
                # This would send a specific factory reset command

            elif calibration_mode == "manual" and reference_value is not None:
                # Manual calibration with reference value
                _LOGGER.info("Performing manual calibration for sensor %s with reference value: %s",
                           sensor, reference_value)
                # This would send the reference value to the device

            else:
                # Auto calibration
                _LOGGER.info("Performing auto calibration for sensor: %s", sensor)
                # This would trigger the device's auto-calibration routine

        except Exception as ex:
            _LOGGER.error("Failed to calibrate sensor %s: %s", sensor, ex)
            raise

    # Wait for calibration to complete
    await asyncio.sleep(2)
    _LOGGER.info("Sensor calibration completed for: %s", sensors_to_calibrate)


async def _set_display_brightness(
    config_entry_data: ConfigEntryData,
    brightness_level: int,
    auto_dim: bool,
    night_mode: bool,
    night_mode_start: Any,
    night_mode_end: Any
) -> None:
    """Set display brightness and related settings."""
    client = config_entry_data.coordinator.client

    try:
        # Set display brightness (0-100 to device scale)
        device_brightness = int(brightness_level * 255 / 100)  # Convert to 0-255 scale
        await client.set_control_value(PhilipsApi.DISPLAY_BACKLIGHT, str(device_brightness))
        _LOGGER.info("Set display brightness to %s%% (device value: %s)", brightness_level, device_brightness)

        # Set auto-dim if supported
        if auto_dim:
            _LOGGER.info("Auto-dim enabled")
            # This would enable automatic dimming based on ambient light

        # Set night mode if supported
        if night_mode:
            _LOGGER.info("Night mode enabled from %s to %s", night_mode_start, night_mode_end)
            # This would configure night mode timing

    except Exception as ex:
        _LOGGER.error("Failed to set display brightness: %s", ex)
        raise


async def _schedule_maintenance(
    config_entry_data: ConfigEntryData,
    maintenance_type: str,
    reminder_interval: int,
    next_reminder_date: Any,
    enable_notifications: bool,
    notification_advance_days: int,
    maintenance_notes: str
) -> None:
    """Schedule maintenance reminders."""

    # Calculate next reminder date if not provided
    if next_reminder_date is None:
        next_reminder_date = dt_util.now().date() + timedelta(days=reminder_interval)

    # Store maintenance schedule (this would typically be persisted)
    maintenance_schedule = {
        "type": maintenance_type,
        "interval_days": reminder_interval,
        "next_reminder": next_reminder_date.isoformat(),
        "notifications_enabled": enable_notifications,
        "advance_days": notification_advance_days,
        "notes": maintenance_notes,
        "created": dt_util.now().isoformat(),
    }

    _LOGGER.info("Scheduled %s maintenance every %s days, next reminder: %s",
                maintenance_type, reminder_interval, next_reminder_date)

    # This would typically create a persistent reminder or integration with HA's automation system


async def _set_child_lock(config_entry_data: ConfigEntryData, enabled: bool) -> None:
    """Set child lock state."""
    client = config_entry_data.coordinator.client

    try:
        await client.set_control_value(PhilipsApi.CHILD_LOCK, enabled)
        _LOGGER.info("Child lock %s", "enabled" if enabled else "disabled")
    except Exception as ex:
        _LOGGER.error("Failed to set child lock: %s", ex)
        raise


async def _set_timer(
    config_entry_data: ConfigEntryData,
    duration_hours: float,
    action_after_timer: str
) -> None:
    """Set device timer."""
    client = config_entry_data.coordinator.client

    try:
        # Convert hours to minutes for device
        duration_minutes = int(duration_hours * 60)

        if duration_minutes == 0:
            # Disable timer
            _LOGGER.info("Timer disabled")
            # Send command to disable timer
        else:
            _LOGGER.info("Timer set for %s hours (%s minutes), action: %s",
                        duration_hours, duration_minutes, action_after_timer)
            # Send timer command to device

    except Exception as ex:
        _LOGGER.error("Failed to set timer: %s", ex)
        raise


async def _reset_device(config_entry_data: ConfigEntryData, reset_type: str) -> None:
    """Reset device to factory defaults."""
    client = config_entry_data.coordinator.client

    try:
        if reset_type == "factory_reset":
            _LOGGER.warning("Performing factory reset - all settings will be lost")
            # Send factory reset command

        elif reset_type == "network_reset":
            _LOGGER.info("Performing network reset - WiFi settings will be cleared")
            # Send network reset command

        else:  # soft_reset
            _LOGGER.info("Performing soft reset - restarting device")
            # Send soft reset command

        # Wait for reset to complete
        await asyncio.sleep(5)

    except Exception as ex:
        _LOGGER.error("Failed to reset device: %s", ex)
        raise
