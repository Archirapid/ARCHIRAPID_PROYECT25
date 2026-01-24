#!/usr/bin/env python3
"""
Test script to verify the marketplace fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_marketplace():
    print("Testing marketplace functionality...")

    # Test imports
    try:
        import app
        print("✓ App imported successfully")
    except Exception as e:
        print(f"✗ App import failed: {e}")
        return False

    try:
        from src import db
        from modules.marketplace.marketplace import get_project_display_image
        print("✓ Database and marketplace modules imported")
    except Exception as e:
        print(f"✗ Module import failed: {e}")
        return False

    # Test get_featured_projects
    try:
        projects = db.get_featured_projects(limit=3)
        print(f"✓ Found {len(projects)} projects")
    except Exception as e:
        print(f"✗ get_featured_projects failed: {e}")
        return False

    # Test image detection for each project
    for p in projects:
        title = p.get('title', 'No title')
        print(f"  Project {p['id']}: {title}")

        try:
            main_img = get_project_display_image(p['id'], 'main')
            gallery_imgs = get_project_display_image(p['id'], 'gallery')
            print(f"    ✓ Main: {main_img}")
            print(f"    ✓ Gallery: {len(gallery_imgs) if gallery_imgs else 0} images")
        except Exception as e:
            print(f"    ✗ Image detection failed: {e}")
            return False

    print("✓ All tests passed!")
    return True

if __name__ == "__main__":
    success = test_marketplace()
    sys.exit(0 if success else 1)