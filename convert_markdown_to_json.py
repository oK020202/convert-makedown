#!/usr/bin/env python3
"""
Script to convert the Markdown table in README.md to structured JSON format.
"""

import re
import json
from typing import List, Dict, Any, Optional


STATUS_MAPPING = {
    "✅": "full_adoption",
    "🌀": "partial_adoption",
    "❓": "unconfirmed",
    "": "not_adopted"
}


def parse_official_sources(official_info: str) -> List[Dict[str, Optional[str]]]:
    """
    Parse the official information column to extract descriptions and URLs.

    Args:
        official_info: Raw text from the 公式情報 column

    Returns:
        List of dictionaries with 'description' and 'url' keys
    """
    if not official_info or official_info.strip() == "":
        return []

    sources = []

    parts = re.split(r'<br\s*/?>', official_info)

    for part in parts:
        part = part.strip()
        if not part:
            continue

        markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', part)

        if markdown_links:
            for text, url in markdown_links:
                sources.append({
                    "description": text.strip(),
                    "url": url.strip()
                })
            part_without_links = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', '', part).strip()
            if part_without_links and part_without_links not in ['', '（）', '()']:
                part_without_links = re.sub(r'^\（|\）$', '', part_without_links).strip()
                if part_without_links:
                    sources.append({
                        "description": part_without_links,
                        "url": None
                    })
        else:
            clean_part = re.sub(r'^\（|\）$', '', part).strip()
            if clean_part:
                sources.append({
                    "description": clean_part,
                    "url": None
                })

    return sources


def map_status(emoji: str) -> str:
    """
    Map emoji status indicators to text values.

    Args:
        emoji: The emoji or text from the table cell

    Returns:
        Mapped status string
    """
    emoji = emoji.strip()
    return STATUS_MAPPING.get(emoji, "not_adopted")


def parse_markdown_table(readme_content: str) -> List[Dict[str, Any]]:
    """
    Parse the markdown table from README.md content.

    Args:
        readme_content: Full content of the README.md file

    Returns:
        List of company dictionaries
    """
    companies = []

    lines = readme_content.split('\n')

    table_start = -1
    for i, line in enumerate(lines):
        if '**会社名**' in line and '**Cursor**' in line:
            table_start = i
            break

    if table_start == -1:
        raise ValueError("Could not find table header in README.md")

    data_start = table_start + 2

    for i in range(data_start, len(lines)):
        line = lines[i].strip()

        if not line or not line.startswith('|'):
            continue

        if '---' in line or line.startswith('|**注:**') or 'チェックマーク' in line:
            continue

        cells = [cell.strip() for cell in line.split('|')]

        if len(cells) < 8:
            continue

        company_name = cells[1].strip()
        cursor_status = cells[2].strip()
        devin_status = cells[3].strip()
        copilot_status = cells[4].strip()
        chatgpt_status = cells[5].strip()
        claude_status = cells[6].strip()
        official_info = cells[7].strip()

        if not company_name or company_name.startswith('**') or company_name == '':
            continue

        official_sources = parse_official_sources(official_info)

        company = {
            "name": company_name,
            "tools": {
                "cursor": map_status(cursor_status),
                "devin": map_status(devin_status),
                "github_copilot": map_status(copilot_status),
                "chatgpt": map_status(chatgpt_status),
                "claude_code": map_status(claude_status)
            },
            "official_sources": official_sources
        }

        companies.append(company)

    return companies


def main():
    """Main function to convert README.md to JSON."""

    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            readme_content = f.read()
    except FileNotFoundError:
        print("Error: README.md file not found")
        return
    except Exception as e:
        print(f"Error reading README.md: {e}")
        return

    try:
        companies = parse_markdown_table(readme_content)
        print(f"Successfully parsed {len(companies)} companies")
    except Exception as e:
        print(f"Error parsing markdown table: {e}")
        return

    output_data = {
        "companies": companies,
        "status_mapping": STATUS_MAPPING
    }

    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print("Successfully wrote data.json")
        print(f"Total companies: {len(companies)}")

        tool_stats = {}
        for tool in ["cursor", "devin", "github_copilot", "chatgpt", "claude_code"]:
            stats = {}
            for company in companies:
                status = company["tools"][tool]
                stats[status] = stats.get(status, 0) + 1
            tool_stats[tool] = stats

        print("\nTool adoption statistics:")
        for tool, stats in tool_stats.items():
            print(f"  {tool}: {stats}")

    except Exception as e:
        print(f"Error writing data.json: {e}")
        return


if __name__ == "__main__":
    main()
