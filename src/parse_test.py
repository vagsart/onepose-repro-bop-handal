import os
import os.path as osp
from pathlib import Path
from shutil import copyfile, rmtree
from glob import glob
import numpy as np
import json
import argparse
from tqdm import tqdm


parser = argparse.ArgumentParser(description="Process IndustryShapes Onboarding Data")
parser.add_argument("--dataset_root", type=str, required=True, help="")
parser.add_argument("--folder_name", type=str, required=True, help="")
parser.add_argument("--output_root", type=str, required=True, help="")
args = parser.parse_args()


def setup_output_dirs(output_data_obj_dir, sequence_name):
    output_data_seq_dir = osp.join(output_data_obj_dir, sequence_name)
    if osp.exists(output_data_seq_dir):
        rmtree(output_data_seq_dir)
    Path(output_data_seq_dir).mkdir(parents=True, exist_ok=True)

    subdirs = {
        "color_full": osp.join(output_data_seq_dir, "color_full"),
    }
    for path in subdirs.values():
        Path(path).mkdir(exist_ok=True)
    return output_data_seq_dir, subdirs

def main():
    rgb_paths = sorted(glob(osp.join(args.dataset_root, args.folder_name, 'rgb', "*.png")))
    if not len(rgb_paths):
        rgb_paths = sorted(glob(osp.join(args.dataset_root, args.folder_name, 'rgb', "*.jpg")))

    with open(osp.join(args.dataset_root, args.folder_name, "scene_gt.json")) as f:
        scene_gt = json.load(f)
    with open(osp.join(args.dataset_root, args.folder_name, "scene_camera.json")) as f:
        scene_camera = json.load(f)

    # Gather all obj_ids that appear
    obj_ids_set = set()
    for annotations in scene_gt.values():
        for ann in annotations:
            obj_ids_set.add(ann['obj_id'])
    obj_ids = sorted(list(obj_ids_set))

    print(f"Found {len(obj_ids)} unique object IDs: {obj_ids}")

    # Extract intrinsics from first frame
    first_frame_id = next(iter(scene_camera))
    cam_K = np.array(scene_camera[first_frame_id]['cam_K']).reshape(3, 3)
    fx, fy = cam_K[0, 0], cam_K[1, 1]
    cx, cy = cam_K[0, 2], cam_K[1, 2]
    

    output_data_seq_dir, subdirs = setup_output_dirs(args.output_root, args.folder_name)

    # Copy RGB images
    for rgb_path in tqdm(rgb_paths):
        filename = osp.basename(rgb_path)
        # Remove leading zeros from filename (keep extension)
        name_no_ext, ext = osp.splitext(filename)
        if ext == '.jpg':
            ext = '.png'
        name_no_zeros = str(int(name_no_ext)) + ext
        dst_path = osp.join(subdirs["color_full"], name_no_zeros)
        copyfile(rgb_path, dst_path)

    # Create obj_ids.txt file and save object IDs
    obj_ids_txt_path = osp.join(output_data_seq_dir, "obj_ids.txt")
    with open(obj_ids_txt_path, "w") as f_obj_ids:
        for obj_id in obj_ids:
            f_obj_ids.write(f"{int(obj_id):06d}\n")

    # Save intrinsics.txt
    intrinsics_path = osp.join(output_data_seq_dir, "intrinsics.txt")
    with open(intrinsics_path, "w") as f_intr:
        f_intr.write(f"fx: {fx:.6f}\n")
        f_intr.write(f"fy: {fy:.6f}\n")
        f_intr.write(f"cx: {cx:.6f}\n")
        f_intr.write(f"cy: {cy:.6f}\n")

    # Create Frames.txt
    frames_txt_path = osp.join(output_data_seq_dir, "Frames.txt")
    with open(frames_txt_path, "w") as f_frames:
        f_frames.write("timestamp,frame_index,fx,fy,cx,cy\n")
        for idx, rgb_path in enumerate(rgb_paths):
            filename = osp.basename(rgb_path)
            frame_index = int(osp.splitext(filename)[0])  # Assuming filename like 000001.png
            line = f"0,{frame_index},{fx:.6f},{fy:.6f},{cx:.6f},{cy:.6f}\n"
            f_frames.write(line)

if __name__ == "__main__":
    main()
