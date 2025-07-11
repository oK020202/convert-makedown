#!/usr/bin/env python3
"""
Script to convert the Markdown table in README.md to structured JSON format.
"""

import re
import json
from typing import Dict, List, Any, Optional


def parse_markdown_table(file_path: str) -> Dict[str, Any]:
    """Parse the markdown table and convert to JSON structure."""
    
    status_mapping = {
        "✅": "full_adoption",
        "🌀": "partial_adoption", 
        "❓": "unconfirmed",
        "": "not_adopted"
    }
    
    companies = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    table_started = False
    
    for line in lines:
        if '**会社名**' in line and '**Cursor**' in line:
            table_started = True
            continue
        
        if table_started and '---' in line:
            continue
            
        if table_started and line.strip().startswith('|') and '**会社名**' not in line and '---' not in line:
            row_content = line.strip()[1:]  # Remove leading |
            if row_content.endswith('|'):
                row_content = row_content[:-1]  # Remove trailing |
            row_data = row_content.split('|')
            
            if len(row_data) >= 6:  # Ensure we have at least the main columns
                company_name = row_data[0].strip()
                cursor_status = row_data[1].strip()
                devin_status = row_data[2].strip()
                copilot_status = row_data[3].strip()
                chatgpt_status = row_data[4].strip()
                claude_status = row_data[5].strip()
                official_info = row_data[6].strip() if len(row_data) > 6 else ""
                
                if not company_name:
                    continue
                
                tools = {
                    "cursor": status_mapping.get(cursor_status, "not_adopted"),
                    "devin": status_mapping.get(devin_status, "not_adopted"),
                    "github_copilot": status_mapping.get(copilot_status, "not_adopted"),
                    "chatgpt": status_mapping.get(chatgpt_status, "not_adopted"),
                    "claude_code": status_mapping.get(claude_status, "not_adopted")
                }
                
                official_sources = parse_official_sources(official_info)
                
                company_data = {
                    "name": company_name,
                    "tools": tools,
                    "official_sources": official_sources
                }
                
                companies.append(company_data)
    
    return {
        "companies": companies,
        "status_mapping": status_mapping
    }


def parse_official_sources(official_info: str) -> List[Dict[str, Optional[str]]]:
    """Parse the official information column to extract descriptions and URLs."""
    if not official_info or official_info == "":
        return []
    
    sources = []
    
    entries = re.split(r'<br\s*/?>', official_info)
    
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
            
        markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', entry)
        
        if markdown_links:
            for text, url in markdown_links:
                sources.append({
                    "description": text.strip(),
                    "url": url.strip()
                })
            entry_without_links = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', '', entry).strip()
            if entry_without_links and entry_without_links not in ['', '（）']:
                entry_without_links = re.sub(r'[（）()]', '', entry_without_links).strip()
                if entry_without_links:
                    sources.append({
                        "description": entry_without_links,
                        "url": None
                    })
        else:
            description = re.sub(r'^[（(]|[）)]$', '', entry).strip()
            if description:
                sources.append({
                    "description": description,
                    "url": None
                })
    
    return sources


def main():
    """Main function to convert README.md to JSON."""
    input_file = "README.md"
    output_file = "data.json"
    
    try:
        data = parse_markdown_table(input_file)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully converted {len(data['companies'])} companies to {output_file}")
        print(f"Status mapping: {data['status_mapping']}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
