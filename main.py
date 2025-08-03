from algorithm.core.spatial_domain import *
from pathlib import Path
from algorithm.tools.exel_writer import appendData_xl
import os



def filter_datesets(root: str) -> None:
    
    img_id = 1

    for label_folder in sorted(os.listdir(root)):
        folder_dir = os.path.join(root, label_folder)
        if not os.path.isdir(folder_dir):
            continue
    
        for file_name in os.listdir(folder_dir):
            if not file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            img_path = os.path.join(folder_dir, file_name)
            print(f"\n[NOTICE]: [{img_id}] Processing: {file_name} | Label: {label_folder}")

            success = process(label_folder, img_path, img_id)

            img_id += 1



def process(label: str, img_path: str , id: int) -> dict:

    analysis_result = {}
    CONFIG = g_loadConfig()

    try:
        img = cv2.imread(img_path)
        
        spatial = Spatial_Domain(img)
        img_config = CONFIG.get('image', {})

        ela_cfg = img_config.get("ela")
        if ela_cfg and ela_cfg.get("enabled"):
            ela_res = spatial.ela(
                ela_cfg.get("compression"),
                ela_cfg.get("multiplier")
            )
            analysis_result.update({f"ELA_{k}": v for k, v in ela_res.items()})

        noise_cfg = img_config.get("noise")
        if noise_cfg and noise_cfg.get("enabled"):
            noise_res = spatial.noise(
                noise_cfg.get("local_mean"),
                noise_cfg.get("varience")
            )
            analysis_result.update({f"Noise_{k}": v for k, v in noise_res.items()})

        copyMove_cfg = img_config.get("copyMove")
        if copyMove_cfg and copyMove_cfg.get("enabled"):
            copyMove_res = spatial.copyMove(
                copyMove_cfg.get("block_size"),
                copyMove_cfg.get("step"),
                copyMove_cfg.get("threshold")
            )
            analysis_result.update({f"CopyMove_{k}": v for k, v in copyMove_res.items()})


        resampling_res = spatial.resampling()
        analysis_result.update({f"Resampling_{k}": v for k,v in resampling_res.items()})

        return datasets_gen(label, analysis_result, id) 


    except Exception as e:
        print(f"[ALERT] Error during the process: {e}")
        return False




def datasets_gen(label: str, result: dict, id: int) -> None:
    
    exel_path = "datasets/mmmn_GroundTruth_datasets.xlsx"

    append = appendData_xl(exel_path, label, result, id)

    if append:
        print(f"[NOTICE] successfuly appened data")
        return True
    else:
        print(f"[ERROR] failed to append data")
        return False






if __name__ == "__main__":

    root_dir = "datasets"
    filter_datesets(root_dir)