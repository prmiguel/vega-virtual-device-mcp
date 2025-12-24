# [WIP] Vega Virtual Device MCP Server

This is a Model Context Protocol (MCP) server that provides control over a Vega Virtual Device (Kepler). It exposes tools to interact with the device using both JSON-RPC (via HTTP) and direct shell commands.

## Prerequisites

- **Python 3.10+**
- **Access to Vega Device Tools**: The server must run in an environment where `vpm`, `vlcm`, `vmsgr`, `vda`, and `input` commands are available (e.g., inside the device container).
- **Kepler CLI**: The `kepler` command must be available for device connection checks.
- **Network Access**: Must be able to reach `http://localhost:8383/jsonrpc` (or configured URL).

## Configuration

| Environment Variable | Description | Default |
| :--- | :--- | :--- |
| `JSON_RPC_URL` | URL of the Vega JSON-RPC endpoint | `http://localhost:8383/jsonrpc` |

## Installation

1.  Clone this repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Startup Behavior

The server automatically performs the following checks on startup:
1. **Device Connection Check**: Waits for the Simulator device to be connected using `kepler device is-connected -d Simulator`
2. **Port Forwarding Setup**: Configures port forwarding with `vda forward tcp:8383 tcp:8383`

### Stdio (Default)
Run the server using `fastmcp` over standard input/output (for local MCP clients like Claude Desktop):

```bash
fastmcp run server.py
```

### HTTP (SSE)
To expose the server via HTTP (e.g., for Docker or remote access):

```bash
fastmcp run server.py --transport sse --host 0.0.0.0 --port 8000
```
*Ensure port 8000 is exposed in your container/environment.*

## Available Tools

### JSON-RPC Tools
Interact via the application's JSON-RPC interface (port 8383).

- `set_text(id: int, text: str)` - Sets text on an element by ID
- `show_keyboard(id: int)` - Shows keyboard for a specific element
- `click_coordinate(x: int, y: int)` - Clicks a specific coordinate on screen
- `take_screenshot()` - Captures a screenshot
- `get_page_source()` - Retrieves the current page source
- `find_objects(selector_strategy: str, args: dict)` - Finds element IDs by selector
- `bounds_of(id: int)` - Returns bounding box of an element
- `get_attribute(id: int, attribute: str)` - Retrieves element attributes
- `inject_input_key_event(input_key_event: str, hold_duration: int)` - Injects key event with duration
- `press_button(name: str, hold_duration: int)` - Presses button by name using keycode mapping from `keycodes.json`

### Shell Tools
Interact via system shell commands (executed through `vda shell`).

- `launch_app(app_id: str)` - Launches application via `vmsgr`
- `terminate_app(app_id: str)` - Terminates application via `vlcm` (uses PID lookup)
- `install_app(remote_path: str)` - Installs application via `vpm`
- `uninstall_app(app_id: str)` - Uninstalls application via `vpm`
- `is_app_installed(app_id: str)` - Checks if app is installed
- `input_text(text: str)` - Types text via `input` command
- `input_key_event(keycode: int)` - Sends key event via `input` command

## Available Resources

MCP resources provide read-only access to device state and information.

### `device://status`
Returns the current device connection status and configuration.

**Response includes:**
- Device name
- JSON-RPC endpoint URL
- Port forwarding configuration
- Connection status
- JSON-RPC accessibility check

### `device://screenshot`
Returns the current screenshot of the device as a base64-encoded image.

**Use case:** Query the current visual state without executing a tool action.

### `device://page-source`
Returns the XML representation of the current UI hierarchy.

**Use case:** Understand available UI elements and their structure before interacting with them.

### `device://keycodes`
Returns all available keycode mappings for the `press_button` tool.

**Response includes:**
- Total number of keycodes
- Canonical key names
- Key codes
- Alternative aliases for each key

**Use case:** Discover valid button names before calling `press_button`.


## Testing

See [mcp-tools-tested.md](mcp-tools-tested.md) for a checklist to track manual testing of all MCP tools.
