# Reproducing OnePose and OnePose++ on the HANDAL Dataset

This repository prepares **HANDAL dataset** for **OnePose** and **OnePose++**.

---

## Instructions

### 1. Download the HANDAL Dataset
Download the HANDAL dataset from the BOP benchmark:
[Insert dataset link here]

### 2. Prepare Folder Structure
Run the following script after modifying the dataset paths to match your local setup:


```bash scripts/batch_run_handal.sh
```

This creates the required folder structure and intermediate files so that OnePose and OnePose++ can run bypassing the first step in demo pipelines.

### 3. Run Demo Pipeline
Execute the modified demo pipeline from **OnePose++** directory using:

```bash path/to/repo/scripts/demo_pipeline.sh
```

This will run OnePose++ for all combinations of onboarding and test scenes.

---

## Minimal Reproduction Example

To quickly test the pipeline:

1. Download the pre-structured folders in OnePose / OnePose++ format:
   [Insert link to structured data]

2. Run the demo pipeline from the original OnePose or OnePose++ repository **after commenting out the first step**, which generates intermediate files already included in the download:

```bash scripts/demo_pipeline.sh
```
3. View the results here: 
   [Insert link to results]

---

## Notes

- This repo does not modify the original OnePose / OnePose++ codebases beyond skipping preprocessing.


---


