import os
import random
import math
from PIL import Image, ExifTags
from tqdm import tqdm
import argparse

Image.MAX_IMAGE_PIXELS = 500_000_000

def fusion_frames_from_folders(folders:list[str], miniature_width:int|None=300, subset_size:int|None=None, columns:int|None=None, no_crop:bool=False, no_auto_rotate:bool=False) -> Image:
    """ Fusionne les images des dossiers spécifiés pour créer un collage.
    """
    pictures = find_pictures_in_folders(folders)
    random.shuffle(pictures)
    frames = load_and_resize_pictures(pictures, target_width=miniature_width, subset_size=subset_size, no_auto_rotate=no_auto_rotate)
    collage = create_collage(frames, columns, no_crop)
    return collage

def find_pictures_in_folders(paths:list[str]) -> list[str]:
    """ Recherche les images dans les dossiers spécifiés et renvoie une liste de chemins d'accès.
    """
    print(f"🖼️ Looking for pictures on the {paths} gived folders...")
    images = []
    for folder in paths:
        for root, _, files in os.walk(folder):
            folders_files_founded = 0
            for filename in files:
                if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    filepath = os.path.join(root, filename)
                    images.append(filepath)
                    folders_files_founded += 1
            print(f"📁 {root} : {folders_files_founded} files found.")

    if len(images) == 0:
        raise Exception("🖼️ No images found in the specified folders.")

    print(f"🖼️ Find {len(images)} pictures in the specified folders.")
    return images

def load_and_resize_pictures(pictures:list[str], target_width:int, subset_size:int|None=None, no_auto_rotate:bool=False) -> list[Image]:
    """ Charger et redimensionner les images, avec barre de progression.
    """
    resized_pictures = []
    
    if subset_size is not None:
        print(f"🖼️ Creating a subset of {subset_size} images.")
        pictures = pictures[:subset_size]

    # Deuxième passe pour charger et redimensionner les images avec tqdm
    with tqdm(total=len(pictures), desc="Loading and resizing images", unit="image") as pbar:
        for picture in pictures:
            try:
                with Image.open(picture) as img:
                    if not no_auto_rotate:
                        img = correct_image_orientation(img)
                    # Redimensionne l'image dès le chargement
                    resized_image = resize_image_to_width(img, target_width)
                    resized_pictures.append(resized_image)
                    pbar.update(1)  # Met à jour la barre de progression
                
            except Exception as e:
                print(f"🖼️ Error loading image {picture} : {e}")

    return resized_pictures

def resize_image_to_width(image:Image, target_width:int) -> Image:
    """Resize image to a specific width while maintaining aspect ratio."""
    width_percent = target_width / float(image.width)
    target_height = int(float(image.height) * width_percent)
    resized_image = image.resize((target_width, target_height), Image.LANCZOS)
    return resized_image

def calculate_optimal_collage_width(num_images, avg_height_per_image, target_width):
    """Calculate optimal collage width based on the number of images and average height."""
    approx_square_side = math.sqrt(num_images * avg_height_per_image * target_width)
    num_columns = max(1, int(approx_square_side / target_width))
    optimal_width = num_columns * target_width
    return optimal_width

def distribute_images_uniformly(images, num_columns):
    # Sort images by height in descending order
    sorted_images = sorted(images, key=lambda x: x.height, reverse=True)
    
    # Initialize columns and their heights
    columns = [[] for _ in range(num_columns)]
    column_heights = [0] * num_columns
    
    # Distribute images into columns
    for image in sorted_images:
        # Find the column with the lowest total height
        min_height_index = column_heights.index(min(column_heights))
        
        # Add the image to this column
        columns[min_height_index].append(image)
        
        # Update the total height of the column
        column_heights[min_height_index] += image.height
    
    # shuffle the columns to avoid having the tallest columns on one side
    random.shuffle(columns)
    for c in columns:
        random.shuffle(c)
    return columns

def create_collage(frames:list[Image], columns:int|None=None, no_crop:bool=False) -> Image:
    print("🖼️ Resizing images to a common width...")

    total_height = sum(img.height for img in frames)
    avg_height_per_image = total_height / len(frames)
    num_images = len(frames)
    frames_width = frames[0].width

    if not columns:
        max_collage_width = calculate_optimal_collage_width(num_images, avg_height_per_image, frames_width)
        num_columns = max(1, max_collage_width // frames_width)
    else:
        num_columns = columns

    target_column_height = total_height / num_columns * 0.9
    print(f"🖼️ Target column height: {target_column_height}px across {num_columns} columns.")

    _columns = []
    current_column = []
    current_height = 0
    
    _columns = distribute_images_uniformly(frames, num_columns)

    if not no_crop:
        _columns, min_height = balance_column_heights(_columns)

    collage_width = len(_columns) * frames_width
    collage_theoric_height = max(sum(img.height for img in col) for col in _columns)
    collage = Image.new("RGB", (collage_width, collage_theoric_height), (0, 0, 0))
    print("🖼️ Creating collage canvas with a black background...")

    x_offset = 0
    for col_num, col in enumerate(_columns, start=1):
        y_offset = 0
        for img in col:
            collage.paste(img, (x_offset, y_offset))
            y_offset += img.height
        print(f"🖼️ Placed column {col_num} at x offset {x_offset}.")
        x_offset += frames_width

    if not no_crop and (min_height < collage_theoric_height):
        collage = collage.crop((0, 0, collage_width, min_height))
        print(f"✂️ Cropping collage to final height of {min_height}px.")

    print("🖼️ Collage creation complete!")
    return collage

def balance_column_heights(columns):
    # Calculer la hauteur totale de chaque colonne
    column_heights = [sum(img.height for img in col) for col in columns]
    min_height = min(column_heights)

    print(f"✂️ Minimum column height to match: {min_height}px")

    # Ajuster chaque colonne pour qu'elle corresponde à la hauteur minimale
    for col_idx, col in enumerate(columns):
        excess_height = column_heights[col_idx] - min_height
        if excess_height > 1:
            print(f"✂️ Column {col_idx} - Excess height: {excess_height}px, reducing height of each image.")
            
            # Calculer le nombre de pixels à enlever par image
            pixels_to_crop_per_image = excess_height // len(col)
            
            for img_idx, img in enumerate(col):
                # Calculer combien enlever en haut et en bas
                top_crop = pixels_to_crop_per_image // 2
                bottom_crop = pixels_to_crop_per_image - top_crop

                # Rogner l'image uniformément sur le haut et le bas
                cropped_img = img.crop((0, top_crop, img.width, img.height - bottom_crop))
                col[img_idx] = cropped_img  # Remplacer l'image par sa version rognée

    print("✂️ All columns balanced to the same height.")
    return columns, min_height


def correct_image_orientation(img):
    try:
        # Récupérer les métadonnées EXIF de l'image
        exif = img._getexif()
        if exif:
            # Trouver la clé correspondant à l'orientation
            for tag, value in exif.items():
                if ExifTags.TAGS.get(tag) == 'Orientation':
                    orientation = value
                    if not orientation in [3, 6, 8]:
                        break
                    #print(f"🔄 Correcting image orientation: {value}")

                    # Appliquer la rotation/transposition selon l'orientation EXIF
                    if orientation == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)
                    break
    except Exception as e:
        print(f"Error correcting orientation: {e}")

    return img

def main():
    parser = argparse.ArgumentParser(description="Generate an image collage from multiple folders.")
    parser.add_argument("--miniature_width", type=int, default=300, help="Width of each image in the collage")
    parser.add_argument("folders", nargs="+", help="Paths to folders containing images")
    parser.add_argument("--to", type=str, default="bigfusion.jpg", help="Output file name for the collage")
    parser.add_argument("--subset_size", type=int, default=None, help="Size of the subset to use for collage creation")
    parser.add_argument("--columns", type=int, default=None, help="Number of columns to use in the collage")
    parser.add_argument("--no_crop", action="store_true", help="Crop images to match the shortest column")
    parser.add_argument("--no_auto_rotate", action="store_true", help="Auto rotate images based on EXIF orientation")

    args = parser.parse_args()
    framesFusion = fusion_frames_from_folders(
        folders=args.folders, 
        miniature_width=args.miniature_width, 
        subset_size=args.subset_size,
        columns=args.columns,
        no_crop=args.no_crop,
        no_auto_rotate=args.no_auto_rotate,
    )

    framesFusion.save(args.to, "JPEG")
    print(f"Big fusion saved as '{args.to}'.")

if __name__ == "__main__":
    main()
