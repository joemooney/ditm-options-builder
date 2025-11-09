# Port Management System

## Overview

The DITM Options Portfolio Builder now includes a **global port management system** that tracks port assignments across all your development applications. This prevents port conflicts and provides a centralized registry at `$HOME/.ports`.

## Features

- **Global Registry**: Single file (`~/.ports`) tracks all port assignments
- **Conflict Detection**: Automatically detects and prevents port conflicts
- **Auto-Assignment**: Finds available ports if preferred port is taken
- **CLI Tool**: Manage ports from command line
- **Programmatic API**: Python API for application integration

## Quick Start

### View All Registered Ports

```bash
python port_manager.py list
```

Output:
```
Application          Port     Description
----------------------------------------------------------------------
ditm                 5010     DITM Options Portfolio Builder - Web Interface
```

### Register a New Application

```bash
python port_manager.py register myapp 5020 --description "My Application Server"
```

### Find an Available Port

```bash
python port_manager.py find --start 5000 --end 6000
```

Output:
```
Available port: 5011
```

### Get Port for Specific Application

```bash
python port_manager.py get ditm
```

Output:
```
ditm: 5010
```

### Unregister an Application

```bash
python port_manager.py unregister myapp
```

---

## Registry File Format

**Location**: `$HOME/.ports`

**Format**: `application_name:port_number:description`

**Example**:
```
# Global Port Registry
# Format: application_name:port_number:description
# This file tracks port assignments across all development applications

ditm:5010:DITM Options Portfolio Builder - Web Interface
myapp:5020:My Application Server
webapp:5030:React Frontend Development Server
api:5040:REST API Backend
```

---

## CLI Reference

### Commands

#### `list`
List all registered ports.

```bash
python port_manager.py list
```

**Output**: Table with application name, port, and description.

#### `get <app_name>`
Get the port assigned to a specific application.

```bash
python port_manager.py get ditm
```

**Exit Code**:
- 0: Port found
- 1: Application not registered

#### `register <app_name> <port> [--description <desc>]`
Register or update a port assignment.

```bash
python port_manager.py register myapp 5020 --description "My App"
```

**Arguments**:
- `app_name`: Application identifier (alphanumeric, underscores, hyphens)
- `port`: Port number (1-65535)
- `--description`, `-d`: Optional description

**Exit Code**:
- 0: Success
- 1: Port conflict (already assigned to different app)

#### `unregister <app_name>`
Remove a port assignment.

```bash
python port_manager.py unregister myapp
```

#### `find [--start <port>] [--end <port>]`
Find the next available port in a range.

```bash
python port_manager.py find --start 5000 --end 6000
```

**Options**:
- `--start`: Start of port range (default: 5000)
- `--end`: End of port range (default: 6000)

**Exit Code**:
- 0: Found available port
- 1: No available ports in range

---

## Python API

### Basic Usage

```python
from port_manager import PortManager

# Initialize manager
pm = PortManager()

# Get port for application
port = pm.get_port('ditm')
if port:
    print(f"DITM is using port {port}")
else:
    print("DITM not registered")
```

### Register Port

```python
pm = PortManager()

try:
    pm.register_port('myapp', 5020, 'My Application')
    print("✓ Port registered")
except ValueError as e:
    print(f"Error: {e}")
```

### Find Available Port

```python
pm = PortManager()

try:
    port = pm.find_available_port(start_port=5000, end_port=6000)
    print(f"Available port: {port}")
except ValueError:
    print("No available ports in range")
```

### List All Ports

```python
pm = PortManager()

ports = pm.list_ports()
for app_name, port, description in ports:
    print(f"{app_name}: {port} - {description}")
```

### Unregister Port

```python
pm = PortManager()
pm.unregister_port('myapp')
```

---

## Integration with Web Applications

### Flask Example

The DITM web application demonstrates automatic integration:

```python
from port_manager import PortManager

if __name__ == '__main__':
    # Get port from port manager
    port_manager = PortManager()
    app_name = "ditm"
    port = port_manager.get_port(app_name)

    if port is None:
        # Register with default port
        port = 5010
        try:
            port_manager.register_port(
                app_name,
                port,
                "DITM Options Portfolio Builder"
            )
        except ValueError as e:
            # Port conflict - auto-assign
            port = port_manager.find_available_port(5000, 6000)
            port_manager.register_port(app_name, port, "DITM")
            print(f"Auto-assigned port {port}")

    app.run(host='0.0.0.0', port=port)
```

### Express.js Example

```javascript
const PortManager = require('./port_manager');  // You'd need to implement this
const express = require('express');

const pm = new PortManager();
const appName = 'myapp';
let port = pm.getPort(appName);

if (!port) {
    port = pm.findAvailablePort(5000, 6000);
    pm.registerPort(appName, port, 'My Express App');
}

const app = express();
app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
```

---

## How DITM Uses Port Manager

When you start the DITM web server:

```bash
python web_app.py
```

**Automatic Behavior**:

1. **Check Registry**: Looks for 'ditm' in `~/.ports`
2. **Use Registered Port**: If found, uses that port
3. **Register Default**: If not found, registers port 5010
4. **Conflict Resolution**: If 5010 is taken, finds available port
5. **Start Server**: Launches Flask on assigned port

**Console Output**:
```
======================================================================
DITM Options Portfolio Builder - Web Interface
======================================================================
Starting server at http://localhost:5010
Port assignment managed via: /home/joe/.ports
Press Ctrl+C to stop
======================================================================
```

---

## Best Practices

### 1. Use Descriptive Application Names

**Good**:
```bash
python port_manager.py register my-web-app 5020 --description "Customer Portal"
```

**Bad**:
```bash
python port_manager.py register app1 5020 --description "App"
```

### 2. Document Your Ports

Always include descriptions:
```bash
python port_manager.py register analytics-api 5030 \
    --description "Analytics REST API (Production)"
```

### 3. Reserve Port Ranges

Consider reserving ranges for different types of apps:
- **5000-5099**: Web interfaces
- **5100-5199**: REST APIs
- **5200-5299**: WebSocket servers
- **5300-5399**: Database interfaces

### 4. Check Before Starting Development

Before starting a new app, find an available port:
```bash
python port_manager.py find --start 5000 --end 5100
```

### 5. Clean Up Unused Registrations

Periodically review and clean up:
```bash
python port_manager.py list
python port_manager.py unregister old-app
```

---

## Troubleshooting

### Port Already in Use

**Symptom**: Error when starting server despite registry showing port available.

**Cause**: Application crashed without releasing port, or another unregistered app is using it.

**Solution**:
```bash
# Find process using port
lsof -i :5010

# Kill process
kill -9 <PID>

# Or use different port
python port_manager.py find
```

### Registry File Corrupted

**Symptom**: `port_manager.py` fails to parse registry.

**Solution**:
```bash
# Backup current registry
cp ~/.ports ~/.ports.backup

# Recreate from scratch
rm ~/.ports
python port_manager.py list  # Creates new empty registry

# Manually re-register apps
python port_manager.py register ditm 5010 --description "DITM"
```

### Permission Denied

**Symptom**: Cannot write to `~/.ports`

**Solution**:
```bash
# Check permissions
ls -la ~/.ports

# Fix permissions
chmod 644 ~/.ports

# Ensure ownership
chown $USER ~/.ports
```

### Port Conflicts Between Machines

**Problem**: Different machines should use different ports for same app.

**Solution**: Use environment variables:
```python
port_override = os.getenv('DITM_PORT')
if port_override:
    port = int(port_override)
else:
    port = port_manager.get_port('ditm')
```

---

## Advanced Usage

### Custom Registry Location

```python
pm = PortManager(registry_path='/path/to/custom/.ports')
```

### Programmatic Port Assignment

```python
def ensure_port(app_name: str, preferred_port: int) -> int:
    """Ensure app has a port, registering if needed."""
    pm = PortManager()
    port = pm.get_port(app_name)

    if port is None:
        try:
            pm.register_port(app_name, preferred_port)
            return preferred_port
        except ValueError:
            # Port taken, find alternative
            port = pm.find_available_port(5000, 6000)
            pm.register_port(app_name, port)
            return port

    return port
```

### Batch Registration

```python
pm = PortManager()

apps = [
    ('frontend', 5000, 'React Frontend'),
    ('backend', 5001, 'Django Backend'),
    ('api', 5002, 'REST API'),
    ('websocket', 5003, 'WebSocket Server'),
]

for app_name, port, description in apps:
    try:
        pm.register_port(app_name, port, description)
        print(f"✓ {app_name} -> {port}")
    except ValueError as e:
        print(f"✗ {app_name}: {e}")
```

### Port Range Validation

```python
def is_port_in_range(port: int, start: int = 5000, end: int = 6000) -> bool:
    """Check if port is in allowed range."""
    return start <= port < end

pm = PortManager()
port = 8080

if not is_port_in_range(port):
    print(f"Warning: Port {port} outside standard range")
```

---

## Integration with Other Tools

### Docker Compose

Use port manager to assign ports before generating `docker-compose.yml`:

```bash
#!/bin/bash
FRONTEND_PORT=$(python port_manager.py get frontend)
BACKEND_PORT=$(python port_manager.py get backend)

cat > docker-compose.yml <<EOF
version: '3'
services:
  frontend:
    ports:
      - "${FRONTEND_PORT}:3000"
  backend:
    ports:
      - "${BACKEND_PORT}:8000"
EOF
```

### Systemd Services

Reference ports in systemd unit files:

```bash
#!/bin/bash
APP_NAME="ditm"
PORT=$(python /home/joe/ai/ditm/port_manager.py get $APP_NAME)

cat > /etc/systemd/system/ditm.service <<EOF
[Service]
Environment="PORT=${PORT}"
ExecStart=/home/joe/ai/ditm/.venv/bin/python web_app.py
EOF
```

### Nginx Reverse Proxy

Generate nginx configs from registry:

```python
from port_manager import PortManager

pm = PortManager()
ports = pm.list_ports()

for app_name, port, description in ports:
    config = f"""
server {{
    listen 80;
    server_name {app_name}.example.com;

    location / {{
        proxy_pass http://localhost:{port};
    }}
}}
"""
    with open(f'/etc/nginx/sites-available/{app_name}', 'w') as f:
        f.write(config)
```

---

## Migration Guide

### Migrating Existing Applications

1. **List Current Ports**:
   ```bash
   # Find all servers running on localhost
   lsof -i -P | grep LISTEN | grep localhost
   ```

2. **Register Each Application**:
   ```bash
   python port_manager.py register app1 5000 --description "App 1"
   python port_manager.py register app2 5001 --description "App 2"
   ```

3. **Update Application Code**:
   Replace hardcoded ports with port manager calls.

4. **Test**:
   Verify each app uses registered port.

### Example Migration

**Before**:
```python
# Hardcoded port
app.run(host='0.0.0.0', port=5010)
```

**After**:
```python
from port_manager import PortManager

pm = PortManager()
port = pm.get_port('myapp') or 5010
pm.register_port('myapp', port, 'My Application')
app.run(host='0.0.0.0', port=port)
```

---

## API Reference

### `PortManager` Class

#### `__init__(registry_path: str = None)`
Initialize port manager.

**Parameters**:
- `registry_path`: Path to registry file (default: `~/.ports`)

#### `get_port(app_name: str) -> Optional[int]`
Get assigned port for application.

**Returns**: Port number or `None` if not found

#### `register_port(app_name: str, port: int, description: str = "")`
Register or update port assignment.

**Raises**: `ValueError` if port is already assigned to different app

#### `unregister_port(app_name: str)`
Remove port assignment.

#### `list_ports() -> List[Tuple[str, int, str]]`
List all registered ports.

**Returns**: List of `(app_name, port, description)` tuples

#### `find_available_port(start_port: int = 5000, end_port: int = 6000) -> int`
Find next available port in range.

**Returns**: First available port number

**Raises**: `ValueError` if no available ports

---

## Security Considerations

### File Permissions

The registry file (`~/.ports`) should be readable by your user:
```bash
chmod 644 ~/.ports
```

### Port Range Restrictions

Use unprivileged ports (1024-65535) for development:
- **Do not use**: 1-1023 (require root)
- **Safe range**: 5000-9999 (common for development)

### Network Exposure

By default, Flask binds to `0.0.0.0` (all interfaces). For security:
- **Development**: Use `127.0.0.1` (localhost only)
- **Production**: Use proper firewall rules

```python
# Localhost only
app.run(host='127.0.0.1', port=port)

# All interfaces (requires firewall)
app.run(host='0.0.0.0', port=port)
```

---

## Future Enhancements

Potential additions:
- **Port Reservations**: Reserve ports without starting apps
- **Multi-User Support**: Per-user registries
- **Web UI**: Browser-based port management
- **Health Checks**: Verify ports are actually in use
- **Auto-Discovery**: Scan network for active ports
- **Cloud Integration**: Sync ports across development machines

---

## Conclusion

The port management system provides:

✅ **Centralized Registry**: Single source of truth for all ports
✅ **Conflict Prevention**: Automatic detection and resolution
✅ **Easy Integration**: Simple Python API and CLI
✅ **Flexibility**: Works with any web framework
✅ **Transparency**: Human-readable registry file

**Start using it today**:
```bash
python port_manager.py list
```

For questions or issues, refer to:
- **README.md** - Project overview
- **WEB_INTERFACE_GUIDE.md** - Web interface documentation

Happy developing! 🚀
