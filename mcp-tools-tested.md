# MCP Tools Testing Checklist

This document tracks manual testing of all MCP tools defined in `server.py`.

## JSON-RPC Tools

### Element Interaction
- [ ] `set_text` - Sets text on an element by ID
- [ ] `show_keyboard` - Shows keyboard for a specific element
- [ ] `click_coordinate` - Clicks a specific coordinate on screen
- [ ] `take_screenshot` - Captures a screenshot
- [ ] `get_page_source` - Retrieves current page source

### Element Finding & Attributes
- [ ] `find_objects` - Finds element IDs by selector
- [ ] `bounds_of` - Returns bounding box of an element
- [ ] `get_attribute` - Retrieves element attributes

### Input Events
- [ ] `inject_input_key_event` - Injects key event with duration
- [ ] `press_button` - Presses button by name using keycode mapping

## Shell Tools

### Application Management
- [ ] `launch_app` - Launches application via vmsgr
- [ ] `terminate_app` - Terminates application via vlcm
- [ ] `install_app` - Installs application via vpm
- [ ] `uninstall_app` - Uninstalls application via vpm
- [ ] `is_app_installed` - Checks if app is installed

### Input Commands
- [ ] `input_text` - Types text via input command
- [ ] `input_key_event` - Sends key event via input command

## Notes

Add any testing notes, issues, or observations below:

---
