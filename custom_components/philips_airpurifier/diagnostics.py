"""Diagnostics support for Philips Air Purifier integration."""

from __future__ import annotations

import asyncio
import logging
import sys
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.util import dt as dt_util

from .config_entry_data import ConfigEntryData
from .const import CONF_DEVICE_ID, CONF_MODEL, CONF_STATUS, DOMAIN

_LOGGER = logging.getLogger(__name__)

# Data to redact for privacy
TO_REDACT = {
    "device_id",
    "DeviceId", 
    "device_serial",
    "serial_number",
    "mac",
    "ip_address",
    "host",
    "ssid",
    "wifi_ssid",
    "network_name",
    "bssid",
    "wifi_password",
    "password",
    "token",
    "api_key",
    "unique_id",
    "id",
    "entry_id",
    "config_entry_id",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    
    config_entry_data: ConfigEntryData = hass.data[DOMAIN][entry.entry_id]
    
    # Get device and entity registries
    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)
    
    # Find the device for this integration
    device_entry = None
    for device in device_registry.devices.values():
        if entry.entry_id in device.config_entries:
            device_entry = device
            break
    
    # Collect basic system information
    diagnostics_data = {
        "system_info": await _get_system_info(hass, entry),
        "integration_info": await _get_integration_info(hass, entry, config_entry_data),
        "device_info": await _get_device_info(hass, entry, config_entry_data, device_entry),
        "connectivity_info": await _get_connectivity_info(hass, config_entry_data),
        "performance_metrics": await _get_performance_metrics(hass, config_entry_data),
        "entity_info": await _get_entity_info(hass, entry, entity_registry),
        "configuration_data": await _get_configuration_data(hass, entry),
        "error_tracking": await _get_error_tracking(hass, config_entry_data),
        "device_status": await _get_device_status(hass, config_entry_data),
    }
    
    # Redact sensitive information
    return async_redact_data(diagnostics_data, TO_REDACT)


async def _get_system_info(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    """Get system information."""
    return {
        "home_assistant_version": hass.config.version,
        "python_version": sys.version,
        "integration_version": "0.26.0",  # From manifest.json
        "domain": DOMAIN,
        "entry_id": entry.entry_id,
        "entry_title": entry.title,
        "entry_version": entry.version,
        "timestamp": dt_util.utcnow().isoformat(),
    }


async def _get_integration_info(
    hass: HomeAssistant, entry: ConfigEntry, config_entry_data: ConfigEntryData
) -> dict[str, Any]:
    """Get integration-specific information."""
    
    coordinator = config_entry_data.coordinator
    device_info = config_entry_data.device_information
    
    return {
        "integration_domain": DOMAIN,
        "integration_name": "Philips AirPurifier",
        "device_model": device_info.model,
        "device_name": device_info.name,
        "device_host": device_info.host,
        "coordinator_status": {
            "is_connected": coordinator.client is not None,
            "timeout_setting": getattr(coordinator, '_timeout', 'unknown'),
            "has_listeners": len(getattr(coordinator, '_listeners', [])) > 0,
            "task_running": coordinator._task is not None and not coordinator._task.done() if coordinator._task else False,
        },
        "client_info": {
            "client_type": type(coordinator.client).__name__ if coordinator.client else None,
            "client_available": coordinator.client is not None,
        }
    }


async def _get_device_info(
    hass: HomeAssistant, 
    entry: ConfigEntry, 
    config_entry_data: ConfigEntryData,
    device_entry: DeviceEntry | None
) -> dict[str, Any]:
    """Get device information."""
    
    device_info = config_entry_data.device_information
    status = config_entry_data.latest_status or {}
    
    device_data = {
        "device_model": device_info.model,
        "device_name": device_info.name,
        "device_host": device_info.host,
        "device_mac": device_info.mac,
        "device_id_from_config": device_info.device_id,
    }
    
    # Add device registry information if available
    if device_entry:
        device_data.update({
            "device_registry_id": device_entry.id,
            "device_manufacturer": device_entry.manufacturer,
            "device_model_registry": device_entry.model,
            "device_name_registry": device_entry.name,
            "device_sw_version": device_entry.sw_version,
            "device_hw_version": device_entry.hw_version,
            "device_connections": device_entry.connections,
            "device_identifiers": device_entry.identifiers,
            "device_config_entries": list(device_entry.config_entries),
        })
    
    # Add device status information
    if status:
        device_data.update({
            "device_status_keys": list(status.keys()),
            "device_status_count": len(status),
            "has_error_code": "err" in status,
            "error_code_value": status.get("err", "N/A"),
            "has_wifi_version": "WifiVersion" in status,
            "wifi_version": status.get("WifiVersion", "N/A"),
            "has_software_version": "swversion" in status,
            "software_version": status.get("swversion", "N/A"),
            "has_model_id": "modelid" in status,
            "model_id": status.get("modelid", "N/A"),
            "has_product_id": "ProductId" in status,
            "product_id": status.get("ProductId", "N/A"),
        })
    
    return device_data


async def _get_connectivity_info(
    hass: HomeAssistant, config_entry_data: ConfigEntryData
) -> dict[str, Any]:
    """Get connectivity information."""
    
    coordinator = config_entry_data.coordinator
    device_info = config_entry_data.device_information
    status = config_entry_data.latest_status or {}
    
    connectivity_data = {
        "host": device_info.host,
        "connection_status": "connected" if coordinator.client else "disconnected",
        "coordinator_available": coordinator is not None,
        "has_status_data": status is not None and len(status) > 0,
        "status_data_age": "unknown",  # Could be enhanced with timestamp tracking
    }
    
    # Add signal strength if available
    if "rssi" in status:
        rssi_value = status["rssi"]
        connectivity_data.update({
            "signal_strength_dbm": rssi_value,
            "signal_quality": _get_signal_quality(rssi_value),
        })
    
    # Test connectivity
    try:
        if coordinator.client:
            connectivity_data["client_status"] = "available"
            # Could add ping test here if needed
        else:
            connectivity_data["client_status"] = "unavailable"
    except Exception as ex:
        connectivity_data["client_status"] = f"error: {ex}"
    
    return connectivity_data


def _get_signal_quality(rssi: int) -> str:
    """Get signal quality description from RSSI value."""
    if rssi >= -50:
        return "excellent"
    elif rssi >= -60:
        return "good"
    elif rssi >= -70:
        return "fair"
    else:
        return "poor"


async def _get_performance_metrics(
    hass: HomeAssistant, config_entry_data: ConfigEntryData
) -> dict[str, Any]:
    """Get performance metrics."""
    
    coordinator = config_entry_data.coordinator
    
    return {
        "coordinator_listeners": len(getattr(coordinator, '_listeners', [])),
        "update_method": "push" if coordinator._task else "unknown",
        "reconnect_task_active": coordinator._reconnect_task is not None and not coordinator._reconnect_task.done() if coordinator._reconnect_task else False,
        "timer_disconnected_active": getattr(coordinator._timer_disconnected, 'is_running', 'unknown') if hasattr(coordinator, '_timer_disconnected') else False,
        "memory_usage": "not_tracked",  # Could be enhanced with memory tracking
        "api_call_count": "not_tracked",  # Could be enhanced with call counting
        "cache_hit_rate": "not_applicable",  # This integration uses push updates
    }


async def _get_entity_info(
    hass: HomeAssistant, entry: ConfigEntry, entity_registry: er.EntityRegistry
) -> dict[str, Any]:
    """Get entity information."""
    
    entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
    
    entity_counts = {}
    entity_details = []
    
    for entity in entities:
        platform = entity.platform
        entity_counts[platform] = entity_counts.get(platform, 0) + 1
        
        entity_details.append({
            "entity_id": entity.entity_id,
            "platform": platform,
            "device_class": entity.device_class,
            "entity_category": entity.entity_category,
            "disabled": entity.disabled_by is not None,
            "hidden": entity.hidden_by is not None,
            "has_entity_name": entity.has_entity_name,
            "translation_key": entity.translation_key,
        })
    
    return {
        "total_entities": len(entities),
        "entity_counts_by_platform": entity_counts,
        "entity_details": entity_details,
    }


async def _get_configuration_data(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Get configuration data."""
    
    return {
        "config_entry_data": {
            "host": entry.data.get(CONF_HOST),
            "model": entry.data.get(CONF_MODEL),
            "name": entry.data.get(CONF_NAME),
            "has_device_id": CONF_DEVICE_ID in entry.data,
            "has_status": CONF_STATUS in entry.data,
            "status_keys_count": len(entry.data.get(CONF_STATUS, {})),
        },
        "config_entry_options": dict(entry.options),
        "config_entry_source": entry.source,
        "config_entry_state": entry.state.value,
    }


async def _get_error_tracking(
    hass: HomeAssistant, config_entry_data: ConfigEntryData
) -> dict[str, Any]:
    """Get error tracking information."""
    
    status = config_entry_data.latest_status or {}
    
    error_data = {
        "device_error_code": status.get("err", 0),
        "device_error_description": "Normal Operation" if status.get("err", 0) == 0 else f"Error Code: {status.get('err', 'unknown')}",
        "recent_exceptions": "not_tracked",  # Could be enhanced with exception tracking
        "connection_failures": "not_tracked",  # Could be enhanced with failure tracking
        "api_timeouts": "not_tracked",  # Could be enhanced with timeout tracking
    }
    
    return error_data


async def _get_device_status(
    hass: HomeAssistant, config_entry_data: ConfigEntryData
) -> dict[str, Any]:
    """Get current device status."""
    
    status = config_entry_data.latest_status or {}
    
    if not status:
        return {"status": "no_data_available"}
    
    # Extract key operational data
    device_status = {
        "power_status": "on" if status.get("pwr") == "1" else "off",
        "mode": status.get("mode", "unknown"),
        "fan_speed": status.get("om", "unknown"),
        "air_quality": {
            "pm25": status.get("pm25", "unknown"),
            "indoor_allergen_index": status.get("iaql", "unknown"),
            "gas_level": status.get("gas", "unknown") if "gas" in status else "not_available",
        },
        "environmental": {
            "temperature": status.get("temp", "unknown"),
            "humidity": status.get("rh", "unknown"),
        },
        "filters": {},
        "settings": {
            "child_lock": "on" if status.get("cl") == True else "off",
            "display_backlight": status.get("uil", "unknown"),
            "preferred_index": status.get("ddp", "unknown"),
        },
        "device_info": {
            "runtime": status.get("Runtime", "unknown"),
            "wifi_version": status.get("WifiVersion", "unknown"),
            "software_version": status.get("swversion", "unknown"),
            "model_id": status.get("modelid", "unknown"),
            "product_id": status.get("ProductId", "unknown"),
        }
    }
    
    # Extract filter information
    filter_keys = [key for key in status.keys() if key.startswith(('flt', 'wick', 'D05'))]
    for filter_key in filter_keys:
        device_status["filters"][filter_key] = status[filter_key]
    
    return device_status
