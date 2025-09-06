#!/usr/bin/env python3
"""Update service documentation with standardized Message Hub requirements."""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Base paths
BASE_DIR = Path('/home/ajs7/dnd_tools/dnd_char_creator')
SRD_DIR = BASE_DIR / 'requirements' / 'srd'
ICD_DIR = BASE_DIR / 'requirements' / 'icd'

# Template for Core Principles section in SRDs
SRD_CORE_PRINCIPLES_TEMPLATE = """### 1.2 Core Principles
- {service_specific_purpose}
- All inter-service communication MUST go through Message Hub
- No direct service-to-service communication allowed
- Service isolation and independence
- Event-driven architecture
"""

# Template for Communication Architecture section in ICDs
ICD_COMM_ARCH_TEMPLATE = """## 1. Communication Architecture

### 1.1 Service Communication Pattern
- All service-to-service communication MUST be routed through the Message Hub service
- No direct HTTP calls between services are permitted
- All integrations must use asynchronous messaging patterns
- All events and requests must include proper correlation IDs

### 1.2 Base URL (API Gateway Access Only)
```http
http://{service_name}:{port}  # Only accessible via API Gateway
```

### 1.3 Message Hub Protocol
- Every request/event must include:
  * Correlation ID (for tracing)
  * Source service identifier
  * Request/event type and version
  * Timestamp
  * TTL (time-to-live)

### 1.4 Common Headers
"""

# Service-specific details
SERVICE_DETAILS = {
    'api_gateway': {
        'purpose': 'Single public entry point for the entire system',
        'port': 8080
    },
    'llm': {
        'purpose': 'Provide centralized LLM operations for all services',
        'port': 8100
    },
    'character': {
        'purpose': 'Manage character creation and evolution',
        'port': 8000
    },
    'campaign': {
        'purpose': 'Manage campaign creation and story development',
        'port': 8001
    },
    'image': {
        'purpose': 'Provide AI-powered image generation and management',
        'port': 8002
    },
    'auth': {
        'purpose': 'Handle authentication and authorization',
        'port': 8300
    },
    'cache': {
        'purpose': 'Provide distributed caching capabilities',
        'port': 8400
    },
    'catalog': {
        'purpose': 'Manage unified content catalog',
        'port': 8500
    },
    'search': {
        'purpose': 'Provide search capabilities across services',
        'port': 8600
    },
    'storage': {
        'purpose': 'Handle binary asset storage and management',
        'port': 8700
    },
    'audit': {
        'purpose': 'Track and log system activities',
        'port': 8800
    },
    'metrics': {
        'purpose': 'Collect and analyze system metrics',
        'port': 8900
    }
}

def get_service_name(file_path: str) -> str:
    """Extract service name from file path."""
    file_name = Path(file_path).name
    # Remove SRD_ or ICD_ prefix and .md extension
    return file_name[4:-3].lower()

def update_srd_core_principles(content: str, service_name: str) -> str:
    """Update SRD core principles section."""
    service_details = SERVICE_DETAILS.get(service_name, {'purpose': 'Provide service-specific functionality'})
    new_principles = SRD_CORE_PRINCIPLES_TEMPLATE.format(
        service_specific_purpose=service_details['purpose']
    )
    
    # Look for existing Core Principles section
    if '### 1.2 Core Principles' in content:
        # Replace existing section
        pattern = r'### 1\.2 Core Principles\n(?:- .*\n)*'
        content = re.sub(pattern, new_principles, content)
    elif '### 1.2 Core Mission' in content:
        # Replace Core Mission with Core Principles
        pattern = r'### 1\.2 Core Mission\n(?:- .*\n)*'
        content = re.sub(pattern, new_principles, content)
    else:
        # Add after Purpose section
        pattern = r'### 1\.1 Purpose\n(?:.*\n)*?\n'
        content = re.sub(pattern, lambda m: m.group(0) + new_principles, content)
    
    return content

def update_icd_communication(content: str, service_name: str) -> str:
    """Update ICD communication architecture section."""
    service_details = SERVICE_DETAILS.get(service_name, {'port': 8000})
    new_comm_arch = ICD_COMM_ARCH_TEMPLATE.format(
        service_name=service_name.replace('_', '-'),
        port=service_details['port']
    )
    
    # Look for existing Service Interface section
    if '## 1. Service Interface' in content:
        pattern = r'## 1\. Service Interface\n(?:.*\n)*?(?=##)'
        content = re.sub(pattern, new_comm_arch, content)
    else:
        # Add after version information
        pattern = r'Version: .*\nStatus: .*\nLast Updated: .*\n\n'
        content = re.sub(pattern, lambda m: m.group(0) + new_comm_arch, content)
    
    return content

def update_file(file_path: str, is_srd: bool) -> None:
    """Update a single documentation file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    service_name = get_service_name(file_path)
    
    if is_srd:
        content = update_srd_core_principles(content, service_name)
    else:
        content = update_icd_communication(content, service_name)
    
    with open(file_path, 'w') as f:
        f.write(content)

def get_doc_files() -> Tuple[List[str], List[str]]:
    """Get lists of SRD and ICD files."""
    srd_files = list(SRD_DIR.glob('SRD_*.md'))
    icd_files = list(ICD_DIR.glob('ICD_*.md'))
    return srd_files, icd_files

def main() -> None:
    """Update all service documentation with Message Hub requirements."""
    srd_files, icd_files = get_doc_files()
    
    print("Updating SRDs...")
    for file_path in srd_files:
        print(f"Processing {file_path.name}")
        update_file(str(file_path), True)
    
    print("\nUpdating ICDs...")
    for file_path in icd_files:
        print(f"Processing {file_path.name}")
        update_file(str(file_path), False)
    
    print("\nAll documentation updated with standardized Message Hub requirements.")

if __name__ == '__main__':
    main()
