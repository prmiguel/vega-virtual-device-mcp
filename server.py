from fastmcp import FastMCP
import requests
import subprocess
import os
import json
import shlex
import time
import sys
from typing import Optional, Dict, Any, List

# Configuration
JSON_RPC_URL = os.getenv("JSON_RPC_URL", "http://localhost:8383/jsonrpc")

# Initialize Server

mcp = FastMCP("Vega Virtual Device MCP")

# --- Keycode Loading ---
KEYCODES_FILE = os.path.join(os.path.dirname(__file__), "keycodes.json")
KEYCODE_MAP = {}

try:
    with open(KEYCODES_FILE, 'r') as f:
        keycodes_data = json.load(f)
        for entry in keycodes_data:
            # Map canonical name
            KEYCODE_MAP[entry["name"].upper()] = entry["code"]
            # Map all alternatives
            for alt in entry["alternatives"]:
                KEYCODE_MAP[str(alt).upper()] = entry["code"]
    print(f"Loaded {len(KEYCODE_MAP)} keycode mappings.")
except Exception as e:
    print(f"Warning: Failed to load keycodes.json: {e}")


# --- Helpers ---

def _json_rpc_call(method: str, params: Dict[str, Any]) -> Any:
    """Helper to make JSON-RPC calls."""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    try:
        response = requests.post(JSON_RPC_URL, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            return f"Error: {data['error']}"
        return data.get("result")
    except requests.RequestException as e:
        return f"HTTP Request Failed: {e}"


def _shell(command: str) -> str:
    """Helper to run shell commands."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            return f"Command Failed (Exit Code {result.returncode}):\nStdout: {result.stdout}\nStderr: {result.stderr}"
        return result.stdout.strip()
    except Exception as e:
        return f"Execution Error: {e}"


# --- JSON-RPC Tools ---

def wait_for_device():
    """Waits for the device to be connected."""
    print("Waiting for device Simulator to be connected...")
    while True:
        result = _shell("kepler device is-connected -d Simulator")
        if "Device Simulator is connected" in result:
            print("Device connected!")
            break
        time.sleep(2)

def setup_port_forwarding():
    """Sets up port forwarding for JSON-RPC."""
    print("Setting up port forwarding...")
    result = _shell("vda forward tcp:8383 tcp:8383")
    if "8383" in result:
        print("Port forwarding set up successfully on port 8383")
    else:
        print(f"Warning: Port forwarding might have failed. Output: {result}")

# Initialize Server
wait_for_device()
setup_port_forwarding()


@mcp.tool()
def set_text(id: int, text: str) -> str:
    """Sets text on the element with the given ID (Vega JSON-RPC)."""
    return str(_json_rpc_call("setText", {"id": id, "text": text}))

@mcp.tool()
def show_keyboard(id: int) -> str:
    """Requests to show the keyboard for a specific element ID (Vega JSON-RPC)."""
    return str(_json_rpc_call("showKeyboard", {"id": id}))

@mcp.tool()
def click_coordinate(x: int, y: int) -> str:
    """Clicks a specific coordinate on the screen (Vega JSON-RPC)."""
    return str(_json_rpc_call("v2.clickCoordinate", {"x": x, "y": y}))

@mcp.tool()
def take_screenshot() -> str:
    """Captures a screenshot of the device (Vega JSON-RPC)."""
    return str(_json_rpc_call("takeScreenshot", {}))

@mcp.tool()
def find_objects(selector_strategy: str, args: Dict[str, Any]) -> Any:
    """Finds element IDs matching the selector (Vega JSON-RPC).
    
    Args:
        selector_strategy: 'uiSelector', 'javaUiSelector', 'xpath', or 'id'.
        args: Dictionary containing selector arguments (e.g., {'text': 'Home'}).
    """
    return _json_rpc_call("findObjects", {"selectorStrategy": selector_strategy, "args": args})

@mcp.tool()
def bounds_of(id: int) -> Any:
    """Returns the bounding box {x, y, width, height} of an element (Vega JSON-RPC)."""
    return _json_rpc_call("boundsOf", {"id": id})

@mcp.tool()
def get_attribute(id: int, attribute: str) -> Any:
    """Retrieves an attribute of an element (Vega JSON-RPC).
    
    Supported attributes:
    isEnabled, isFocused, isCheckable, isChecked, isClickable, isEditable,
    isFocusable, isLongClickable, isScrollable, isDraggable, isPinchable,
    isPageable, visibilityOf, getText, getTestId, getDescription, getRole,
    getCurrentPage, getPageCount, getScrollDirections, getScrollOffset.
    """
    return _json_rpc_call(attribute, {"id": id})

@mcp.tool()
def inject_input_key_event(input_key_event: str, hold_duration: int = 100) -> str:
    """Injects a key event (e.g., keycode) with a duration (Vega JSON-RPC)."""
    return str(_json_rpc_call("injectInputKeyEvent", {"inputKeyEvent": input_key_event, "holdDuration": hold_duration}))

@mcp.tool()
def press_button(name: str, hold_duration: int = 100) -> str:
    """Presses a button by name (or alias) using the loaded keycode mapping."""
    name_upper = name.upper()
    if name_upper in KEYCODE_MAP:
        code = KEYCODE_MAP[name_upper]
        return str(_json_rpc_call("injectInputKeyEvent", {"inputKeyEvent": str(code), "holdDuration": hold_duration}))
    
    # Fallback: try to see if the input is already a number
    if name.isdigit():
         return str(_json_rpc_call("injectInputKeyEvent", {"inputKeyEvent": name, "holdDuration": hold_duration}))

    return f"Error: Key name '{name}' not found in keycodes configuration."


# --- Shell Tools ---

@mcp.tool()
def launch_app(app_id: str) -> str:
    """Launches an application via vmsgr."""
    # Using proper shell escaping for the app_id is safer, though vmsgr syntax is specific.
    # We'll trust the input is a valid ID for now, but in prod consider validation.
    return _shell(f"vda shell -- 'vmsgr send orpheus://{shlex.quote(app_id)}'")

@mcp.tool()
def terminate_app(app_id: str) -> str:
    """Terminates an application via vlcm."""
    return _shell(f"vda shell -- 'vlcm terminate-app --pkg-id {shlex.quote(app_id)} --force'")

@mcp.tool()
def install_app(remote_path: str) -> str:
    """Installs an application from a local path on the device (vpm)."""
    return _shell(f"vda shell -- 'vpm install {shlex.quote(remote_path)}'")

@mcp.tool()
def uninstall_app(app_id: str) -> str:
    """Uninstalls an application via vpm."""
    return _shell(f"vda shell -- 'vpm uninstall {shlex.quote(app_id)}'")

@mcp.tool()
def is_app_installed(app_id: str) -> str:
    """Checks if an app is installed via vpm list."""
    # Generates exit code 0 if found, 1 if not
    # Complex piping needs careful quoting when wrapped in vda shell
    cmd = f"vda shell -- 'vpm list packages | grep -x \"[[:space:]]*{app_id}\" || true'"
    result = _shell(cmd)
    return "true" if app_id in result else "false"

@mcp.tool()
def input_text(text: str) -> str:
    """Types text via input command (Android/Linux shell)."""
    # 'input text' requires replacing spaces with %s or similar on older droids,
    # or escaped spaces. On many modern implementations simply quoting works or specific escaping.
    # The reference used 'replace(/ /g, "\\ ")'.
    escaped_text = text.replace(" ", "\\ ")
    return _shell(f"vda shell -- 'input text {shlex.quote(escaped_text)}'")

@mcp.tool()
def input_key_event(keycode: int) -> str:
    """Sends a key event via input command (Android/Linux shell)."""
    return _shell(f"vda shell -- 'input keyevent {keycode}'")

if __name__ == "__main__":
    mcp.run()
