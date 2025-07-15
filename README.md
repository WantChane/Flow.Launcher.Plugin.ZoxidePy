# Flow.Launcher.Plugin.ZoxidePy

Zoxide integration for Flow Launcher, written in Python.

## Description

ZoxidePy is a Flow Launcher plugin that integrates with [Zoxide](https://github.com/ajeetdsouza/zoxide), a smarter cd command that learns your habits. This plugin allows you to quickly navigate to frequently used directories directly from Flow Launcher.

## Features

- **Smart Directory Navigation**: Quickly jump to frequently used directories
- **Contextual Search**: Search directories based on your usage patterns
- **Context Menu**: Right-click for additional options like copying paths and removing directories
- **Add & Open Directory (`z cd`)**: Instantly add a new directory to zoxide and open it

## Prerequisites

- [Flow Launcher](https://www.flowlauncher.com/) installed
- [Zoxide](https://github.com/ajeetdsouza/zoxide) installed on your system
  
## Installation

### Manual
1. Download the latest release from the [Releases](https://github.com/WantChane/Flow.Launcher.Plugin.ZoxidePy/releases) page
2. Extract the zip file to your Flow Launcher plugins directory
3. Restart Flow Launcher
4. Configure the zoxide executable path in plugin settings if needed

## Configuration

1. **Zoxide Executable Directory**
   - Default: `zoxide.exe` (if zoxide is in your PATH)
   - Example: `C:\Program Files\zoxide\zoxide.exe`

## Usage

### Basic Search
- Type `z` followed by a space and your search query
- Example: `z documents` to find directories containing "documents"

### Add & Open Directory (`z cd`)
- Type `z cd` followed by a space and path
- Example: `z cd D:\Projects\MyApp`

### Actions
- **Enter**: Open the selected directory in File Explorer
- **Right Click**: Show context menu with additional options
  - **Copy path**: Copy the directory path to clipboard
  - **Remove from zoxide**: Remove the directory from zoxide database

## License

[MIT](LICENSE)

## Acknowledgments

- [Zoxide](https://github.com/ajeetdsouza/zoxide) - The amazing directory jumper
- [Flow Launcher](https://www.flowlauncher.com/) - The powerful application launcher
- [PyFlowLauncher](https://github.com/Garulf/pyFlowLauncher) - Python SDK for Flow Launcher plugins