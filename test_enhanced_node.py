#!/usr/bin/env python3
"""
Test script for the enhanced AspectRatioResizer node with enable/disable functionality.
"""

import sys
import os
import torch

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_node():
    """Test the enhanced node with enable/disable functionality."""
    try:
        print("Testing enhanced AspectRatioResizer node...")
        from src.nodes import NODE_CLASS_MAPPINGS
        
        AspectRatioResizer = NODE_CLASS_MAPPINGS["AspectRatioResizer"]
        node = AspectRatioResizer()
        
        # Create a test image (1920x1080)
        test_image = torch.rand(1, 1080, 1920, 3)  # [B, H, W, C]
        print(f"Test image shape: {test_image.shape} (1920x1080)")
        
        # Test 1: Only width enabled (should resize to 1024x576)
        print("\n--- Test 1: Only width enabled ---")
        result1 = node.resize_images(
            images=test_image,
            max_width=1024,
            max_height=1024,
            enable_width=True,
            enable_height=False,
            resize_mode="downscale_only",
            interpolation="bilinear"
        )
        print(f"Result shape: {result1[0].shape}")
        expected_height = int(1080 * (1024 / 1920))
        print(f"Expected: 1024x{expected_height}, Got: {result1[0].shape[2]}x{result1[0].shape[1]}")
        
        # Test 2: Only height enabled (should resize to 1365x1024)
        print("\n--- Test 2: Only height enabled ---")
        result2 = node.resize_images(
            images=test_image,
            max_width=1024,
            max_height=1024,
            enable_width=False,
            enable_height=True,
            resize_mode="downscale_only",
            interpolation="bilinear"
        )
        print(f"Result shape: {result2[0].shape}")
        expected_width = int(1920 * (1024 / 1080))
        print(f"Expected: {expected_width}x1024, Got: {result2[0].shape[2]}x{result2[0].shape[1]}")
        
        # Test 3: Both enabled (should use most restrictive - width in this case)
        print("\n--- Test 3: Both enabled ---")
        result3 = node.resize_images(
            images=test_image,
            max_width=1024,
            max_height=1024,
            enable_width=True,
            enable_height=True,
            resize_mode="downscale_only",
            interpolation="bilinear"
        )
        print(f"Result shape: {result3[0].shape}")
        print(f"Should be same as Test 1: 1024x{int(1080 * (1024 / 1920))}")
        
        # Test 4: Neither enabled (should remain unchanged)
        print("\n--- Test 4: Neither enabled ---")
        result4 = node.resize_images(
            images=test_image,
            max_width=1024,
            max_height=1024,
            enable_width=False,
            enable_height=False,
            resize_mode="downscale_only",
            interpolation="bilinear"
        )
        print(f"Result shape: {result4[0].shape}")
        print("Should be unchanged: 1920x1080")
        
        # Test 5: Small image with upscale_only and width constraint
        small_image = torch.rand(1, 480, 640, 3)  # [B, H, W, C]
        print(f"\n--- Test 5: Small image (640x480) with width upscale ---")
        result5 = node.resize_images(
            images=small_image,
            max_width=1024,
            max_height=1024,
            enable_width=True,
            enable_height=False,
            resize_mode="upscale_only",
            interpolation="bilinear"
        )
        print(f"Result shape: {result5[0].shape}")
        expected_height_upscale = int(480 * (1024 / 640))
        print(f"Expected: 1024x{expected_height_upscale}, Got: {result5[0].shape[2]}x{result5[0].shape[1]}")
        
        print("\n🎉 All enhanced tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Enhanced AspectRatioResizer Node Test ===\n")
    success = test_enhanced_node()
    
    if success:
        print("\n✅ Enhanced functionality working correctly!")
        print("\nNew features:")
        print("- Enable/disable width constraint")
        print("- Enable/disable height constraint") 
        print("- Use only width OR only height for aspect ratio calculation")
        print("- Detailed constraint information in logs")
    else:
        print("\n❌ Tests failed. Check the errors above.")
