import os
import os.path as osp
from pathlib import Path
from shutil import copyfile, rmtree
from glob import glob
import numpy as np
import cv2
import json
import argparse
from tqdm import tqdm
import open3d as o3d  # for loading 3D models

import sys
sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
from data_utils import get_image_crop_resize, get_K_crop_resize


parser = argparse.ArgumentParser(description="Process IndustryShapes Onboarding Data")
parser.add_argument("--dataset_root", type=str, required=True, help="")
parser.add_argument("--folder_name", type=str, required=True, help="")
parser.add_argument("--model_root", type=str, required=True, help="")
parser.add_argument("--output_root", type=str, required=True, help="")
args = parser.parse_args()


def setup_output_dirs(output_data_obj_dir, sequence_name):
    output_data_seq_dir = osp.join(output_data_obj_dir, sequence_name)
    if osp.exists(output_data_seq_dir):
        rmtree(output_data_seq_dir)
    Path(output_data_seq_dir).mkdir(parents=True, exist_ok=True)

    subdirs = {
        "color": osp.join(output_data_seq_dir, "color"),
        "color_full": osp.join(output_data_seq_dir, "color_full"),
        "intrin_ba": osp.join(output_data_seq_dir, "intrin_ba"),
        "intrin": osp.join(output_data_seq_dir, "intrin"),
        "poses_ba": osp.join(output_data_seq_dir, "poses_ba")
    }
    for path in subdirs.values():
        Path(path).mkdir(exist_ok=True)
    return output_data_seq_dir, subdirs


def save_onboarding_metadata(obj_id, model_info, output_data_obj_dir):
    scale = np.array([model_info["size_x"], model_info["size_y"], model_info["size_z"]])
    corners = np.array([
        [-scale[0], -scale[0], -scale[0], -scale[0], scale[0], scale[0], scale[0], scale[0]],
        [-scale[1], -scale[1], scale[1], scale[1], -scale[1], -scale[1], scale[1], scale[1]],
        [-scale[2], scale[2], scale[2], -scale[2], -scale[2], scale[2], scale[2], -scale[2]],
    ]).T[:, :3] * 0.5

    np.savetxt(osp.join(output_data_obj_dir, "box3d_corners.txt"), corners)
    # copyfile(model_path, osp.join(output_data_obj_dir, "model_eval.ply"))
    np.savetxt(osp.join(output_data_obj_dir, "diameter.txt"), [model_info["diameter"]])


def project_model_get_bbox(model_path, R, t, K):
    mesh = o3d.io.read_triangle_mesh(model_path)
    points = np.asarray(mesh.vertices)
    transformed = (R @ points.T + t).T
    projected = (K @ transformed.T).T
    projected = projected[:, :2] / projected[:, 2:3]
    x_min, y_min = projected.min(axis=0)
    x_max, y_max = projected.max(axis=0)
    return [int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min)]


def process_image(global_id, rgb_path, scene_gt, scene_camera, obj_id,
                  model_path, subdirs):
    dataset_img_id = int(Path(rgb_path).stem)
    if str(dataset_img_id) not in scene_gt:
        return

    # Get GT index for object
    index_gt = next((i for i, gt in enumerate(scene_gt[str(dataset_img_id)])
                     if gt["obj_id"] == obj_id), None)
    if index_gt is None:
        print(f"GT not found for {dataset_img_id} and {obj_id}")
        return

    # Load camera intrinsics and pose
    K = np.array(scene_camera[str(dataset_img_id)]["cam_K"]).reshape(3, 3)
    R = np.array(scene_gt[str(dataset_img_id)][index_gt]["cam_R_m2c"]).reshape(3, 3)
    t = np.array(scene_gt[str(dataset_img_id)][index_gt]["cam_t_m2c"]).reshape(3, 1)
    pose = np.hstack((R, t))

    bbox = project_model_get_bbox(model_path, R, t, K)
    x0, y0, w, h = bbox
    x1, y1 = x0 + w, y0 + h

    # Clamp box within image bounds
    original_img = cv2.imread(rgb_path)
    img_h, img_w = original_img.shape[:2]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(img_w, x1), min(img_h, y1)

    box = np.array([x0, y0, x1, y1])
    crop_shape = np.array([y1 - y0, x1 - x0])
    K_crop, _ = get_K_crop_resize(box, K, crop_shape)
    cropped_img, _ = get_image_crop_resize(original_img, box, crop_shape)

    final_shape = np.array([512, 512])
    K_crop, _ = get_K_crop_resize([0, 0, crop_shape[1], crop_shape[0]], K_crop, final_shape)
    resized_img, _ = get_image_crop_resize(cropped_img, [0, 0, crop_shape[1], crop_shape[0]], final_shape)

    # cv2.imwrite(osp.join(subdirs["color"], f"{global_id:06d}.png"), resized_img)
    # cv2.imwrite(osp.join(subdirs["color_full"], f"{global_id:06d}.png"), original_img)
    # np.savetxt(osp.join(subdirs["intrin_ba"], f"{global_id:06d}.txt"), K_crop)
    # np.savetxt(osp.join(subdirs["intrin"], f"{global_id:06d}.txt"), K)
    # np.savetxt(osp.join(subdirs["poses_ba"], f"{global_id}.txt"), pose)
    
    cv2.imwrite(osp.join(subdirs["color"], f"{global_id}.png"), resized_img)
    cv2.imwrite(osp.join(subdirs["color_full"], f"{global_id}.png"), original_img)
    np.savetxt(osp.join(subdirs["intrin_ba"], f"{global_id}.txt"), K_crop)
    np.savetxt(osp.join(subdirs["intrin"], f"{global_id}.txt"), K)
    np.savetxt(osp.join(subdirs["poses_ba"], f"{global_id}.txt"), pose)

    vis_img = original_img.copy()
    cv2.rectangle(vis_img, (x0, y0), (x1, y1), color=(0, 255, 0), thickness=2)

    # Optional: save for debugging/visualization
    cv2.imwrite(osp.join(subdirs["color_full"], f"{global_id}_bbox.png"), vis_img)


def main():
    rgb_paths = sorted(glob(osp.join(args.dataset_root, args.folder_name, 'rgb', "*.png")))
    if not len(rgb_paths):
        rgb_paths = sorted(glob(osp.join(args.dataset_root, args.folder_name, 'rgb', "*.jpg")))

    with open(osp.join(args.dataset_root, args.folder_name, "scene_gt.json")) as f:
        scene_gt = json.load(f)
    with open(osp.join(args.dataset_root, args.folder_name, "scene_camera.json")) as f:
        scene_camera = json.load(f)
    with open(osp.join(args.model_root, 'models_info.json'), 'r') as f:
        models_info = json.load(f)
    
    # Get object id from first frame annotation
    first_frame = list(scene_gt.keys())[0]
    obj_id = scene_gt[first_frame][0]['obj_id']
    
    model_path = osp.join(args.model_root, f'obj_{obj_id:06d}.ply')

    output_data_obj_dir = osp.join(args.output_root, args.folder_name)
    sequence_name = f"{args.folder_name}-annotate"

    output_data_seq_dir, subdirs = setup_output_dirs(output_data_obj_dir, sequence_name)

    save_onboarding_metadata(obj_id, models_info[str(obj_id)], output_data_obj_dir)

    for global_id, rgb_path in tqdm(enumerate(rgb_paths), total=len(rgb_paths)):
        process_image(global_id, rgb_path, scene_gt, scene_camera, obj_id, model_path, subdirs)


if __name__ == "__main__":
    main()
