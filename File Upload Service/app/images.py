import os
import pandas as pd
from PIL import Image
import numpy as np
from datetime import datetime

def save_processed_images(images, output_folder, save_as="png", logger=None):
    valid_formats = ["png", "jpg", "jpeg", "bmp", "tiff"]
    save_as = save_as.lower()
    
    if save_as not in valid_formats:
        if logger:
            logger.warning(f"Unsupported image format '{save_as}'. Defaulting to 'png'.")
        save_as = "png"

    os.makedirs(output_folder, exist_ok=True)

    metadata = []

    for i, img_array in enumerate(images):
        img_uint8 = (img_array * 255).astype(np.uint8)

        # Convert to PIL image
        if img_uint8.ndim == 2:
            img_pil = Image.fromarray(img_uint8, mode='L')
        else:
            img_pil = Image.fromarray(img_uint8)

        # Save image
        filename = f"processed_img_{i}.{save_as}"
        save_path = os.path.join(output_folder, filename)
        img_pil.save(save_path)

        # Collect metadata
        metadata.append({
            "filename": filename,
            "width": img_pil.width,
            "height": img_pil.height,
            "timestamp": datetime.now().isoformat(),
            "processed_path": save_path
        })

        if logger:
            logger.debug(f"Saved processed image {save_path}")

    # Save metadata CSV
    metadata_df = pd.DataFrame(metadata)
    metadata_csv_path = os.path.join(output_folder, "metadata.csv")
    metadata_df.to_csv(metadata_csv_path, index=False)

    if logger:
        logger.info(f"Saved image metadata to {metadata_csv_path}")

    return metadata