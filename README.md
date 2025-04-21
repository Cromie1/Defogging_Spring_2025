# Defogging Project

## Overview
This project focuses on collecting, processing, and training data for **defogging images** using a Pix2Pix model.  
It includes programs for both **data collection** (via Raspberry Pi) and **dataset preparation** (splitting and augmenting the data for training and testing).

---

## Project Structure


- **RaspberryPiPrograms/**  
  Contains all scripts and files needed for **data collection** using a Raspberry Pi.  
  These programs capture fogged and clear images for the dataset.

- **DataloaderPrograms/**  
  Contains scripts for **preprocessing** the collected data.  
  Each program inside this folder:
  - Looks for a `dataset` folder in the current directory.
  - Splits the dataset into `train/` and `test/` sets automatically.
  - Supports various splitting and augmentation methods (e.g., cropping, variance thresholding, rotation augmentation).

---

## Usage Instructions

### 1. Data Collection
- Navigate to the `RaspberryPiPrograms/` directory on your Raspberry Pi.
- Run the appropriate script to start capturing images.

### 2. Data Preparation
- Place your raw images inside a folder named `dataset/`.
- Navigate to the `DataloaderPrograms/` directory.
- Run one of the provided scripts depending on your preprocessing needs:
  ```bash
  python SplitDatasetAugment.py
