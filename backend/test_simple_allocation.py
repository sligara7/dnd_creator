#!/usr/bin/env python3
"""
Test simple allocation with the new AllocationService
"""

import sys
import os
sys.path.append('.')

import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def test_simple_allocation():
    """Test simple allocation using known character and item IDs."""
    
    session = requests.Session()
    
    # First get any existing character
    print("1. Getting existing characters...")
    list_response = session.get(f"{BASE_URL}/api/v2/characters")
    if list_response.status_code != 200:
        print(f"❌ Failed to get characters: {list_response.text}")
        return False
    
    characters = list_response.json()
    if not characters:
        print("❌ No characters found")
        return False
    
    character_id = characters[0]["id"]
    print(f"✅ Using character: {character_id} ({characters[0]['name']})")
    
    # Get any item from catalog
    print("\n2. Getting items from catalog...")
    catalog_response = session.post(f"{BASE_URL}/api/v2/catalog/search", json={
        "item_type": "spell",
        "limit": 5
    })
    
    if catalog_response.status_code != 200:
        print(f"❌ Failed to search catalog: {catalog_response.text}")
        return False
    
    items = catalog_response.json()["data"]["items"]
    if not items:
        print("❌ No items found in catalog")
        return False
    
    item = items[0]
    item_id = item["id"]
    print(f"✅ Using item: {item_id} ({item['name']})")
    
    # Try allocation
    print("\n3. Testing allocation...")
    alloc_data = {
        "character_id": character_id,
        "item_id": item_id,
        "access_type": "inventory",
        "acquired_method": "Test allocation",
        "skip_validation": True  # Skip validation for this test
    }
    
    alloc_response = session.post(f"{BASE_URL}/api/v2/catalog/access", json=alloc_data)
    
    if alloc_response.status_code == 200:
        result = alloc_response.json()
        print(f"✅ Allocation successful: {result}")
        
        # Test getting character items
        print("\n4. Testing character items retrieval...")
        items_response = session.get(f"{BASE_URL}/api/v2/catalog/character/{character_id}/items")
        if items_response.status_code == 200:
            items_result = items_response.json()
            print(f"✅ Character items retrieved successfully!")
            print(f"Response structure: {list(items_result.get('data', {}).keys())}")
            return True
        else:
            print(f"❌ Failed to get character items: {items_response.text}")
            return False
    else:
        print(f"❌ Allocation failed: {alloc_response.status_code} - {alloc_response.text}")
        return False

if __name__ == "__main__":
    test_simple_allocation()
