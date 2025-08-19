import os
import pandas as pd
from PIL import Image
import numpy as np
from datetime import datetime

def save_processed_video_frames(frames, output_folder, logger=None):
    os.makedirs(output_folder, exist_ok=True)

    metadata = []
    saved_count = 0
    for idx, frame in enumerate(frames):
        # Convert float32 RGB array [0,1] back to uint8 [0,255]
        frame_uint8 = (frame * 255).astype(np.uint8)
        img = Image.fromarray(frame_uint8)

        filename = f'frame_{idx:04d}.png'
        out_path = os.path.join(output_folder, filename)
        try:
            img.save(out_path)
            saved_count += 1
            if logger:
                logger.debug(f"Saved frame {idx} to {out_path}")
            # Collect metadata
            metadata.append({
                "filename": filename,
                "width": img.width,
                "height": img.height,
                "timestamp": datetime.now().isoformat(),
                "processed_path": out_path
            })
        except Exception as e:
            if logger:
                logger.error(f"Error saving frame {idx}: {e}")

    if logger:
        logger.info(f"Saved {saved_count} frames to folder: {output_folder}")

    # Save metadata CSV
    metadata_df = pd.DataFrame(metadata)
    metadata_csv_path = os.path.join(output_folder, "metadata.csv")
    metadata_df.to_csv(metadata_csv_path, index=False)

    if logger:
        logger.info(f"Saved video frames metadata to {metadata_csv_path}")

    return metadata 
