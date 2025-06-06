"""Repairs support for Philips Air Purifier integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from aioairctrl import CoAPClient

from homeassistant.components.repairs import ConfirmRepairFlow, RepairsFlow
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er, issue_registry as ir
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.util.timeout import TimeoutManager

from .config_entry_data import ConfigEntryData
from .const import CONF_DEVICE_ID, CONF_MODEL, CONF_STATUS, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, str | int | float | None] | None,
) -> RepairsFlow:
    """Create flow to fix an issue."""
    
    if issue_id == "connectivity_issue":
        return ConnectivityRepairFlow()
    elif issue_id == "entity_registry_cleanup":
        return EntityRegistryCleanupFlow()
    elif issue_id == "filter_replacement_warning":
        return FilterReplacementWarningFlow()
    elif issue_id == "configuration_migration":
        return ConfigurationMigrationFlow()
    elif issue_id == "duplicate_entities":
        return DuplicateEntitiesFlow()
    
    return ConfirmRepairFlow()


class ConnectivityRepairFlow(RepairsFlow):
    """Handler for connectivity issues."""

    async def async_step_init(
        self, user_input: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Handle the initial step."""
        
        if user_input is not None:
            # Attempt to fix connectivity
            return await self.async_step_fix_connectivity()
        
        return self.async_show_form(
            step_id="init",
            description_placeholders={
                "issue_description": "The air purifier device is not responding to network requests. This may be due to network connectivity issues, device power state, or IP address changes."
            },
        )

    async def async_step_fix_connectivity(self) -> dict[str, Any]:
        """Attempt to fix connectivity issues."""
        
        try:
            # Get the config entry for this repair
            config_entries = self.hass.config_entries.async_entries(DOMAIN)
            if not config_entries:
                return self.async_create_entry(
                    title="Connectivity Check",
                    data={"result": "no_config_entries_found"}
                )
            
            for entry in config_entries:
                host = entry.data.get(CONF_HOST)
                if not host:
                    continue
                
                # Test connectivity
                try:
                    timeout = TimeoutManager()
                    async with timeout.async_timeout(10):
                        client = await CoAPClient.create(host)
                        await client.get_status()
                        await client.shutdown()
                    
                    # If we get here, connectivity is working
                    return self.async_create_entry(
                        title="Connectivity Restored",
                        data={"result": "connectivity_restored", "host": host}
                    )
                    
                except Exception as ex:
                    _LOGGER.debug("Connectivity test failed for %s: %s", host, ex)
                    continue
            
            return self.async_create_entry(
                title="Connectivity Issue Persists",
                data={"result": "connectivity_failed"}
            )
            
        except Exception as ex:
            _LOGGER.error("Error during connectivity repair: %s", ex)
            return self.async_create_entry(
                title="Repair Failed",
                data={"result": "repair_error", "error": str(ex)}
            )


class EntityRegistryCleanupFlow(RepairsFlow):
    """Handler for entity registry cleanup."""

    async def async_step_init(
        self, user_input: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Handle the initial step."""
        
        if user_input is not None:
            return await self.async_step_cleanup_entities()
        
        return self.async_show_form(
            step_id="init",
            description_placeholders={
                "issue_description": "Orphaned or duplicate entities have been detected in the entity registry. This can happen after device reconfigurations or integration updates."
            },
        )

    async def async_step_cleanup_entities(self) -> dict[str, Any]:
        """Clean up entity registry."""
        
        try:
            entity_registry = er.async_get(self.hass)
            device_registry = dr.async_get(self.hass)
            
            cleaned_entities = []
            
            # Find entities for this integration
            for entry in self.hass.config_entries.async_entries(DOMAIN):
                entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
                
                for entity in entities:
                    # Check if entity's device still exists
                    if entity.device_id:
                        device = device_registry.async_get(entity.device_id)
                        if not device:
                            # Orphaned entity - device no longer exists
                            entity_registry.async_remove(entity.entity_id)
                            cleaned_entities.append(entity.entity_id)
                            continue
                    
                    # Check for duplicate entities (same unique_id)
                    if entity.unique_id:
                        duplicates = [
                            e for e in entities 
                            if e.unique_id == entity.unique_id and e.entity_id != entity.entity_id
                        ]
                        if duplicates:
                            # Remove duplicates, keeping the first one
                            for duplicate in duplicates:
                                entity_registry.async_remove(duplicate.entity_id)
                                cleaned_entities.append(duplicate.entity_id)
            
            return self.async_create_entry(
                title="Entity Cleanup Complete",
                data={"result": "cleanup_complete", "cleaned_entities": cleaned_entities}
            )
            
        except Exception as ex:
            _LOGGER.error("Error during entity cleanup: %s", ex)
            return self.async_create_entry(
                title="Cleanup Failed",
                data={"result": "cleanup_error", "error": str(ex)}
            )


class FilterReplacementWarningFlow(RepairsFlow):
    """Handler for filter replacement warnings."""

    async def async_step_init(
        self, user_input: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Handle the initial step."""
        
        if user_input is not None:
            return await self.async_step_acknowledge_warning()
        
        return self.async_show_form(
            step_id="init",
            description_placeholders={
                "issue_description": "One or more filters in your air purifier need attention. Check the filter status sensors for replacement or cleaning requirements."
            },
        )

    async def async_step_acknowledge_warning(self) -> dict[str, Any]:
        """Acknowledge the filter warning."""
        
        return self.async_create_entry(
            title="Filter Warning Acknowledged",
            data={"result": "warning_acknowledged"}
        )


class ConfigurationMigrationFlow(RepairsFlow):
    """Handler for configuration migration issues."""

    async def async_step_init(
        self, user_input: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Handle the initial step."""
        
        if user_input is not None:
            return await self.async_step_migrate_config()
        
        return self.async_show_form(
            step_id="init",
            description_placeholders={
                "issue_description": "Your integration configuration needs to be updated to support new features. This migration will update your configuration automatically."
            },
        )

    async def async_step_migrate_config(self) -> dict[str, Any]:
        """Migrate configuration."""
        
        try:
            migrated_entries = []
            
            for entry in self.hass.config_entries.async_entries(DOMAIN):
                # Check if status data is missing (old configuration)
                if CONF_STATUS not in entry.data:
                    try:
                        # Try to fetch status data
                        host = entry.data.get(CONF_HOST)
                        if host:
                            timeout = TimeoutManager()
                            async with timeout.async_timeout(30):
                                client = await CoAPClient.create(host)
                                status, _ = await client.get_status()
                                await client.shutdown()
                            
                            # Update entry with status data
                            new_data = {**entry.data}
                            new_data[CONF_STATUS] = status
                            self.hass.config_entries.async_update_entry(entry, data=new_data)
                            migrated_entries.append(entry.entry_id)
                            
                    except Exception as ex:
                        _LOGGER.warning("Failed to migrate config for %s: %s", entry.title, ex)
            
            return self.async_create_entry(
                title="Configuration Migration Complete",
                data={"result": "migration_complete", "migrated_entries": migrated_entries}
            )
            
        except Exception as ex:
            _LOGGER.error("Error during configuration migration: %s", ex)
            return self.async_create_entry(
                title="Migration Failed",
                data={"result": "migration_error", "error": str(ex)}
            )


class DuplicateEntitiesFlow(RepairsFlow):
    """Handler for duplicate entity issues."""

    async def async_step_init(
        self, user_input: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Handle the initial step."""
        
        if user_input is not None:
            return await self.async_step_remove_duplicates()
        
        return self.async_show_form(
            step_id="init",
            description_placeholders={
                "issue_description": "Duplicate entities have been detected. This typically happens when entity unique IDs conflict. The repair will remove duplicate entities automatically."
            },
        )

    async def async_step_remove_duplicates(self) -> dict[str, Any]:
        """Remove duplicate entities."""
        
        try:
            entity_registry = er.async_get(self.hass)
            removed_entities = []
            
            for entry in self.hass.config_entries.async_entries(DOMAIN):
                entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
                
                # Group entities by unique_id
                unique_id_groups = {}
                for entity in entities:
                    if entity.unique_id:
                        if entity.unique_id not in unique_id_groups:
                            unique_id_groups[entity.unique_id] = []
                        unique_id_groups[entity.unique_id].append(entity)
                
                # Remove duplicates
                for unique_id, entity_group in unique_id_groups.items():
                    if len(entity_group) > 1:
                        # Keep the first entity, remove the rest
                        for entity in entity_group[1:]:
                            entity_registry.async_remove(entity.entity_id)
                            removed_entities.append(entity.entity_id)
            
            return self.async_create_entry(
                title="Duplicate Entities Removed",
                data={"result": "duplicates_removed", "removed_entities": removed_entities}
            )
            
        except Exception as ex:
            _LOGGER.error("Error during duplicate removal: %s", ex)
            return self.async_create_entry(
                title="Duplicate Removal Failed",
                data={"result": "removal_error", "error": str(ex)}
            )


@callback
def async_create_issue(
    hass: HomeAssistant,
    issue_id: str,
    translation_key: str,
    severity: ir.IssueSeverity = ir.IssueSeverity.WARNING,
    **kwargs: Any,
) -> None:
    """Create a repair issue."""
    
    ir.async_create_issue(
        hass,
        DOMAIN,
        issue_id,
        is_fixable=True,
        severity=severity,
        translation_key=translation_key,
        **kwargs,
    )


@callback
def async_delete_issue(hass: HomeAssistant, issue_id: str) -> None:
    """Delete a repair issue."""
    
    ir.async_delete_issue(hass, DOMAIN, issue_id)


async def async_check_integration_health(
    hass: HomeAssistant, config_entry_data: ConfigEntryData
) -> None:
    """Check integration health and create repair issues if needed."""
    
    # Check connectivity
    if not config_entry_data.coordinator.client:
        async_create_issue(
            hass,
            "connectivity_issue",
            "connectivity_issue",
            severity=ir.IssueSeverity.ERROR,
        )
    else:
        async_delete_issue(hass, "connectivity_issue")
    
    # Check for filter replacement needs
    status = config_entry_data.latest_status or {}
    filter_warning_needed = False
    
    # Check various filter types
    filter_keys = [
        ("fltsts0", "flttotal0"),  # Pre-filter
        ("fltsts1", "flttotal1"),  # HEPA filter
        ("fltsts2", "flttotal2"),  # Active carbon filter
        ("D05-14", "D05-08"),     # NanoProtect filter
    ]
    
    for status_key, total_key in filter_keys:
        if status_key in status and total_key in status:
            remaining = status[status_key]
            total = status[total_key]
            if total > 0:
                percentage = (remaining / total) * 100
                if percentage <= 15:  # Less than 15% remaining
                    filter_warning_needed = True
                    break
    
    if filter_warning_needed:
        async_create_issue(
            hass,
            "filter_replacement_warning",
            "filter_replacement_warning",
            severity=ir.IssueSeverity.WARNING,
        )
    else:
        async_delete_issue(hass, "filter_replacement_warning")
    
    # Check for entity registry issues
    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)
    
    orphaned_entities = []
    duplicate_entities = []
    
    for entry in hass.config_entries.async_entries(DOMAIN):
        entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
        
        # Check for orphaned entities
        for entity in entities:
            if entity.device_id:
                device = device_registry.async_get(entity.device_id)
                if not device:
                    orphaned_entities.append(entity.entity_id)
        
        # Check for duplicates
        unique_ids = {}
        for entity in entities:
            if entity.unique_id:
                if entity.unique_id in unique_ids:
                    duplicate_entities.append(entity.entity_id)
                else:
                    unique_ids[entity.unique_id] = entity.entity_id
    
    if orphaned_entities or duplicate_entities:
        async_create_issue(
            hass,
            "entity_registry_cleanup",
            "entity_registry_cleanup",
            severity=ir.IssueSeverity.WARNING,
        )
    else:
        async_delete_issue(hass, "entity_registry_cleanup")
