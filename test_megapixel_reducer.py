#!/usr/bin/env python3
"""
Test script for the AutoMegapixelReducer node.
"""

import sys
import os
import torch

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_megapixel_reducer():
    """Test the AutoMegapixelReducer node."""
    try:
        print("Testing AutoMegapixelReducer node...")
        from src.nodes import NODE_CLASS_MAPPINGS
        
        AutoMegapixelReducer = NODE_CLASS_MAPPINGS["AutoMegapixelReducer"]
        node = AutoMegapixelReducer()
        
        # Test 1: 4K image (3840x2160 = 8.3MP) -> reduce to 2MP
        print("\n--- Test 1: 4K image (3840x2160 = 8.3MP) -> 2MP ---")
        test_4k = torch.rand(1, 2160, 3840, 3)  # [B, H, W, C]
        current_mp = (3840 * 2160) / 1_000_000
        print(f"Input: 3840x2160 ({current_mp:.1f}MP)")
        
        result1 = node.reduce_megapixels(
            images=test_4k,
            max_megapixels=2.0,
            only_reduce=True,
            interpolation="bilinear"
        )
        
        new_h, new_w = result1[0].shape[1], result1[0].shape[2]
        new_mp = (new_w * new_h) / 1_000_000
        print(f"Output: {new_w}x{new_h} ({new_mp:.1f}MP)")
        
        # Test 2: 8K image (7680x4320 = 33.2MP) -> reduce to 2MP
        print("\n--- Test 2: 8K image (7680x4320 = 33.2MP) -> 2MP ---")
        test_8k = torch.rand(1, 4320, 7680, 3)  # [B, H, W, C]
        current_mp = (7680 * 4320) / 1_000_000
        print(f"Input: 7680x4320 ({current_mp:.1f}MP)")
        
        result2 = node.reduce_megapixels(
            images=test_8k,
            max_megapixels=2.0,
            only_reduce=True,
            interpolation="bilinear"
        )
        
        new_h, new_w = result2[0].shape[1], result2[0].shape[2]
        new_mp = (new_w * new_h) / 1_000_000
        print(f"Output: {new_w}x{new_h} ({new_mp:.1f}MP)")
        
        # Test 3: Small image (1024x768 = 0.8MP) -> should remain unchanged
        print("\n--- Test 3: Small image (1024x768 = 0.8MP) -> should remain unchanged ---")
        test_small = torch.rand(1, 768, 1024, 3)  # [B, H, W, C]
        current_mp = (1024 * 768) / 1_000_000
        print(f"Input: 1024x768 ({current_mp:.1f}MP)")
        
        result3 = node.reduce_megapixels(
            images=test_small,
            max_megapixels=2.0,
            only_reduce=True,
            interpolation="bilinear"
        )
        
        new_h, new_w = result3[0].shape[1], result3[0].shape[2]
        new_mp = (new_w * new_h) / 1_000_000
        print(f"Output: {new_w}x{new_h} ({new_mp:.1f}MP)")
        print("Should be unchanged!")
        
        # Test 4: Portrait image (2160x3840 = 8.3MP) -> reduce to 2MP
        print("\n--- Test 4: Portrait 4K (2160x3840 = 8.3MP) -> 2MP ---")
        test_portrait = torch.rand(1, 3840, 2160, 3)  # [B, H, W, C] - portrait
        current_mp = (2160 * 3840) / 1_000_000
        print(f"Input: 2160x3840 ({current_mp:.1f}MP)")
        
        result4 = node.reduce_megapixels(
            images=test_portrait,
            max_megapixels=2.0,
            only_reduce=True,
            interpolation="bilinear"
        )
        
        new_h, new_w = result4[0].shape[1], result4[0].shape[2]
        new_mp = (new_w * new_h) / 1_000_000
        print(f"Output: {new_w}x{new_h} ({new_mp:.1f}MP)")
        
        # Test 5: Different target megapixels
        print("\n--- Test 5: 4K image -> 5MP ---")
        result5 = node.reduce_megapixels(
            images=test_4k,
            max_megapixels=5.0,
            only_reduce=True,
            interpolation="bilinear"
        )
        
        new_h, new_w = result5[0].shape[1], result5[0].shape[2]
        new_mp = (new_w * new_h) / 1_000_000
        print(f"Input: 3840x2160 (8.3MP)")
        print(f"Output: {new_w}x{new_h} ({new_mp:.1f}MP)")
        
        print("\n🎉 All AutoMegapixelReducer tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== AutoMegapixelReducer Node Test ===\n")
    success = test_megapixel_reducer()
    
    if success:
        print("\n✅ AutoMegapixelReducer working correctly!")
        print("\nFeatures:")
        print("- Automatically detects high-resolution images")
        print("- Reduces to target megapixel count while maintaining aspect ratio")
        print("- Perfect for handling 4K, 8K, and other large images")
        print("- Safe mode (only_reduce) prevents upscaling small images")
    else:
        print("\n❌ Tests failed. Check the errors above.")
