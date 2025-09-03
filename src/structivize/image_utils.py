import numpy as np
from PIL import Image


def images_are_similar(img_path1, img_path2, tolerance=5):
    with Image.open(img_path1) as i1, Image.open(img_path2) as i2:
        img1 = i1.convert("RGBA")
        img2 = i2.convert("RGBA")

        # Get the smaller common size
        common_size = (min(img1.size[0], img2.size[0]), min(img1.size[1], img2.size[1]))  # width  # height

        # Resize both to the smaller size
        img1_resized = img1.resize(common_size)
        img2_resized = img2.resize(common_size)

        # Convert to numpy arrays
        arr1 = np.array(img1_resized)
        arr2 = np.array(img2_resized)

        # Compare with tolerance
        return np.allclose(arr1, arr2, atol=tolerance)


def is_image_single_color(img_path):
    try:
        with Image.open(img_path) as img:
            img_rgba = img.convert("RGBA")
            pixels = np.array(img_rgba)
            # Flatten all pixel values and check if all are the same
            return np.all(pixels == pixels[0, 0])
    except Exception as e:
        print(f"Error opening image: {e}")
        return False


def is_image_mainly_black(image_path, threshold=5, black_ratio=0.55, alpha_threshold=10):
    """
    Check if the image is mainly black.

    Parameters:
    - image_path: path to the image file
    - threshold: pixel values below this are considered black (0-255)
    - black_ratio: minimum ratio of black pixels to consider the image as mainly black

    Returns:
    - True if image is mainly black, False otherwise
    """
    with Image.open(image_path) as img:
        img_rgba = img.convert("RGBA")
        np_img = np.array(img_rgba)

        # Split RGBA
        r, g, b, a = np_img[:, :, 0], np_img[:, :, 1], np_img[:, :, 2], np_img[:, :, 3]

        # Create a mask for "visible" pixels
        visible_mask = a >= alpha_threshold

        # Check if RGB values are all below threshold
        black_mask = (r < threshold) & (g < threshold) & (b < threshold)

        # Apply visibility filter
        black_visible_pixels = np.sum(black_mask & visible_mask)
        total_visible_pixels = np.sum(visible_mask)

        if total_visible_pixels == 0:
            return False  # no visible content → not black

        return (black_visible_pixels / total_visible_pixels) >= black_ratio


def is_image_valid(img_path):
    try:
        with Image.open(img_path) as img:
            img.verify()  # Checks if image is not corrupted
        return True
    except Exception as e:
        print(f"Image is broken: {e}")
        return False


def get_png_size(image_path):
    with Image.open(image_path) as img:
        return img.size


def resize_png_preserve_aspect(image_path, max_width, max_height, keep_transparency=True):
    """
    Resize a PNG image while preserving the aspect ratio.

    Parameters:
    - input_path: Path to the input PNG image
    - output_path: Path to save the resized image
    - max_width, max_height: Bounding box for resized image
    - keep_transparency: If False, background will be white
    """
    with Image.open(image_path) as img:
        img_rgba = img.convert("RGBA")
        # Resize while keeping aspect ratio
        img_rgba.thumbnail((max_width, max_height), Image.LANCZOS)

        if keep_transparency:
            img_rgba.save(image_path, format="PNG")
        else:
            # Create white background
            background = Image.new("RGB", img_rgba.size, (255, 255, 255))
            background.paste(img_rgba, mask=img_rgba.split()[3])  # Paste using alpha channel as mask
            background.save(image_path, format="PNG")

        return img_rgba.size
