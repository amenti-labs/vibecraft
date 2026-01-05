#!/usr/bin/env python3
"""
Pytest tests for Minecraft item search functionality.

Converted from: test_search.py (manual script)

Note: Import paths are configured via conftest.py
"""

import pytest
from vibecraft.minecraft_items_loader import minecraft_items


def search_items(query: str, limit: int = 20) -> list:
    """
    Search for Minecraft items by name or display name.

    Args:
        query: Search term (case-insensitive)
        limit: Maximum number of results

    Returns:
        List of matching items
    """
    query = query.lower()
    matches = []

    for item in minecraft_items:
        if query in item.get("name", "").lower() or query in item.get("displayName", "").lower():
            matches.append(item)
            if len(matches) >= limit:
                break

    return matches


class TestMinecraftItemSearch:
    """Tests for Minecraft item search functionality"""

    def test_search_stone(self):
        """Test searching for 'stone' items"""
        matches = search_items("stone", limit=10)
        assert len(matches) > 0, "Should find stone items"
        assert len(matches) <= 10, "Should respect limit"

        # Verify all results contain 'stone' in name or display name
        for item in matches:
            name = item.get("name", "").lower()
            display = item.get("displayName", "").lower()
            assert "stone" in name or "stone" in display, f"Item {item} doesn't match 'stone'"

    def test_search_concrete(self):
        """Test searching for 'concrete' items"""
        matches = search_items("concrete", limit=10)
        assert len(matches) > 0, "Should find concrete items"

        # Verify results contain 'concrete'
        for item in matches:
            name = item.get("name", "").lower()
            display = item.get("displayName", "").lower()
            assert "concrete" in name or "concrete" in display

    def test_search_oak(self):
        """Test searching for 'oak' items"""
        matches = search_items("oak", limit=10)
        assert len(matches) > 0, "Should find oak items"

        # Oak planks, logs, etc. should be included
        for item in matches:
            name = item.get("name", "").lower()
            display = item.get("displayName", "").lower()
            assert "oak" in name or "oak" in display

    def test_search_red(self):
        """Test searching for 'red' items"""
        matches = search_items("red", limit=10)
        assert len(matches) > 0, "Should find red items"

        for item in matches:
            name = item.get("name", "").lower()
            display = item.get("displayName", "").lower()
            assert "red" in name or "red" in display

    def test_search_sword(self):
        """Test searching for 'sword' items"""
        matches = search_items("sword", limit=5)
        assert len(matches) > 0, "Should find sword items"
        assert len(matches) <= 5, "Should respect limit of 5"

        for item in matches:
            name = item.get("name", "").lower()
            display = item.get("displayName", "").lower()
            assert "sword" in name or "sword" in display

    def test_search_limit_respected(self):
        """Test that search limit is respected"""
        limit = 3
        matches = search_items("stone", limit=limit)
        assert len(matches) <= limit, f"Should return at most {limit} results"

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive"""
        lower_matches = search_items("stone", limit=5)
        upper_matches = search_items("STONE", limit=5)
        mixed_matches = search_items("StOnE", limit=5)

        # All should return the same results (case-insensitive)
        assert len(lower_matches) == len(upper_matches)
        assert len(lower_matches) == len(mixed_matches)

    def test_search_no_results(self):
        """Test searching for a term with no matches"""
        matches = search_items("xyznonexistent", limit=10)
        assert len(matches) == 0, "Should return empty list for no matches"

    def test_item_structure(self):
        """Test that returned items have expected structure"""
        matches = search_items("stone", limit=1)
        assert len(matches) > 0, "Should find at least one item"

        item = matches[0]
        assert "name" in item, "Item should have 'name' field"
        assert "displayName" in item, "Item should have 'displayName' field"
        assert "id" in item, "Item should have 'id' field"

        # Validate types
        assert isinstance(item["name"], str), "name should be string"
        assert isinstance(item["displayName"], str), "displayName should be string"
        assert isinstance(item["id"], int), "id should be integer"


if __name__ == "__main__":
    # Allow running directly with python
    pytest.main([__file__, "-v"])
