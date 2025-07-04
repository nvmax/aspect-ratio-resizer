import torch
import torch.nn.functional as F
try:
    from server import PromptServer
except ImportError:
    # Fallback if server import fails
    PromptServer = None


class AspectRatioResizer:
    """
    A ComfyUI custom node that resizes images while maintaining aspect ratio.
    If the image width or height exceeds the specified maximum, it will be resized
    to fit within those constraints while preserving the original aspect ratio.
    """

    CATEGORY = "image/resize"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "max_width": ("INT", {
                    "default": 1024,
                    "min": 64,
                    "max": 8192,
                    "step": 8,
                    "display": "number"
                }),
                "max_height": ("INT", {
                    "default": 1024,
                    "min": 64,
                    "max": 8192,
                    "step": 8,
                    "display": "number"
                }),
                "enable_width": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Width Enabled",
                    "label_off": "Width Disabled"
                }),
                "enable_height": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Height Enabled",
                    "label_off": "Height Disabled"
                }),
                "resize_mode": (["downscale_only", "upscale_only", "both"], {
                    "default": "downscale_only"
                }),
                "interpolation": (["nearest", "linear", "bilinear", "bicubic", "trilinear", "area"], {
                    "default": "bilinear"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("resized_images",)
    FUNCTION = "resize_images"
    
    def resize_images(self, images, max_width, max_height, enable_width, enable_height, resize_mode, interpolation):
        """
        Resize images while maintaining aspect ratio.

        Args:
            images: Batch of images as torch.Tensor with shape [B, H, W, C]
            enable_width: Whether to use width constraint
            max_width: Maximum allowed width (only used if enable_width is True)
            enable_height: Whether to use height constraint
            max_height: Maximum allowed height (only used if enable_height is True)
            resize_mode: Whether to only downscale, only upscale, or both
            interpolation: Interpolation method for resizing

        Returns:
            Tuple containing the resized images
        """
        batch_size, original_height, original_width, channels = images.shape
        
        # Convert to the format expected by torch.nn.functional.interpolate [B, C, H, W]
        images_tensor = images.permute(0, 3, 1, 2)
        
        resized_images = []
        resize_info = []
        
        for i in range(batch_size):
            image = images_tensor[i:i+1]  # Keep batch dimension

            # Validate that at least one dimension is enabled
            if not enable_width and not enable_height:
                # If both are disabled, no resize needed
                resized_images.append(image)
                resize_info.append({
                    "original": f"{original_width}x{original_height}",
                    "new": "unchanged (both constraints disabled)",
                    "scale": "1.000"
                })
                continue

            # Calculate scaling factor based on enabled constraints
            scale_factors = []
            width_scale = None
            height_scale = None

            if enable_width:
                width_scale = max_width / original_width
                scale_factors.append(width_scale)

            if enable_height:
                height_scale = max_height / original_height
                scale_factors.append(height_scale)

            # Use the most restrictive scale factor (smallest) to maintain aspect ratio
            scale_factor = min(scale_factors)
            
            # Determine if we should resize based on the resize_mode
            should_resize = False
            if resize_mode == "downscale_only" and scale_factor < 1.0:
                should_resize = True
            elif resize_mode == "upscale_only" and scale_factor > 1.0:
                should_resize = True
            elif resize_mode == "both":
                should_resize = True
            
            if should_resize and scale_factor != 1.0:
                # Calculate new dimensions
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)
                
                # Ensure dimensions are at least 1 and even numbers for better compatibility
                new_width = max(2, new_width - (new_width % 2))
                new_height = max(2, new_height - (new_height % 2))
                
                # Resize the image
                resized_image = F.interpolate(
                    image, 
                    size=(new_height, new_width), 
                    mode=interpolation,
                    align_corners=False if interpolation in ['linear', 'bilinear', 'bicubic', 'trilinear'] else None
                )
                
                # Determine which constraint was used
                constraint_used = []
                if enable_width and width_scale is not None and width_scale == scale_factor:
                    constraint_used.append(f"width:{max_width}")
                if enable_height and height_scale is not None and height_scale == scale_factor:
                    constraint_used.append(f"height:{max_height}")

                constraint_text = " & ".join(constraint_used) if constraint_used else "aspect ratio"

                resize_info.append({
                    "original": f"{original_width}x{original_height}",
                    "new": f"{new_width}x{new_height}",
                    "scale": f"{scale_factor:.3f}",
                    "constraint": constraint_text
                })
            else:
                # No resize needed
                resized_image = image

                # Show which constraints were checked
                constraints_checked = []
                if enable_width:
                    constraints_checked.append(f"width≤{max_width}")
                if enable_height:
                    constraints_checked.append(f"height≤{max_height}")

                constraint_text = " & ".join(constraints_checked) if constraints_checked else "none"

                resize_info.append({
                    "original": f"{original_width}x{original_height}",
                    "new": "unchanged",
                    "scale": "1.000",
                    "constraint": f"within limits ({constraint_text})"
                })
            
            resized_images.append(resized_image)
        
        # Concatenate all resized images back into a batch
        result_tensor = torch.cat(resized_images, dim=0)
        
        # Convert back to ComfyUI format [B, H, W, C]
        result_tensor = result_tensor.permute(0, 2, 3, 1)
        
        # Send resize information to the frontend (if available)
        if PromptServer is not None:
            try:
                # Create constraints description
                constraints = []
                if enable_width:
                    constraints.append(f"width≤{max_width}")
                if enable_height:
                    constraints.append(f"height≤{max_height}")
                constraints_text = " & ".join(constraints) if constraints else "none"

                PromptServer.instance.send_sync("aspectratioresizer.resize_info", {
                    "batch_size": batch_size,
                    "resize_info": resize_info,
                    "constraints": constraints_text,
                    "resize_mode": resize_mode,
                    "enable_width": enable_width,
                    "enable_height": enable_height
                })
            except Exception as e:
                print(f"AspectRatioResizer: Could not send frontend message: {e}")
        
        return (result_tensor,)


class AutoMegapixelReducer:
    """
    A ComfyUI custom node that automatically reduces image resolution if it exceeds
    a specified megapixel threshold while maintaining aspect ratio.
    Perfect for handling very large images like 4K, 8K, etc.
    """

    CATEGORY = "image/resize"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "max_megapixels": ("FLOAT", {
                    "default": 2.1,
                    "min": 0.1,
                    "max": 50.0,
                    "step": 0.1,
                    "display": "number"
                }),
                "only_reduce": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Only Reduce (Safe)",
                    "label_off": "Allow Upscale"
                }),
                "interpolation": (["nearest", "linear", "bilinear", "bicubic", "trilinear", "area"], {
                    "default": "bilinear"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("resized_images",)
    FUNCTION = "reduce_megapixels"

    def reduce_megapixels(self, images, max_megapixels, only_reduce, interpolation):
        """
        Reduce image resolution if it exceeds megapixel threshold.

        Args:
            images: Batch of images as torch.Tensor with shape [B, H, W, C]
            max_megapixels: Maximum allowed megapixels (e.g., 2.0 for 2MP)
            only_reduce: If True, only reduce size, never increase
            interpolation: Interpolation method for resizing

        Returns:
            Tuple containing the resized images
        """
        import math

        batch_size, original_height, original_width, channels = images.shape

        # Convert to the format expected by torch.nn.functional.interpolate [B, C, H, W]
        images_tensor = images.permute(0, 3, 1, 2)

        resized_images = []
        resize_info = []

        # Calculate current megapixels
        current_megapixels = (original_width * original_height) / 1_000_000

        for i in range(batch_size):
            image = images_tensor[i:i+1]  # Keep batch dimension

            # Check if resize is needed
            if current_megapixels <= max_megapixels:
                # No resize needed
                resized_images.append(image)
                resize_info.append({
                    "original": f"{original_width}x{original_height}",
                    "new": "unchanged",
                    "megapixels": f"{current_megapixels:.2f}MP",
                    "target": f"{max_megapixels}MP",
                    "scale": "1.000"
                })
                continue

            if only_reduce and current_megapixels <= max_megapixels:
                # Only reduce mode and image is already small enough
                resized_images.append(image)
                resize_info.append({
                    "original": f"{original_width}x{original_height}",
                    "new": "unchanged (only_reduce mode)",
                    "megapixels": f"{current_megapixels:.2f}MP",
                    "target": f"{max_megapixels}MP",
                    "scale": "1.000"
                })
                continue

            # Calculate target dimensions to achieve max_megapixels
            target_total_pixels = max_megapixels * 1_000_000

            # Calculate scale factor to achieve target megapixels
            current_total_pixels = original_width * original_height
            scale_factor = math.sqrt(target_total_pixels / current_total_pixels)

            # Calculate new dimensions
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)

            # Ensure dimensions are at least 2 and even numbers for better compatibility
            new_width = max(2, new_width - (new_width % 2))
            new_height = max(2, new_height - (new_height % 2))

            # Recalculate actual megapixels with rounded dimensions
            actual_megapixels = (new_width * new_height) / 1_000_000

            # Resize the image
            resized_image = F.interpolate(
                image,
                size=(new_height, new_width),
                mode=interpolation,
                align_corners=False if interpolation in ['linear', 'bilinear', 'bicubic', 'trilinear'] else None
            )

            resize_info.append({
                "original": f"{original_width}x{original_height}",
                "new": f"{new_width}x{new_height}",
                "megapixels": f"{current_megapixels:.2f}MP → {actual_megapixels:.2f}MP",
                "target": f"{max_megapixels}MP",
                "scale": f"{scale_factor:.3f}"
            })

            resized_images.append(resized_image)

        # Concatenate all resized images back into a batch
        result_tensor = torch.cat(resized_images, dim=0)

        # Convert back to ComfyUI format [B, H, W, C]
        result_tensor = result_tensor.permute(0, 2, 3, 1)

        # Send resize information to the frontend (if available)
        if PromptServer is not None:
            try:
                PromptServer.instance.send_sync("automegapixelreducer.resize_info", {
                    "batch_size": batch_size,
                    "resize_info": resize_info,
                    "max_megapixels": max_megapixels,
                    "only_reduce": only_reduce,
                    "original_megapixels": current_megapixels
                })
            except Exception as e:
                print(f"AutoMegapixelReducer: Could not send frontend message: {e}")

        return (result_tensor,)


# Register the nodes
NODE_CLASS_MAPPINGS = {
    "AspectRatioResizer": AspectRatioResizer,
    "AutoMegapixelReducer": AutoMegapixelReducer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AspectRatioResizer": "Aspect Ratio Resizer",
    "AutoMegapixelReducer": "Auto Megapixel Reducer",
}
