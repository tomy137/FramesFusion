# FramesFusion
An automated image collage generator that arranges photos into a balanced, high-quality mosaic with customizable layouts.

![Demo picture](https://i.imgur.com/rEoVPyM.jpeg)

# Description
This project is an automated image collage generator that helps you create stunning photo mosaics from a collection of images. Simply specify one or more folders of images, and the tool will load, resize, and arrange them into a balanced collage with customizable layouts and dimensions. The application dynamically calculates the optimal layout to ensure an even distribution of images, minimizing empty spaces and creating a visually pleasing composition.

Using a streamlined two-pass process, the tool first counts images and then displays a real-time progress bar as it loads and resizes photos, making it easy to track progress even with large collections. Ideal for photographers, designers, and casual users alike, this tool is perfect for creating memory collages, event highlights, or visual summaries with minimal effort.

Voici une version améliorée du README en anglais, en respectant les bonnes pratiques de présentation sur GitHub et en utilisant un format Markdown structuré pour plus de lisibilité.

# How to Use

### Installation
1. Clone this repository and navigate to the project directory.
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Running the Script

To generate a collage, run the following command:

```bash
python3 main.py --miniature_width=400 --to="collage_output.jpg" /path/to/folder1 /path/to/folder2 /path/to/folder3
```

### Parameters

| Parameter         | Description                                                                                           | Default              |
|-------------------|-------------------------------------------------------------------------------------------------------|----------------------|
| `--miniature_width` | Width of each image thumbnail in pixels.                                                              | 300                  |
| `--to`            | Name of the output file for the collage.                                                              | `bigcollage.jpg`     |
| `--subset_size`   | Number of random images to sample from the input folders, for testing on a reduced dataset.           | All images           |
| `--columns`       | Number of columns in the collage. If not specified, the script will automatically compute this value for an optimal width/height ratio. | Auto-calculated      |
| `folders`         | List of folder paths to scan for images. Each folder will be scanned recursively for supported image formats (`.png`, `.jpg`, `.jpeg`). | -                    |
| `--no_crop`       | By default, the collage will be cropped to ensure all columns are aligned with the shortest column height, creating a neat, even bottom edge. If included in the command, prevents the final collage image from being cropped.| False                    |
| `--no_auto_rotate` | By default, pictures will be auto rotate based on EXIF orientation. If included prevent this. | False |
### Example

To generate a collage with 400px wide thumbnails, save it as `collage_output.jpg`, using a maximum of 100 randomly selected images from the specified folders, run:

```bash
python3 main.py --miniature_width=400 --to="collage_output.jpg" --subset_size=100 /path/to/folder1 /path/to/folder2
```

### Supported Image Formats

This script currently supports the following image formats:
- `.png`
- `.jpg`
- `.jpeg`

Each specified folder will be scanned recursively to include all images in these formats.

# Warning
Warning, it's far from perfect. But after a few hours of work with the trusty ChatGPT, it's already pretty cool! Feel free to correct and improve it!