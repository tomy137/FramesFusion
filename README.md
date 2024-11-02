# FramesFusion
An automated image collage generator that arranges photos into a balanced, high-quality mosaic with customizable layouts.

![Demo picture](https://i.imgur.com/rEoVPyM.jpeg)

# Description
This project is an automated image collage generator that helps you create stunning photo mosaics from a collection of images. Simply specify one or more folders of images, and the tool will load, resize, and arrange them into a balanced collage with customizable layouts and dimensions. The application dynamically calculates the optimal layout to ensure an even distribution of images, minimizing empty spaces and creating a visually pleasing composition.

Using a streamlined two-pass process, the tool first counts images and then displays a real-time progress bar as it loads and resizes photos, making it easy to track progress even with large collections. Ideal for photographers, designers, and casual users alike, this tool is perfect for creating memory collages, event highlights, or visual summaries with minimal effort.

# HOW TO 
```
pip install -r requirements.txt
python3 main.py --miniature_width=400 /path/to/folder1 /path/to/folder2 /path/to/folder3
```