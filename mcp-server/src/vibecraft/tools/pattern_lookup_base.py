"""
Base Pattern Lookup Handler

Generic pattern lookup logic shared by building and terrain pattern handlers.
Eliminates 400+ lines of duplicate code.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from mcp.types import TextContent

logger = logging.getLogger(__name__)


class PatternLookupHandler:
    """
    Generic handler for pattern lookup operations.

    Supports: browse, categories, subcategories, tags, search, get actions.
    Used by both building and terrain pattern lookup tools.
    """

    def __init__(
        self,
        patterns_file: Path,
        emoji_prefix: str,
        category_name: str,
        logger_instance: logging.Logger,
        has_structure_check: Optional[Callable[[str], bool]] = None,
    ):
        """
        Initialize pattern lookup handler.

        Args:
            patterns_file: Path to JSON file with patterns
            emoji_prefix: Emoji to prefix output (e.g., "🏗️" or "🌲")
            category_name: Display name (e.g., "Building" or "Terrain")
            logger_instance: Logger instance
            has_structure_check: Optional function to check if pattern has structured placement
        """
        self.patterns_file = patterns_file
        self.emoji_prefix = emoji_prefix
        self.category_name = category_name
        self.logger = logger_instance
        self.has_structure_check = has_structure_check
        self.patterns = []

    def load_patterns(self) -> List[TextContent]:
        """
        Load patterns from JSON file.

        Returns:
            List of TextContent with error if loading fails, empty list if success
        """
        if not self.patterns_file.exists():
            self.logger.warning(f"Pattern file not found: {self.patterns_file}")
            return [
                TextContent(
                    type="text", text=f"❌ Error: {self.category_name} patterns file not found"
                )
            ]

        try:
            with open(self.patterns_file, "r") as f:
                data = json.load(f)

                # Handle both array format and object format
                if isinstance(data, list):
                    self.patterns = data
                elif isinstance(data, dict):
                    if "patterns" in data:
                        patterns_dict = data["patterns"]
                        self.patterns = list(patterns_dict.values())
                    else:
                        self.patterns = list(data.values())

        except Exception as e:
            self.logger.warning(f"Could not load patterns: {str(e)}")
            return [
                TextContent(
                    type="text",
                    text=f"❌ Error loading {self.category_name.lower()} patterns: {str(e)}",
                )
            ]

        if not self.patterns:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Error: No {self.category_name.lower()} pattern metadata available.",
                )
            ]

        return []  # Success - no error

    def action_browse(self) -> List[TextContent]:
        """List all patterns (names and IDs only)."""
        result_text = f"{self.emoji_prefix} **{self.category_name} Pattern Library** - {len(self.patterns)} patterns available\n\n"

        # Group by category
        by_category = {}
        for pattern in self.patterns:
            cat = pattern.get("category", "unknown")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(pattern)

        for category, cat_patterns in sorted(by_category.items()):
            result_text += f"**{category.upper()}** ({len(cat_patterns)} patterns):\n"
            for pattern in sorted(cat_patterns, key=lambda p: p.get("id", "")):
                pattern_id = pattern.get("id")
                structured_flag = ""
                if self.has_structure_check and pattern_id:
                    if self.has_structure_check(pattern_id):
                        structured_flag = " ✅"
                result_text += f"  - {pattern.get('name')} (ID: `{pattern_id}`){structured_flag}\n"
            result_text += "\n"

        if self.has_structure_check:
            result_text += "✅ indicates structured placement data is available.\n"
        result_text += "💡 Use action='get' with pattern_id to retrieve full construction details."

        return [TextContent(type="text", text=result_text)]

    def action_categories(self) -> List[TextContent]:
        """List all categories with counts."""
        category_counts = {}
        category_subcats = {}

        for pattern in self.patterns:
            cat = pattern.get("category", "unknown")
            subcat = pattern.get("subcategory", "")

            category_counts[cat] = category_counts.get(cat, 0) + 1

            if cat not in category_subcats:
                category_subcats[cat] = set()
            if subcat:
                category_subcats[cat].add(subcat)

        result_text = f"{self.emoji_prefix} **{self.category_name} Pattern Categories**\n\n"

        for category in sorted(category_counts.keys()):
            count = category_counts[category]
            subcats = sorted(category_subcats.get(category, set()))

            result_text += f"**{category}** ({count} patterns)\n"
            if subcats:
                result_text += f"  Subcategories: {', '.join(subcats)}\n"
            result_text += "\n"

        result_text += "💡 Use action='subcategories' with category='<name>' to see patterns in that category.\n"
        result_text += "💡 Use action='search' with category='<name>' to find patterns."

        if self.has_structure_check:
            result_text += (
                "\n✅ Structured patterns can be placed automatically with place_building_pattern."
            )

        return [TextContent(type="text", text=result_text)]

    def action_subcategories(self, category: str) -> List[TextContent]:
        """List subcategories for a specific category."""
        if not category:
            return [
                TextContent(
                    type="text",
                    text="❌ Error: 'category' parameter required for action='subcategories'",
                )
            ]

        category = category.lower()

        # Find patterns in this category
        cat_patterns = [p for p in self.patterns if p.get("category", "").lower() == category]

        if not cat_patterns:
            return [
                TextContent(
                    type="text",
                    text=f"❌ No patterns found in category '{category}'. Use action='categories' to see available categories.",
                )
            ]

        # Group by subcategory
        by_subcat = {}
        for pattern in cat_patterns:
            subcat = pattern.get("subcategory", "none")
            if subcat not in by_subcat:
                by_subcat[subcat] = []
            by_subcat[subcat].append(pattern)

        result_text = f"{self.emoji_prefix} **{category.upper()} Category** - {len(cat_patterns)} patterns\n\n"

        for subcat, subcat_patterns in sorted(by_subcat.items()):
            result_text += f"**{subcat}** ({len(subcat_patterns)} patterns):\n"
            for pattern in sorted(subcat_patterns, key=lambda p: p.get("id", "")):
                dims = pattern.get("dimensions", {})
                size = f"{dims.get('width')}×{dims.get('height')}×{dims.get('depth')}"
                result_text += f"  - {pattern.get('name')} (ID: `{pattern.get('id')}`) - {size}\n"
            result_text += "\n"

        result_text += "💡 Use action='get' with pattern_id to retrieve full construction details."

        return [TextContent(type="text", text=result_text)]

    def action_tags(self) -> List[TextContent]:
        """List all tags with usage counts."""
        tag_counts = {}

        for pattern in self.patterns:
            for tag in pattern.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        result_text = f"{self.emoji_prefix} **{self.category_name} Pattern Tags**\n\n"

        # Sort by count (most used first)
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

        for tag, count in sorted_tags:
            result_text += f"- **{tag}** ({count} patterns)\n"

        result_text += (
            "\n💡 Use action='search' with tags=['<tag>'] to find patterns with specific tags."
        )

        return [TextContent(type="text", text=result_text)]

    def action_search(
        self,
        query: str = "",
        category_filter: str = "",
        subcategory_filter: str = "",
        tags_filter: List[str] = None,
    ) -> List[TextContent]:
        """Search for patterns by query, category, subcategory, or tags."""
        if tags_filter is None:
            tags_filter = []

        query = query.lower()
        category_filter = category_filter.lower()
        subcategory_filter = subcategory_filter.lower()
        tags_filter = [tag.lower() for tag in tags_filter]

        results = []

        for pattern in self.patterns:
            # Check if matches search criteria
            matches = True

            if query:
                # Search in name, id, category, subcategory, description, and tags
                name_match = query in pattern.get("name", "").lower()
                id_match = query in pattern.get("id", "").lower()
                cat_match = query in pattern.get("category", "").lower()
                subcat_match = query in pattern.get("subcategory", "").lower()
                desc_match = query in pattern.get("description", "").lower()
                tags_match = any(query in tag.lower() for tag in pattern.get("tags", []))

                matches = matches and (
                    name_match or id_match or cat_match or subcat_match or desc_match or tags_match
                )

            if category_filter:
                matches = matches and (category_filter in pattern.get("category", "").lower())

            if subcategory_filter:
                matches = matches and (subcategory_filter in pattern.get("subcategory", "").lower())

            if tags_filter:
                pattern_tags = [tag.lower() for tag in pattern.get("tags", [])]
                # Check if ALL filter tags are present
                matches = matches and all(tag in pattern_tags for tag in tags_filter)

            if matches:
                # Add to results (summary only, not full pattern)
                dims = pattern.get("dimensions", {})
                pattern_id = pattern.get("id")

                result_item = {
                    "name": pattern.get("name"),
                    "id": pattern_id,
                    "category": pattern.get("category"),
                    "subcategory": pattern.get("subcategory"),
                    "tags": pattern.get("tags", []),
                    "dimensions": f"{dims.get('width')}×{dims.get('height')}×{dims.get('depth')}",
                    "difficulty": pattern.get("difficulty", "medium"),
                    "materials_count": sum(pattern.get("materials", {}).values()),
                    "layer_count": len(pattern.get("layers", [])),
                    "description": (
                        pattern.get("description", "")[:150] + "..."
                        if len(pattern.get("description", "")) > 150
                        else pattern.get("description", "")
                    ),
                }

                if self.has_structure_check and pattern_id:
                    result_item["has_structure"] = self.has_structure_check(pattern_id)

                results.append(result_item)

        if not results:
            search_params = []
            if query:
                search_params.append(f"query='{query}'")
            if category_filter:
                search_params.append(f"category='{category_filter}'")
            if subcategory_filter:
                search_params.append(f"subcategory='{subcategory_filter}'")
            if tags_filter:
                search_params.append(f"tags={tags_filter}")

            return [
                TextContent(
                    type="text",
                    text=f"🔍 No {self.category_name.lower()} patterns found matching: {', '.join(search_params)}\n\nTry:\n- Broader search terms\n- Different category\n- Different subcategory\n- Fewer tag filters",
                )
            ]

        # Format results
        result_text = (
            f"{self.emoji_prefix} Found {len(results)} {self.category_name.lower()} pattern(s):\n\n"
        )

        for i, item in enumerate(results, 1):
            structured_flag = ""
            if self.has_structure_check and item.get("has_structure"):
                structured_flag = " ✅"

            result_text += f"{i}. **{item['name']}** (ID: `{item['id']}`){structured_flag}\n"
            result_text += f"   - Category: {item['category']}"
            if item.get("subcategory"):
                result_text += f" > {item['subcategory']}"
            result_text += "\n"
            result_text += f"   - Size: {item['dimensions']} blocks (W×H×D)\n"
            result_text += f"   - Materials: {item['materials_count']} total blocks\n"
            result_text += f"   - Layers: {item['layer_count']} construction layers\n"
            result_text += f"   - Difficulty: {item['difficulty']}\n"
            if item.get("tags"):
                result_text += f"   - Tags: {', '.join(item['tags'])}\n"
            if item.get("description"):
                result_text += f"   - Description: {item['description']}\n"
            result_text += "\n"

        if self.has_structure_check:
            result_text += "✅ indicates automatic placement data is available.\n"

        tool_name = (
            "building_pattern_lookup"
            if self.category_name == "Building"
            else "terrain_pattern_lookup"
        )
        result_text += f"💡 To get full construction instructions, use: {tool_name} with action='get' and pattern_id='<id>'"

        if self.has_structure_check:
            result_text += "\n💡 Use place_building_pattern to instantiate structured patterns."

        return [TextContent(type="text", text=result_text)]

    def action_get(self, pattern_id: str) -> List[TextContent]:
        """Get specific pattern by ID."""
        if not pattern_id:
            return [
                TextContent(
                    type="text",
                    text="❌ Error: 'pattern_id' parameter is required for action='get'",
                )
            ]

        # Find pattern
        pattern = None
        for item in self.patterns:
            if item.get("id") == pattern_id:
                pattern = item
                break

        if not pattern:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Error: Pattern with ID '{pattern_id}' not found.\n\nUse action='search' to find available patterns.",
                )
            ]

        # Format full pattern details
        result_text = (
            f"{self.emoji_prefix} **{pattern.get('name')}** (ID: `{pattern.get('id')}`)\n\n"
        )

        # Basic info
        result_text += f"**Category:** {pattern.get('category')}"
        if pattern.get("subcategory"):
            result_text += f" > {pattern.get('subcategory')}"
        result_text += "\n\n"

        result_text += (
            f"**Description:** {pattern.get('description', 'No description available.')}\n\n"
        )

        # Full pattern data as JSON
        result_text += "**Full Pattern Data (JSON):**\n```json\n"
        result_text += json.dumps(pattern, indent=2)
        result_text += "\n```\n\n"

        result_text += "💡 Use WorldEdit commands to build this pattern layer by layer at your desired location."

        return [TextContent(type="text", text=result_text)]

    def handle(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Main dispatch handler for all pattern lookup actions.

        Args:
            arguments: Tool arguments containing 'action' and action-specific parameters

        Returns:
            List of TextContent with results or errors
        """
        action = arguments.get("action")

        if not action:
            return [TextContent(type="text", text="❌ Error: 'action' parameter is required")]

        # Load patterns
        error = self.load_patterns()
        if error:
            return error

        # Dispatch to action handler
        if action == "browse":
            return self.action_browse()

        elif action == "categories":
            return self.action_categories()

        elif action == "subcategories":
            category = arguments.get("category", "")
            return self.action_subcategories(category)

        elif action == "tags":
            return self.action_tags()

        elif action == "search":
            query = arguments.get("query", "")
            category_filter = arguments.get("category", "")
            subcategory_filter = arguments.get("subcategory", "")
            tags_filter = arguments.get("tags", [])
            return self.action_search(query, category_filter, subcategory_filter, tags_filter)

        elif action == "get":
            pattern_id = arguments.get("pattern_id", "")
            return self.action_get(pattern_id)

        else:
            valid_actions = "browse, categories, subcategories, tags, search, get"
            return [
                TextContent(
                    type="text",
                    text=f"❌ Invalid action: '{action}'. Must be one of: {valid_actions}",
                )
            ]
