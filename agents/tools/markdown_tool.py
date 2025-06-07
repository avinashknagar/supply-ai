from .base_tool import BaseTool
from typing import Dict, Any, List

class MarkdownTool(BaseTool):
    @property
    def name(self) -> str:
        return "markdown_converter"

    def run(self, data: Dict[str, Any], template_type: str = "order_analysis") -> str:
        if template_type == "order_analysis":
            return self._format_order_analysis(data)
        raise ValueError(f"Unknown template type: {template_type}")
    
    def _format_order_analysis(self, data: Dict[str, Any]) -> str:
        if data.get("status") == "error":
            return f"## Error\n\nError processing order: {data.get('error')}"

        output = []
        output.append("# Order Analysis Report")
        
        # Specifications section
        output.append("\n## Order Specifications")
        specs = data.get("order_specifications", {})
        output.extend(self._create_table(specs))

        # Matches section
        output.append("\n## Matching Results")
        matches = data.get("matching_results", [])
        if not matches:
            output.append("\n*No matches found in inventory.*")
        else:
            output.extend(self._format_matches(matches))

        # AI Analysis section
        if data.get("ai_analysis"):
            output.append("\n## AI Supervisor Analysis")
            output.append(data.get("ai_analysis"))

        output.append(f"\n---\n*Report generated at: {data.get('processed_at', 'N/A')}*")
        return "\n".join(output)

    def _create_table(self, data: Dict[str, Any]) -> List[str]:
        """Helper method to create markdown tables"""
        lines = []
        lines.append("| Parameter | Value |")
        lines.append("|-----------|-------|")
        for key, value in data.items():
            lines.append(f"| {key.replace('_', ' ').title()} | {value} |")
        return lines
    
    def _format_matches(self, matches: List[Dict[str, Any]]) -> List[str]:
        """Helper method to format match results"""
        lines = []
        for idx, match in enumerate(matches[:3], 1):
            lines.append(f"\n### Match #{idx}")
            lines.append(f"\n**Match Score:** {match.get('match_score', 0)}%")
            lines.extend(self._create_table(match.get('inventory_item', {})))
        return lines
