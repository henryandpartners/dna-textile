#!/usr/bin/env python3
"""Test script to list communities and motifs."""

import sys
sys.path.insert(0, 'src')

from cultural_rules import get_community_rules

# List all communities
communities = [
    'karen', 'hmong', 'akha', 'lahu', 'lisu', 'mien',
    'palaung', 'khamu', 'lua', 'mlabri', 'mani',
    'moklen', 'urak_lawoi', 'thai_lue', 'tai_dam'
]

print("Available Communities:")
for comm in communities:
    try:
        rules = get_community_rules(comm)
        print(f"  ✓ {comm} ({rules.name})")
    except Exception as e:
        print(f"  ✗ {comm}: {e}")

print("\nDone!")
