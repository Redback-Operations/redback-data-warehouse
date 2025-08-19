import yaml
import pandas as pd
from utils import tabular, images, videos
import logging
from datetime import datetime
import json
import os

def setup_logger(log_path='pipeline.log'):
    logger = logging.getLogger('DataPreprocessingPipeline')
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:  # Avoid duplicate handlers in repeated runs
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

def load_tabular_data(path, data_type='csv'):
    if data_type == 'csv':
        return pd.read_csv(path)
    elif data_type == 'json':
        return pd.read_json(path)
    else:
        raise ValueError(f"Unsupported tabular type: {data_type}")

def main():
    logger = setup_logger()
    logger.info("Starting preprocessing pipeline")

    metadata = {
        'run_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
        'start_time': datetime.now().isoformat(),
        'steps': []
    }

    def log_step(step_name, info):
        metadata['steps'].append({
            'step': step_name,
            'timestamp': datetime.now().isoformat(),
            'info': info
        })

    # Load config
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    logger.info("Loaded config.yaml")

    # TABULAR
    if 'tabular' in config:
        tab_cfg = config['tabular']
        logger.info(f"Loading tabular data from {tab_cfg['path']}")
        df = load_tabular_data(tab_cfg['path'], tab_cfg.get('type', 'csv'))
        logger.info(f"Original tabular shape: {df.shape}")

        processed_df, tab_metadata = tabular.preprocess_tabular(df, tab_cfg['preprocessing'], logger=logger)
        logger.info(f"Processed tabular shape: {processed_df.shape}")

        if 'output_folder' in tab_cfg:
            os.makedirs(tab_cfg['output_folder'], exist_ok=True)
            save_path = os.path.join(tab_cfg['output_folder'], "processed_tabular.csv")
            processed_df.to_csv(save_path, index=False)
            logger.info(f"Saved processed tabular data to {save_path}")

        log_step('tabular_preprocessing', {
            'input_shape': df.shape,
            'output_shape': processed_df.shape,
            'output_folder': tab_cfg.get('output_folder'),
            'metadata': tab_metadata
        })

    # IMAGES
    if 'images' in config:
        img_cfg = config['images']['preprocessing']
        img_path = config['images']['path']
        output_folder = config['images'].get('output_folder')
        
        logger.info(f"Processing images from {img_path}")
        imgs = images.preprocess_images(img_path, img_cfg, logger=logger)
        logger.info(f"Processed {len(imgs)} images.")

        if output_folder:
            img_metadata = images.save_processed_images(imgs, output_folder, save_as="png", logger=logger)
            logger.info(f"Saved processed images and metadata to {output_folder}")
        else:
            img_metadata = []

        log_step('image_preprocessing', {
            'num_images_processed': len(imgs),
            'output_folder': output_folder,
            'metadata': img_metadata
        })

    # VIDEOS
    if 'videos' in config:
        vid_cfg = config['videos']['preprocessing']
        vid_path = config['videos']['path']
        output_folder = config['videos'].get('output_folder')

        logger.info(f"Processing video from {vid_path}")
        video_metadata_dict = {}
        frames = videos.preprocess_video(vid_path, vid_cfg, logger=logger, metadata=video_metadata_dict)
        logger.info(f"Processed {len(frames)} video frames.")

        if output_folder:
            vid_metadata = videos.save_processed_video_frames(frames, output_folder, logger=logger)
            logger.info(f"Saved video frames and metadata to {output_folder}")
        else:
            vid_metadata = []

        log_step('video_preprocessing', {
            'num_frames_processed': len(frames),
            'output_folder': output_folder,
            'metadata': vid_metadata,
            **video_metadata_dict
        })

    # Save metadata
    metadata['end_time'] = datetime.now().isoformat()
    metadata_path = f"metadata_{metadata['run_id']}.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    logger.info(f"Saved pipeline metadata to {metadata_path}")

    logger.info("Pipeline finished successfully")

if __name__ == "__main__":
    main()
