"""Philips Air Purifier & Humidifier Selects."""

from __future__ import annotations

from collections.abc import Callable
import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_DEVICE_CLASS, CONF_ENTITY_CATEGORY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

from .config_entry_data import ConfigEntryData
from .const import DOMAIN, OPTIONS, SELECT_TYPES, FanAttributes
from .philips import PhilipsEntity, model_to_class

_LOGGER = logging.getLogger(__name__)


async def _remove_duplicate_preferred_index_entity(
    hass: HomeAssistant, config_entry_data: ConfigEntryData
) -> None:
    """Remove duplicate preferred index entity if it exists."""
    try:
        entity_registry = async_get_entity_registry(hass)
        device_id = config_entry_data.device_information.device_id
        model = config_entry_data.device_information.model

        # Look for the basic preferred_index entity (without gas support)
        device_name = config_entry_data.device_information.name.lower().replace(' ', '_')
        duplicate_entity_id = f"select.{device_name}_preferred_index"

        # Check if the duplicate entity exists in the registry
        entity_entry = entity_registry.async_get(duplicate_entity_id)
        if entity_entry:
            # Check if this is the basic version by looking at unique_id pattern
            # The basic version should have "d0312a#1" while gas version has "d0312a#2"
            if entity_entry.unique_id and "#1" in entity_entry.unique_id:
                _LOGGER.info(
                    "Removing duplicate preferred index entity: %s (keeping gas-enabled version)",
                    duplicate_entity_id
                )
                entity_registry.async_remove(duplicate_entity_id)
                return

        # Alternative approach: look for any entity with the basic preferred index unique_id pattern
        for entity_id, entry in entity_registry.entities.items():
            if (entry.platform == "philips_airpurifier_coap" and
                entry.unique_id and
                f"{model}-{device_id}-d0312a#1".lower() in entry.unique_id.lower()):
                _LOGGER.info(
                    "Removing duplicate preferred index entity by unique_id: %s",
                    entity_id
                )
                entity_registry.async_remove(entity_id)
                break

    except Exception as e:
        _LOGGER.warning("Could not remove duplicate entity: %s", e)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[list[Entity], bool], None],
) -> None:
    """Set up the select platform."""

    config_entry_data: ConfigEntryData = hass.data[DOMAIN][entry.entry_id]

    model = config_entry_data.device_information.model

    # Remove duplicate preferred index entity for AC4220 models
    if model == "AC4220/12":
        await _remove_duplicate_preferred_index_entity(hass, config_entry_data)

    model_class = model_to_class.get(model)
    if model_class:
        available_selects = []

        for cls in reversed(model_class.__mro__):
            cls_available_selects = getattr(cls, "AVAILABLE_SELECTS", [])
            available_selects.extend(cls_available_selects)

        # Remove duplicates while preserving order, prioritizing child class definitions
        seen = set()
        unique_selects = []
        for select in reversed(available_selects):  # Reverse to prioritize child classes
            if select not in seen:
                seen.add(select)
                unique_selects.append(select)
        available_selects = list(reversed(unique_selects))  # Restore original order

        # Filter out the basic preferred_index for AC4220 to prevent duplicates
        filtered_selects = []
        for select in SELECT_TYPES:
            if select in available_selects:
                # For AC4220, skip the basic preferred_index if gas version is available
                if (model == "AC4220/12" and
                    select == PhilipsApi.NEW2_PREFERRED_INDEX and
                    PhilipsApi.NEW2_GAS_PREFERRED_INDEX in available_selects):
                    continue
                filtered_selects.append(select)

        selects = [
            PhilipsSelect(hass, entry, config_entry_data, select)
            for select in filtered_selects
        ]

        async_add_entities(selects, update_before_add=False)

    else:
        _LOGGER.error("Unsupported model: %s", model)
        return


class PhilipsSelect(PhilipsEntity, SelectEntity):
    """Define a Philips AirPurifier select."""

    _attr_is_on: bool | None = False

    def __init__(
        self,
        hass: HomeAssistant,
        config: ConfigEntry,
        config_entry_data: ConfigEntryData,
        select: str,
    ) -> None:
        """Initialize the select."""

        super().__init__(hass, config, config_entry_data)

        self._model = config_entry_data.device_information.model

        self._description = SELECT_TYPES[select]
        self._attr_device_class = self._description.get(ATTR_DEVICE_CLASS)
        label = FanAttributes.LABEL
        label = label.partition("#")[0]
        self._attr_translation_key = self._description.get(FanAttributes.LABEL)
        self._attr_entity_category = self._description.get(CONF_ENTITY_CATEGORY)

        self._options = self._description.get(OPTIONS)
        self._attr_options = list(self._options.values())

        model = config_entry_data.device_information.model
        device_id = config_entry_data.device_information.device_id
        self._attr_unique_id = f"{model}-{device_id}-{select.lower()}"

        self._attrs: dict[str, Any] = {}
        self.kind = select.partition("#")[0]

    @property
    def current_option(self) -> str:
        """Return the currently selected option."""
        option = self._device_status.get(self.kind)
        current_option = str(self._options.get(option))
        _LOGGER.debug(
            "option: %s, returning as current_option: %s", option, current_option
        )
        return current_option

    async def async_select_option(self, option: str) -> None:
        """Select an option."""
        if option is None or len(option) == 0:
            _LOGGER.error("Cannot set empty option '%s'", option)
            return
        try:
            option_key = next(
                key for key, value in self._options.items() if value == option
            )
            _LOGGER.debug(
                "async_selection_option, kind: %s - option: %s - value: %s",
                self.kind,
                option,
                option_key,
            )
            await self.coordinator.client.set_control_value(self.kind, option_key)
            self._device_status[self.kind] = option_key
            self._handle_coordinator_update()

        except KeyError as e:
            _LOGGER.error("Invalid option key: '%s' with error: %s", option, e)
        except ValueError as e:
            _LOGGER.error("Invalid value for option: '%s' with error: %s", option, e)
