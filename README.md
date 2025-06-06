# Philips Air Purifier Home Assistant Integration

[![HACS Default][hacs_shield]][hacs]
[![GitHub Latest Release][releases_shield]][latest_release]
[![Home Assistant][ha_shield]][ha_link]
[![Documentation][docs_shield]][docs_link]
[![License][license_shield]][license_link]
[![Community Forum][community_forum_shield]][community_forum]
[![GitHub Issues][issues_shield]][issues_link]

[hacs_shield]: https://img.shields.io/badge/HACS-Default-green?style=flat-square
[hacs]: https://hacs.xyz/docs/default_repositories

[releases_shield]: https://img.shields.io/github/release/domalab/ha-philips-airpurifier?style=flat-square&color=blue
[latest_release]: https://github.com/domalab/ha-philips-airpurifier/releases/latest

[ha_shield]: https://img.shields.io/badge/Home%20Assistant-2025.1%2B-blue?style=flat-square
[ha_link]: https://www.home-assistant.io/

[docs_shield]: https://deepwiki.com/badge.svg
[docs_link]: https://deepwiki.com/domalab/ha-philips-airpurifier

[license_shield]: https://img.shields.io/github/license/domalab/ha-philips-airpurifier?style=flat-square&color=orange
[license_link]: https://github.com/domalab/ha-philips-airpurifier/blob/main/custom_components/philips_airpurifier/LICENSE.txt

[community_forum_shield]: https://img.shields.io/badge/Community-Forum-blue?style=flat-square
[community_forum]: https://community.home-assistant.io/t/philips-air-purifier/53030

[issues_shield]: https://img.shields.io/github/issues/domalab/ha-philips-airpurifier?style=flat-square&color=red
[issues_link]: https://github.com/domalab/ha-philips-airpurifier/issues

A comprehensive **Local Push** integration for Philips air purifiers and humidifiers in Home Assistant. This integration provides complete control over your Philips air quality devices using the encrypted CoAP protocol for local communication.

## 📋 Table of Contents

- [Features](#-features)
- [Important Notice](#️-important-notice)
- [Installation](#-installation)
  - [HACS Installation (Recommended)](#hacs-installation-recommended)
  - [Manual Installation](#manual-installation)
- [Configuration](#️-configuration)
- [Supported Devices](#-supported-devices)
- [Available Entities](#-available-entities)
- [Custom Icons](#-custom-icons)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [Credits](#-credits)
- [License](#-license)

## ✨ Features

- **Local Control**: Direct communication with your device without cloud dependency
- **Auto-Discovery**: Automatic detection of compatible devices on your network
- **Comprehensive Entity Support**: Fan, humidifier, sensors, switches, lights, and more
- **Real-time Monitoring**: Air quality sensors, filter status, and device diagnostics
- **Custom Icons**: Beautiful Philips-branded icons for the Home Assistant frontend
- **Multi-language Support**: Available in English, German, Dutch, Bulgarian, Romanian, and Slovak
- **HACS Compatible**: Easy installation and updates through HACS

## ⚠️ Important Notice

**Please read this carefully before installation:**

Due to firmware limitations in Philips devices, this integration may experience stability issues. The connection might work initially but could become unresponsive over time. Common solutions include:

- Power cycling the Philips device
- Restarting Home Assistant
- Both actions combined

This integration includes automatic reconnection attempts, but they may not always succeed. These issues are inherent to the device firmware and cannot be resolved at the integration level.

**Background**: This integration is based on reverse engineering work by [@rgerganov](https://github.com/rgerganov). Read more about the technical details [here](https://xakcop.com/post/ctrl-air-purifier/).

> **Note**: Philips has introduced a cloud-based API that works with Google Home and Alexa, but it's not publicly available for local integrations.


## 🚀 Installation

### HACS Installation (Recommended)

1. **Add Repository**: Click the button below to add this repository to HACS:

   [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=domalab&repository=ha-philips-airpurifier&category=integration)

2. **Install**: Search for "Philips AirPurifier" in HACS and install it
3. **Restart**: Restart Home Assistant
4. **Configure**: Follow the [Configuration](#️-configuration) steps below

### Manual Installation

1. **Download**: Download the latest release from the [releases page](https://github.com/domalab/ha-philips-airpurifier/releases)
2. **Extract**: Extract the `custom_components/philips_airpurifier` folder to your Home Assistant `custom_components` directory
3. **Restart**: Restart Home Assistant
4. **Configure**: Follow the [Configuration](#️-configuration) steps below

## ⚙️ Configuration

### Prerequisites

- Home Assistant 2025.1.0 or newer
- Philips air purifier/humidifier connected to your local network
- Device must support local CoAP communication (see [Important Notice](#️-important-notice))

### Setup Steps

#### Automatic Discovery (Recommended)

The integration automatically discovers compatible devices on your network using:
- MAC address patterns (B0F893*, 047863*, 849DC2*, 80A036*)
- Hostname patterns (mxchip*)

When a device is discovered, Home Assistant will show a notification. Simply follow the setup wizard.

#### Manual Configuration

If automatic discovery doesn't work:

1. **Navigate**: Go to **Settings** → **Devices & Services**
2. **Add Integration**: Click **Add Integration**
3. **Search**: Search for "Philips AirPurifier" and select it
4. **Enter Details**: Provide your device's IP address or hostname
5. **Complete Setup**: The model will be detected automatically

### Important Notes

- **No YAML Configuration**: This integration uses the UI-based config flow only
- **IP Address Changes**: If your device's IP changes, the integration will attempt to auto-update. If this fails, simply reconfigure with the new IP address
- **Model Detection**: Unsupported models will generate a warning in the logs

### Reconfiguration

If your device changes IP addresses:

- **With Auto-discovery**: The integration will automatically detect and update the IP address
- **Manual Setup**: Add the device again with the new IP address - Home Assistant will recognize it's the same device and update the configuration

## 📱 Supported Devices

> **⚠️ Firmware Compatibility Warning**: Some newer firmware versions may disable local CoAP communication. If purchasing a device specifically for Home Assistant integration, ensure you can return it if the integration doesn't work.

### Air Purifiers

| Model Series | Variants | Type |
|--------------|----------|------|
| **AC0850** | 11, 20, 31, 41, 70, 81, 85 | Compact Air Purifiers |
| **AC0950** | 0950, 0951 | Compact Air Purifiers |
| **AC1214** | 1214 | Compact Air Purifiers |
| **AC1715** | 1715 | Compact Air Purifiers |
| **AC2729** | 2729 | Mid-range Air Purifiers |
| **AC2889** | 2889 | Mid-range Air Purifiers |
| **AC2936** | 2936, 2939, 2958, 2959 | Mid-range Air Purifiers |
| **AC3033** | 3033, 3036, 3039 | Advanced Air Purifiers |
| **AC3055** | 3055, 3059 | Advanced Air Purifiers |
| **AC3210** | 3210, 3220, 3221 | Advanced Air Purifiers |
| **AC3259** | 3259 | Advanced Air Purifiers |
| **AC3420** | 3420, 3421 | Advanced Air Purifiers |
| **AC3737** | 3737 | Advanced Air Purifiers |
| **AC3829** | 3829, 3836 | Advanced Air Purifiers |
| **AC3854** | 3854/50, 3854/51 | Advanced Air Purifiers |
| **AC3858** | 3858/50, 3858/51, 3858/83, 3858/86 | Advanced Air Purifiers |
| **AC4220** | 4220, 4221, 4236 | Premium Air Purifiers |
| **AC4550** | 4550, 4558 | Premium Air Purifiers |
| **AC5659** | 5659, 5660 | Premium Air Purifiers |

### Air Purifier & Humidifier Combos

| Model | Type |
|-------|------|
| **AMF765** | 2-in-1 Air Purifier & Humidifier |
| **AMF870** | 2-in-1 Air Purifier & Humidifier |

### Humidifiers

| Model Series | Variants | Type |
|--------------|----------|------|
| **CX3120** | 3120 | Humidifier |
| **CX3550** | 3550 | Humidifier |
| **CX5120** | 5120 | Humidifier |
| **HU1509** | 1509, 1510 | Compact Humidifier |
| **HU5710** | 5710 | Advanced Humidifier |

### Special Variants

Some models include special variants:

- **AWS_Philips_AIR**: Standard air purifier mode
- **AWS_Philips_AIR_Combo**: 2-in-1 air purifier and humidifier mode

## 🔧 Available Entities

This integration provides comprehensive control through various Home Assistant entity types:

### Core Entities

| Entity Type | Description | Features |
|-------------|-------------|----------|
| **Fan** | Main device control | Power, speed control, preset modes |
| **Humidifier** | Humidity control (2-in-1 models) | Target humidity, humidification modes |
| **Climate** | Temperature control (applicable models) | Temperature settings, heating modes |

### Monitoring Entities

| Entity Type | Examples | Purpose |
|-------------|----------|---------|
| **Sensors** | PM2.5, IAI, Temperature, Humidity | Air quality monitoring |
| **Binary Sensors** | Filter replacement, Water refill | Maintenance alerts |

### Control Entities

| Entity Type | Examples | Purpose |
|-------------|----------|---------|
| **Switches** | Child lock, Display light | Device settings |
| **Lights** | Display brightness, Status lights | Visual controls |
| **Select** | Timer settings, Function modes | Advanced options |
| **Number** | Custom values (model-dependent) | Precise control |

### Entity Attributes

The fan entity includes additional attributes with device information:

| Attribute | Description | Example |
|-----------|-------------|---------|
| `name` | Device name | "bedroom" |
| `type` | Configured model | "AC2729" |
| `model_id` | Philips model ID | "AC2729/10" |
| `product_id` | Philips product ID | "85bc26fae62611e8a1e3061302926720" |
| `device_id` | Philips device ID | "3c84c6c8123311ebb1ae8e3584d00715" |
| `software_version` | Device firmware | "0.2.1" |
| `wifi_version` | WiFi module version | "AWS_Philips_AIR@62.1" |
| `error_code` | Philips error code | "49408" |
| `error` | Human-readable error | "no water" |
| `preferred_index` | Air quality index type | "PM2.5", "IAI" |
| `runtime` | Device uptime | "9 days, 10:44:41" |

## 🆘 Troubleshooting

### Debug Logging

To enable detailed logging, add this to your `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.philips_airpurifier_coap: debug
    coap: debug
    aioairctrl: debug
```

Logs will be available in `home-assistant.log`.

### Common Issues

| Problem | Solution |
|---------|----------|
| Device not discovered | Check network connectivity, ensure device supports CoAP |
| Connection drops | Power cycle device, restart Home Assistant |
| Entities unavailable | Check device firmware version, verify local API is enabled |
| Integration not loading | Check Home Assistant logs, verify installation |

### Getting Help for Unsupported Models

If your model isn't supported yet, you can help by providing device data:

#### 1. Prepare Environment

```bash
# Create virtual environment
python -m venv env
source ./env/bin/activate  # On Windows: env\Scripts\activate

# Install required package
python -m pip install aioairctrl
```

#### 2. Collect Device Data

```bash
# Replace $DEVICE_IP with your device's IP address
aioairctrl --host $DEVICE_IP status --json
```

#### 3. Submit Data

1. Test different modes and speeds using the Philips app
2. Collect JSON output for each configuration
3. [Open an issue](https://github.com/domalab/ha-philips-airpurifier/issues) with the collected data

#### 4. Clean Up

```bash
deactivate  # Exit virtual environment
```

## 🎨 Custom Icons

This integration includes beautiful, original Philips icons for the Home Assistant frontend. Icons are accessible with the `pap:` prefix and should appear in the icon picker.

> **Note**: You may need to clear your browser cache after installation to see the icons.

### Available Icons

| Icon | Name | Usage |
|------|------|-------|
| ![power_button](./custom_components/philips_airpurifier/icons/pap/power_button.svg) | `pap:power_button` | Power control |
| ![auto_mode](./custom_components/philips_airpurifier/icons/pap/auto_mode.svg) | `pap:auto_mode` | Auto mode |
| ![sleep_mode](./custom_components/philips_airpurifier/icons/pap/sleep_mode.svg) | `pap:sleep_mode` | Sleep mode |
| ![child_lock_button](./custom_components/philips_airpurifier/icons/pap/child_lock_button.svg) | `pap:child_lock_button` | Child lock |
| ![fan_speed_button](./custom_components/philips_airpurifier/icons/pap/fan_speed_button.svg) | `pap:fan_speed_button` | Fan speed |
| ![humidity_button](./custom_components/philips_airpurifier/icons/pap/humidity_button.svg) | `pap:humidity_button` | Humidity control |
| ![light_dimming_button](./custom_components/philips_airpurifier/icons/pap/light_dimming_button.svg) | `pap:light_dimming_button` | Light dimming |
| ![pm25](./custom_components/philips_airpurifier/icons/pap/pm25.svg) | `pap:pm25` | PM2.5 sensor |
| ![filter_replacement](./custom_components/philips_airpurifier/icons/pap/filter_replacement.svg) | `pap:filter_replacement` | Filter status |
| ![water_refill](./custom_components/philips_airpurifier/icons/pap/water_refill.svg) | `pap:water_refill` | Water level |

<details>
<summary>View All Icons</summary>

| Icon | Name | Icon | Name |
|------|------|------|------|
| ![power_button](./custom_components/philips_airpurifier/icons/pap/power_button.svg) | `pap:power_button` | ![child_lock_button](./custom_components/philips_airpurifier/icons/pap/child_lock_button.svg) | `pap:child_lock_button` |
| ![child_lock_button_open](./custom_components/philips_airpurifier/icons/pap/child_lock_button_open.svg) | `pap:child_lock_button_open` | ![auto_mode_button](./custom_components/philips_airpurifier/icons/pap/auto_mode_button.svg) | `pap:auto_mode_button` |
| ![fan_speed_button](./custom_components/philips_airpurifier/icons/pap/fan_speed_button.svg) | `pap:fan_speed_button` | ![humidity_button](./custom_components/philips_airpurifier/icons/pap/humidity_button.svg) | `pap:humidity_button` |
| ![light_dimming_button](./custom_components/philips_airpurifier/icons/pap/light_dimming_button.svg) | `pap:light_dimming_button` | ![light_function](./custom_components/philips_airpurifier/icons/pap/light_function.svg) | `pap:light_function` |
| ![ambient_light](./custom_components/philips_airpurifier/icons/pap/ambient_light.svg) | `pap:ambient_light` | ![two_in_one_mode_button](./custom_components/philips_airpurifier/icons/pap/two_in_one_mode_button.svg) | `pap:two_in_one_mode_button` |
| ![timer_reset_button](./custom_components/philips_airpurifier/icons/pap/timer_reset_button.svg) | `pap:timer_reset_button` | ![sleep_mode](./custom_components/philips_airpurifier/icons/pap/sleep_mode.svg) | `pap:sleep_mode` |
| ![auto_mode](./custom_components/philips_airpurifier/icons/pap/auto_mode.svg) | `pap:auto_mode` | ![speed_1](./custom_components/philips_airpurifier/icons/pap/speed_1.svg) | `pap:speed_1` |
| ![speed_2](./custom_components/philips_airpurifier/icons/pap/speed_2.svg) | `pap:speed_2` | ![speed_3](./custom_components/philips_airpurifier/icons/pap/speed_3.svg) | `pap:speed_3` |
| ![allergen_mode](./custom_components/philips_airpurifier/icons/pap/allergen_mode.svg) | `pap:allergen_mode` | ![purification_only_mode](./custom_components/philips_airpurifier/icons/pap/purification_only_mode.svg) | `pap:purification_only_mode` |
| ![two_in_one_mode](./custom_components/philips_airpurifier/icons/pap/two_in_one_mode.svg) | `pap:two_in_one_mode` | ![bacteria_virus_mode](./custom_components/philips_airpurifier/icons/pap/bacteria_virus_mode.svg) | `pap:bacteria_virus_mode` |
| ![pollution_mode](./custom_components/philips_airpurifier/icons/pap/pollution_mode.svg) | `pap:pollution_mode` | ![nanoprotect_filter](./custom_components/philips_airpurifier/icons/pap/nanoprotect_filter.svg) | `pap:nanoprotect_filter` |
| ![filter_replacement](./custom_components/philips_airpurifier/icons/pap/filter_replacement.svg) | `pap:filter_replacement` | ![water_refill](./custom_components/philips_airpurifier/icons/pap/water_refill.svg) | `pap:water_refill` |
| ![prefilter_cleaning](./custom_components/philips_airpurifier/icons/pap/prefilter_cleaning.svg) | `pap:prefilter_cleaning` | ![prefilter_wick_cleaning](./custom_components/philips_airpurifier/icons/pap/prefilter_wick_cleaning.svg) | `pap:prefilter_wick_cleaning` |
| ![pm25](./custom_components/philips_airpurifier/icons/pap/pm25.svg) | `pap:pm25` | ![iai](./custom_components/philips_airpurifier/icons/pap/iai.svg) | `pap:iai` |
| ![wifi](./custom_components/philips_airpurifier/icons/pap/wifi.svg) | `pap:wifi` | ![reset](./custom_components/philips_airpurifier/icons/pap/reset.svg) | `pap:reset` |
| ![circulate](./custom_components/philips_airpurifier/icons/pap/circulate.svg) | `pap:circulate` | ![clean](./custom_components/philips_airpurifier/icons/pap/clean.svg) | `pap:clean` |
| ![mode](./custom_components/philips_airpurifier/icons/pap/mode.svg) | `pap:mode` | ![pm25b](./custom_components/philips_airpurifier/icons/pap/pm25b.svg) | `pap:pm25b` |
| ![rotate](./custom_components/philips_airpurifier/icons/pap/rotate.svg) | `pap:rotate` | ![oscillate](./custom_components/philips_airpurifier/icons/pap/oscillate.svg) | `pap:oscillate` |
| ![heating](./custom_components/philips_airpurifier/icons/pap/heating.svg) | `pap:heating` | ![gas](./custom_components/philips_airpurifier/icons/pap/gas.svg) | `pap:gas` |
| ![circle](./custom_components/philips_airpurifier/icons/pap/circle.svg) | `pap:circle` | ![temp_high](./custom_components/philips_airpurifier/icons/pap/temp_high.svg) | `pap:temp_high` |
| ![temp_medium](./custom_components/philips_airpurifier/icons/pap/temp_medium.svg) | `pap:temp_medium` | ![temp_low](./custom_components/philips_airpurifier/icons/pap/temp_low.svg) | `pap:temp_low` |

</details>

*Credit for the icon implementation goes to [@thomasloven](https://github.com/thomasloven)*

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Issues

- Use the [issue tracker](https://github.com/domalab/ha-philips-airpurifier/issues)
- Provide detailed information about your device model and firmware
- Include relevant logs when reporting bugs

### Adding Device Support

1. **Test your device** with the integration
2. **Collect device data** using the steps in [Troubleshooting](#-troubleshooting)
3. **Submit the data** via an issue or pull request

### Code Contributions

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/domalab/ha-philips-airpurifier.git
cd ha-philips-airpurifier

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

## 🙏 Credits

This integration builds upon the excellent work of many contributors:

- **[@rgerganov](https://github.com/rgerganov)**: Original reverse engineering and [py-air-control](https://github.com/rgerganov/py-air-control)
- **[@betaboon](https://github.com/betaboon)**: Initial [philips-airpurifier-coap](https://github.com/betaboon/philips-airpurifier-coap) integration
- **[@Denaun](https://github.com/Denaun)**: Major rework and improvements
- **[@mhetzi](https://github.com/mhetzi)**: Timer and reconnection functionality
- **[@Kraineff](https://github.com/Kraineff)**: Various contributions and testing
- **[@shexbeer](https://github.com/shexbeer)**: Device support and testing
- **[@thomasloven](https://github.com/thomasloven)**: Custom icon implementation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./custom_components/philips_airpurifier/LICENSE.txt) file for details.

---

### Made with ❤️ for the Home Assistant community

If you find this integration useful, consider:

- ⭐ Starring this repository
- 🐛 Reporting issues
- 🔧 Contributing improvements
- ☕ [Supporting the project](https://github.com/sponsors/domalab)
