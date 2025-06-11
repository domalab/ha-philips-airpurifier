# GitHub Labels Guide

This document describes the label system for the ha-philips-airpurifier repository.

## 🏷️ Label Categories

### Core Issue Types
| Label | Color | Description | Auto-Applied By |
|-------|-------|-------------|-----------------|
| `bug` | `#d73a4a` | Something isn't working | Bug Report template |
| `enhancement` | `#a2eeef` | New feature or request | Device Support & Feature Request templates |
| `device-support` | `#0052cc` | Request for support of new/unsupported device models | Device Support Request template |

### Priority Levels
| Label | Color | Description | Usage |
|-------|-------|-------------|-------|
| `priority: high` | `#d73a4a` | High priority issue requiring immediate attention | Manual assignment |
| `priority: medium` | `#fbca04` | Medium priority issue | Manual assignment |
| `priority: low` | `#0e8a16` | Low priority issue | Manual assignment |

### Component Categories
| Label | Color | Description | Usage |
|-------|-------|-------------|-------|
| `component: services` | `#5319e7` | Issues related to custom services functionality | Manual assignment |
| `component: discovery` | `#5319e7` | Issues related to device discovery and auto-detection | Manual assignment |
| `component: sensors` | `#5319e7` | Issues related to sensor entities (PM2.5, IAI, etc.) | Manual assignment |
| `component: connectivity` | `#5319e7` | Issues related to device connection and communication | Manual assignment |

### Device Types
| Label | Color | Description | Usage |
|-------|-------|-------------|-------|
| `device: air-purifier` | `#c2e0c6` | Issues specific to air purifier devices | Manual assignment |
| `device: humidifier` | `#c2e0c6` | Issues specific to humidifier devices | Manual assignment |
| `device: combo` | `#c2e0c6` | Issues specific to 2-in-1 air purifier/humidifier combo devices | Manual assignment |

### Status Tracking
| Label | Color | Description | Usage |
|-------|-------|-------------|-------|
| `status: needs-data` | `#fef2c0` | Waiting for additional data or information from reporter | Manual assignment |
| `status: in-progress` | `#0052cc` | Issue is currently being worked on | Manual assignment |
| `status: testing` | `#1d76db` | Feature/fix is ready for testing | Manual assignment |

### Default GitHub Labels (Preserved)
| Label | Color | Description |
|-------|-------|-------------|
| `documentation` | `#0075ca` | Improvements or additions to documentation |
| `duplicate` | `#cfd3d7` | This issue or pull request already exists |
| `good first issue` | `#7057ff` | Good for newcomers |
| `help wanted` | `#008672` | Extra attention is needed |
| `invalid` | `#e4e669` | This doesn't seem right |
| `question` | `#d876e3` | Further information is requested |
| `wontfix` | `#ffffff` | This will not be worked on |

## 🔄 Label Workflow

### Automatic Label Assignment
- **Device Support Request**: `device-support`, `enhancement`
- **Bug Report**: `bug`
- **Feature Request**: `enhancement`

### Manual Label Assignment Guidelines

#### For Device Support Requests:
1. Add device type: `device: air-purifier`, `device: humidifier`, or `device: combo`
2. Add priority based on device popularity and feasibility
3. Add `status: needs-data` if more information is required
4. Add `status: in-progress` when development starts
5. Add `status: testing` when ready for user testing

#### For Bug Reports:
1. Add component label based on the affected functionality
2. Add device type if issue is device-specific
3. Add priority based on severity and impact
4. Add `status: needs-data` if reproduction steps or logs are needed

#### For Feature Requests:
1. Add component label for the affected area
2. Add priority based on user impact and implementation complexity
3. Add device type if feature is device-specific

## 📊 Label Usage Examples

### Device Support Request Example:
```
Labels: device-support, enhancement, device: air-purifier, priority: medium, status: needs-data
```

### Bug Report Example:
```
Labels: bug, component: connectivity, device: combo, priority: high, status: in-progress
```

### Feature Request Example:
```
Labels: enhancement, component: services, priority: low, status: testing
```

## 🛠️ Label Management

### Adding New Labels
Use the GitHub API or web interface to create new labels following the naming conventions:
- `category: specific-item` format for grouped labels
- Consistent color schemes within categories
- Clear, descriptive names and descriptions

### Color Scheme
- **Red (`#d73a4a`)**: High priority, critical issues
- **Orange (`#fbca04`)**: Medium priority, warnings
- **Green (`#0e8a16`)**: Low priority, success states
- **Blue (`#0052cc`)**: In progress, informational
- **Purple (`#5319e7`)**: Component categories
- **Light Green (`#c2e0c6`)**: Device types
- **Light Yellow (`#fef2c0`)**: Status indicators

This label system provides comprehensive organization while maintaining simplicity and consistency.
