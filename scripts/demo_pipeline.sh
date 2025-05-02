#!/bin/bash
PROJECT_DIR="path/to/OnePose_Plus_Plus"
ONB_DIR="path/to/output/onboarding"
TEST_DIR="path/to/output/onboardingtest"

# echo "Current work dir: $PROJECT_DIR"

# echo '--------------------------------------------------------------'
# echo 'Run Keypoint-Free SfM to reconstruct object point cloud for pose estimation:'
# echo '--------------------------------------------------------------'

# # Loop through each object folder in the demo directory
# for dir in "$ONB_DIR"/*/; do
#     OBJ_NAME=$(basename "$dir")
#     echo "Processing object: $OBJ_NAME"
#     echo "$ONB_DIR/$OBJ_NAME $OBJ_NAME-annotate"
#     if [[ "$folder_name" == *sfm* ]]; then
#         echo "Skipping folder $folder_name"
#         continue
#     fi

#     # Check if tkl_model exists for this object
#     TKL_PATH="$ONB_DIR"/sfm_model/outputs_softmax_loftr_loftr/"$OBJ_NAME"/tkl_model
#     echo "TKL_PATH: $TKL_PATH"
#     if [[ -e "$TKL_PATH" ]]; then
#         echo "Skipping $OBJ_NAME: tkl_model already exists at $TKL_PATH"
#         continue
#     fi

#     python "$PROJECT_DIR/run.py" \
#         +preprocess="sfm_demo" \
#         dataset.data_dir="[$ONB_DIR/$OBJ_NAME $OBJ_NAME-annotate]" \
#         dataset.outputs_dir="$ONB_DIR/sfm_model"
# done





echo "-----------------------------------"
echo "Run inference and output demo video:"
echo "-----------------------------------"

# For every folder in test directory
for dir in "$TEST_DIR"/*/; do
    FOLDER_NAME=$(basename "$dir")
    echo "Processing object: $FOLDER_NAME"
    
    # For every object in folder
    while IFS= read -r OBJ_ID; do
    
    # TODO: Check object 10
    if [[ "$OBJ_ID" == "000010" ]]; then
        echo "Skipping object ID $OBJ_ID"
        continue
    fi

        OBJ_NAME="obj_${OBJ_ID}_up"
        echo "Processing OBJ_NAME: $OBJ_NAME"

        cp $ONB_DIR/$OBJ_NAME/box3d_corners.txt $TEST_DIR/box3d_corners.txt
        # Run inference on $OBJ_NAME-test and output demo video:
        python "$PROJECT_DIR/demo.py" +experiment="inference_demo" data_base_dir="$TEST_DIR $FOLDER_NAME" sfm_base_dir="$ONB_DIR/sfm_model/outputs_softmax_loftr_loftr/$OBJ_NAME"

        rm $TEST_DIR/box3d_corners.txt
        # Add also copy of results
        mv "$TEST_DIR"/"$FOLDER_NAME"/demo_video.mp4 "$TEST_DIR"/"$FOLDER_NAME"/"$OBJ_ID"_demo_video.mp4
    done < "$TEST_DIR/$FOLDER_NAME/obj_ids.txt"

done
