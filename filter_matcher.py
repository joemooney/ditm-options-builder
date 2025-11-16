#!/usr/bin/env python3
"""
Filter Preset Matcher
Checks which filter presets a given option matches.
"""
import json
from pathlib import Path
from typing import Dict, List


class FilterMatcher:
    """Matches options against filter presets."""

    def __init__(self, presets_path: str = "./filter_presets.json"):
        self.presets_path = Path(presets_path)
        self.presets_config = self._load_presets()

    def _load_presets(self) -> Dict:
        """Load filter presets from JSON file."""
        if not self.presets_path.exists():
            raise FileNotFoundError(f"Presets file not found: {self.presets_path}")

        with open(self.presets_path, 'r') as f:
            return json.load(f)

    def reload_presets(self):
        """Reload presets from file (if updated)."""
        self.presets_config = self._load_presets()

    def get_preset(self, preset_name: str) -> Dict:
        """Get a specific preset configuration."""
        presets = self.presets_config.get('filter_presets', {})
        if preset_name not in presets:
            raise ValueError(f"Preset '{preset_name}' not found")
        return presets[preset_name]

    def get_all_presets(self) -> Dict:
        """Get all preset configurations."""
        return self.presets_config.get('filter_presets', {})

    def get_default_preset(self) -> str:
        """Get the default preset name."""
        return self.presets_config.get('default_preset', 'moderate')

    def check_preset_match(self, option_data: Dict, preset_name: str) -> bool:
        """
        Check if an option matches a specific preset's criteria.

        Args:
            option_data: Dict with option metrics (delta, IV, DTE, etc.)
            preset_name: Name of the preset to check

        Returns:
            True if option matches all criteria, False otherwise
        """
        preset = self.get_preset(preset_name)
        filters = preset['filters']

        # Extract option data
        delta = option_data.get('delta', 0)
        iv = option_data.get('iv', 0)
        intrinsic_pct = option_data.get('intrinsic_pct', 0)
        extrinsic_pct = option_data.get('extrinsic_pct', 1)
        dte = option_data.get('dte', 0)
        spread_pct = option_data.get('spread_pct', 1)
        oi = option_data.get('oi', 0)

        # Check all filter criteria
        matches = (
            filters['MIN_DELTA'] <= delta <= filters['MAX_DELTA'] and
            intrinsic_pct >= filters['MIN_INTRINSIC_PCT'] and
            extrinsic_pct <= filters['MAX_EXTRINSIC_PCT'] and
            filters['MIN_DTE'] <= dte <= filters['MAX_DTE'] and
            iv <= filters['MAX_IV'] and
            spread_pct <= filters['MAX_SPREAD_PCT'] and
            oi >= filters['MIN_OI']
        )

        return matches

    def check_all_preset_matches(self, option_data: Dict) -> List[str]:
        """
        Check which filter presets an option matches.

        Args:
            option_data: Dict with option metrics

        Returns:
            List of preset names that match this option
        """
        matched = []

        for preset_name in self.get_all_presets().keys():
            if self.check_preset_match(option_data, preset_name):
                matched.append(preset_name)

        return matched

    def get_preset_filters(self, preset_name: str) -> Dict:
        """Get the filter parameters for a specific preset."""
        preset = self.get_preset(preset_name)
        return preset['filters']

    def compare_option_to_preset(self, option_data: Dict, preset_name: str) -> Dict:
        """
        Compare an option against a preset and show which criteria pass/fail.

        Args:
            option_data: Dict with option metrics
            preset_name: Name of the preset to compare against

        Returns:
            Dict showing pass/fail for each criterion
        """
        preset = self.get_preset(preset_name)
        filters = preset['filters']

        # Extract option data
        delta = option_data.get('delta', 0)
        iv = option_data.get('iv', 0)
        intrinsic_pct = option_data.get('intrinsic_pct', 0)
        extrinsic_pct = option_data.get('extrinsic_pct', 1)
        dte = option_data.get('dte', 0)
        spread_pct = option_data.get('spread_pct', 1)
        oi = option_data.get('oi', 0)

        comparison = {
            'preset_name': preset_name,
            'overall_match': self.check_preset_match(option_data, preset_name),
            'criteria': {
                'delta': {
                    'value': delta,
                    'required': f"{filters['MIN_DELTA']}-{filters['MAX_DELTA']}",
                    'pass': filters['MIN_DELTA'] <= delta <= filters['MAX_DELTA']
                },
                'intrinsic_pct': {
                    'value': intrinsic_pct,
                    'required': f">={filters['MIN_INTRINSIC_PCT']}",
                    'pass': intrinsic_pct >= filters['MIN_INTRINSIC_PCT']
                },
                'extrinsic_pct': {
                    'value': extrinsic_pct,
                    'required': f"<={filters['MAX_EXTRINSIC_PCT']}",
                    'pass': extrinsic_pct <= filters['MAX_EXTRINSIC_PCT']
                },
                'dte': {
                    'value': dte,
                    'required': f"{filters['MIN_DTE']}-{filters['MAX_DTE']}",
                    'pass': filters['MIN_DTE'] <= dte <= filters['MAX_DTE']
                },
                'iv': {
                    'value': iv,
                    'required': f"<={filters['MAX_IV']}",
                    'pass': iv <= filters['MAX_IV']
                },
                'spread_pct': {
                    'value': spread_pct,
                    'required': f"<={filters['MAX_SPREAD_PCT']}",
                    'pass': spread_pct <= filters['MAX_SPREAD_PCT']
                },
                'open_interest': {
                    'value': oi,
                    'required': f">={filters['MIN_OI']}",
                    'pass': oi >= filters['MIN_OI']
                }
            }
        }

        return comparison

    def get_mismatch_reason(self, option_data: Dict, preset_name: str) -> str:
        """
        Get a user-friendly explanation of why an option doesn't match a preset.

        Args:
            option_data: Dict with option metrics
            preset_name: Name of the preset to check

        Returns:
            String explaining why the option doesn't match, or empty string if it matches
        """
        # If it matches, return empty string
        if self.check_preset_match(option_data, preset_name):
            return ""

        # Get detailed comparison
        comparison = self.compare_option_to_preset(option_data, preset_name)

        # Build list of failed criteria with explanations
        failures = []

        for criterion, details in comparison['criteria'].items():
            if not details['pass']:
                value = details['value']
                required = details['required']

                # Format criterion name for display
                criterion_display = {
                    'delta': 'Delta',
                    'intrinsic_pct': 'Intrinsic %',
                    'extrinsic_pct': 'Extrinsic %',
                    'dte': 'Days to Expiration',
                    'iv': 'Implied Volatility',
                    'spread_pct': 'Bid-Ask Spread %',
                    'open_interest': 'Open Interest'
                }.get(criterion, criterion)

                # Format value based on criterion type
                if criterion in ['intrinsic_pct', 'extrinsic_pct', 'spread_pct', 'iv']:
                    value_str = f"{value*100:.2f}%"
                elif criterion == 'delta':
                    value_str = f"{value:.3f}"
                elif criterion in ['dte', 'open_interest']:
                    value_str = f"{int(value)}"
                else:
                    value_str = f"{value:.4f}"

                # Build explanation
                explanation = f"{criterion_display}: {value_str} (required: {required})"
                failures.append(explanation)

        # Join all failures with semicolons
        return "; ".join(failures)


# Convenience function for quick matching
def check_preset_matches(option_data: Dict, presets_path: str = "./filter_presets.json") -> List[str]:
    """
    Quick function to check which presets match an option.

    Args:
        option_data: Dict with delta, iv, intrinsic_pct, etc.
        presets_path: Path to filter_presets.json

    Returns:
        List of preset names that match
    """
    matcher = FilterMatcher(presets_path)
    return matcher.check_all_preset_matches(option_data)


if __name__ == "__main__":
    # Example usage
    matcher = FilterMatcher()

    # Test option data
    test_option = {
        'delta': 0.85,
        'iv': 0.22,
        'intrinsic_pct': 0.85,
        'extrinsic_pct': 0.15,
        'dte': 30,
        'spread_pct': 0.012,
        'oi': 750
    }

    print("Testing option against all presets:")
    print("=" * 60)
    print(f"Delta: {test_option['delta']}")
    print(f"IV: {test_option['iv']*100}%")
    print(f"Intrinsic: {test_option['intrinsic_pct']*100}%")
    print(f"Extrinsic: {test_option['extrinsic_pct']*100}%")
    print(f"DTE: {test_option['dte']}")
    print(f"Spread: {test_option['spread_pct']*100}%")
    print(f"OI: {test_option['oi']}")
    print("=" * 60)

    matched = matcher.check_all_preset_matches(test_option)
    print(f"\nMatches {len(matched)} presets: {', '.join(matched)}")

    # Show detailed comparison for each preset
    for preset_name in matcher.get_all_presets().keys():
        print(f"\n{preset_name.upper()}:")
        comparison = matcher.compare_option_to_preset(test_option, preset_name)
        for criterion, details in comparison['criteria'].items():
            status = "✓" if details['pass'] else "✗"
            print(f"  {status} {criterion}: {details['value']:.4f} (required: {details['required']})")
