#!/usr/bin/env python3
"""
Port Management Utility
Manages port assignments across multiple applications using a global registry.
"""
import os
from pathlib import Path
from typing import Optional, Dict, List, Tuple


class PortManager:
    """Manages application port assignments via global registry."""

    def __init__(self, registry_path: str = None):
        """
        Initialize PortManager.

        Args:
            registry_path: Path to port registry file. Defaults to $HOME/.ports
        """
        if registry_path is None:
            registry_path = os.path.expanduser("~/.ports")

        self.registry_path = Path(registry_path)
        self._ensure_registry_exists()

    def _ensure_registry_exists(self):
        """Create registry file if it doesn't exist."""
        if not self.registry_path.exists():
            self.registry_path.write_text(
                "# Global Port Registry\n"
                "# Format: application_name:port_number:description\n"
                "# This file tracks port assignments across all development applications\n\n"
            )

    def _parse_registry(self) -> Dict[str, Tuple[int, str]]:
        """
        Parse the registry file.

        Returns:
            Dict mapping app_name -> (port, description)
        """
        registry = {}

        if not self.registry_path.exists():
            return registry

        with open(self.registry_path, 'r') as f:
            for line in f:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                parts = line.split(':', 2)
                if len(parts) >= 2:
                    app_name = parts[0].strip()
                    try:
                        port = int(parts[1].strip())
                        description = parts[2].strip() if len(parts) > 2 else ""
                        registry[app_name] = (port, description)
                    except ValueError:
                        # Skip malformed lines
                        continue

        return registry

    def get_port(self, app_name: str) -> Optional[int]:
        """
        Get the assigned port for an application.

        Args:
            app_name: Application identifier

        Returns:
            Port number or None if not found
        """
        registry = self._parse_registry()
        if app_name in registry:
            return registry[app_name][0]
        return None

    def register_port(self, app_name: str, port: int, description: str = ""):
        """
        Register or update a port assignment.

        Args:
            app_name: Application identifier
            port: Port number to assign
            description: Optional description of the application
        """
        registry = self._parse_registry()

        # Check if port is already in use by another app
        for existing_app, (existing_port, _) in registry.items():
            if existing_port == port and existing_app != app_name:
                raise ValueError(
                    f"Port {port} is already assigned to '{existing_app}'. "
                    f"Choose a different port or unregister that application first."
                )

        # Update registry
        registry[app_name] = (port, description)

        # Write back to file
        self._write_registry(registry)

    def unregister_port(self, app_name: str):
        """
        Remove a port assignment.

        Args:
            app_name: Application identifier to remove
        """
        registry = self._parse_registry()

        if app_name in registry:
            del registry[app_name]
            self._write_registry(registry)

    def list_ports(self) -> List[Tuple[str, int, str]]:
        """
        List all registered ports.

        Returns:
            List of (app_name, port, description) tuples
        """
        registry = self._parse_registry()
        return [
            (app_name, port, description)
            for app_name, (port, description) in sorted(registry.items())
        ]

    def find_available_port(self, start_port: int = 5000, end_port: int = 6000) -> int:
        """
        Find the next available port in a range.

        Args:
            start_port: Start of range (inclusive)
            end_port: End of range (exclusive)

        Returns:
            First available port number

        Raises:
            ValueError: If no available ports in range
        """
        registry = self._parse_registry()
        used_ports = {port for port, _ in registry.values()}

        for port in range(start_port, end_port):
            if port not in used_ports:
                return port

        raise ValueError(f"No available ports in range {start_port}-{end_port}")

    def _write_registry(self, registry: Dict[str, Tuple[int, str]]):
        """Write registry dictionary back to file."""
        lines = [
            "# Global Port Registry",
            "# Format: application_name:port_number:description",
            "# This file tracks port assignments across all development applications",
            ""
        ]

        # Sort by port number for readability
        sorted_entries = sorted(registry.items(), key=lambda x: x[1][0])

        for app_name, (port, description) in sorted_entries:
            lines.append(f"{app_name}:{port}:{description}")

        self.registry_path.write_text('\n'.join(lines) + '\n')


def main():
    """CLI interface for port management."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Manage application port assignments"
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List command
    subparsers.add_parser('list', help='List all registered ports')

    # Get command
    get_parser = subparsers.add_parser('get', help='Get port for an application')
    get_parser.add_argument('app_name', help='Application name')

    # Register command
    register_parser = subparsers.add_parser('register', help='Register a port')
    register_parser.add_argument('app_name', help='Application name')
    register_parser.add_argument('port', type=int, help='Port number')
    register_parser.add_argument('--description', '-d', default='',
                                 help='Application description')

    # Unregister command
    unregister_parser = subparsers.add_parser('unregister',
                                              help='Unregister an application')
    unregister_parser.add_argument('app_name', help='Application name')

    # Find available command
    find_parser = subparsers.add_parser('find', help='Find available port')
    find_parser.add_argument('--start', type=int, default=5000,
                            help='Start of port range')
    find_parser.add_argument('--end', type=int, default=6000,
                            help='End of port range')

    args = parser.parse_args()

    manager = PortManager()

    if args.command == 'list':
        ports = manager.list_ports()
        if not ports:
            print("No registered ports")
        else:
            print(f"{'Application':<20} {'Port':<8} Description")
            print("-" * 70)
            for app_name, port, description in ports:
                print(f"{app_name:<20} {port:<8} {description}")

    elif args.command == 'get':
        port = manager.get_port(args.app_name)
        if port:
            print(f"{args.app_name}: {port}")
        else:
            print(f"No port registered for '{args.app_name}'")
            exit(1)

    elif args.command == 'register':
        try:
            manager.register_port(args.app_name, args.port, args.description)
            print(f"✓ Registered {args.app_name} on port {args.port}")
        except ValueError as e:
            print(f"Error: {e}")
            exit(1)

    elif args.command == 'unregister':
        manager.unregister_port(args.app_name)
        print(f"✓ Unregistered {args.app_name}")

    elif args.command == 'find':
        try:
            port = manager.find_available_port(args.start, args.end)
            print(f"Available port: {port}")
        except ValueError as e:
            print(f"Error: {e}")
            exit(1)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
