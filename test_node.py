#!/usr/bin/env python3
"""
Test script to verify the AspectRatioResizer node can be imported and initialized.
Run this script to check if there are any import or initialization errors.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_node_import():
    """Test if the node can be imported successfully."""
    try:
        print("Testing node import...")
        from src.nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
        print("✓ Successfully imported NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS")
        
        print(f"Available nodes: {list(NODE_CLASS_MAPPINGS.keys())}")
        print(f"Display names: {NODE_DISPLAY_NAME_MAPPINGS}")
        
        # Test node class
        AspectRatioResizer = NODE_CLASS_MAPPINGS["AspectRatioResizer"]
        print("✓ Successfully got AspectRatioResizer class")
        
        # Test INPUT_TYPES method
        input_types = AspectRatioResizer.INPUT_TYPES()
        print("✓ Successfully called INPUT_TYPES()")
        print(f"Input types: {input_types}")
        
        # Test node instantiation
        node = AspectRatioResizer()
        print("✓ Successfully created node instance")
        
        print("\n🎉 All tests passed! The node should work in ComfyUI.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_init():
    """Test if the main __init__.py works."""
    try:
        print("\nTesting main __init__.py...")
        import __init__ as main_init
        
        # Check if required attributes exist
        if hasattr(main_init, 'NODE_CLASS_MAPPINGS'):
            print("✓ NODE_CLASS_MAPPINGS found in __init__.py")
        else:
            print("❌ NODE_CLASS_MAPPINGS not found in __init__.py")
            
        if hasattr(main_init, 'NODE_DISPLAY_NAME_MAPPINGS'):
            print("✓ NODE_DISPLAY_NAME_MAPPINGS found in __init__.py")
        else:
            print("❌ NODE_DISPLAY_NAME_MAPPINGS not found in __init__.py")
            
        if hasattr(main_init, 'WEB_DIRECTORY'):
            print("✓ WEB_DIRECTORY found in __init__.py")
        else:
            print("❌ WEB_DIRECTORY not found in __init__.py")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing __init__.py: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== AspectRatioResizer Node Test ===\n")
    
    success1 = test_node_import()
    success2 = test_main_init()
    
    if success1 and success2:
        print("\n✅ All tests passed!")
        print("\nTo use this node in ComfyUI:")
        print("1. Copy this entire folder to ComfyUI/custom_nodes/")
        print("2. Restart ComfyUI")
        print("3. Look for 'Aspect Ratio Resizer' in the 'image/resize' category")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
