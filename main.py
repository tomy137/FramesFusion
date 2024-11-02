import os
import random
import math
from PIL import Image
from tqdm import tqdm
import argparse

def count_images_in_folders(paths):
    """Première passe pour compter le nombre total d'images dans les dossiers spécifiés."""
    total_images = 0
    for folder in paths:
        for root, _, files in os.walk(folder):
            total_images += sum(1 for filename in files if filename.lower().endswith((".png", ".jpg", ".jpeg")))
    print(f"Total images found: {total_images}")
    return total_images

def load_and_resize_images_from_folders(paths, target_width=300):
    """Première passe pour charger et redimensionner les images, avec barre de progression."""
    images = []
    total_images = count_images_in_folders(paths)  # Première passe pour le comptage

    # Deuxième passe pour charger et redimensionner les images avec tqdm
    with tqdm(total=total_images, desc="Loading and resizing images", unit="image") as pbar:
        for folder in paths:
            for root, _, files in os.walk(folder):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    
                    # Vérifie l'extension pour inclure uniquement les images
                    if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
                        continue
                    
                    try:
                        with Image.open(filepath) as img:
                            # Redimensionne l'image dès le chargement
                            resized_image = resize_image_to_width(img, target_width)
                            images.append(resized_image)
                            pbar.update(1)  # Met à jour la barre de progression
                        
                    except Exception as e:
                        print(f"Error loading image {filename} in {root}: {e}")

    return images

def resize_image_to_width(image, target_width):
    """Resize image to a specific width while maintaining aspect ratio."""
    width_percent = target_width / float(image.width)
    target_height = int(float(image.height) * width_percent)
    resized_image = image.resize((target_width, target_height), Image.ANTIALIAS)
    return resized_image

def calculate_optimal_collage_width(num_images, avg_height_per_image, target_width):
    """Calculate optimal collage width based on the number of images and average height."""
    approx_square_side = math.sqrt(num_images * avg_height_per_image * target_width)
    num_columns = max(1, int(approx_square_side / target_width))
    optimal_width = num_columns * target_width
    return optimal_width

def create_collage(images, target_width=300):
    print("Resizing images to a common width...")
    resized_images = []
    
    # Utilisation de tqdm pour afficher la barre de progression lors du redimensionnement
    for img in tqdm(images, desc="Resizing images", unit="image"):
        resized_images.append(resize_image_to_width(img, target_width))
    
    random.shuffle(resized_images)  # Shuffle for a random arrangement
    print(f"All images resized to {target_width}px width.")

    total_height = sum(img.height for img in resized_images)
    avg_height_per_image = total_height / len(resized_images)
    num_images = len(resized_images)

    max_collage_width = calculate_optimal_collage_width(num_images, avg_height_per_image, target_width)
    num_columns = max(1, max_collage_width // target_width)

    target_column_height = total_height / num_columns * 0.9
    print(f"Target column height: {target_column_height}px across {num_columns} columns.")

    columns = []
    current_column = []
    current_height = 0

    for img in resized_images:
        if current_height + img.height > target_column_height and current_column:
            columns.append(current_column)
            current_column = []
            current_height = 0
        current_column.append(img)
        current_height += img.height

    if current_column:
        columns.append(current_column)

    while len(columns) > 1 and sum(img.height for img in columns[-1]) < target_column_height * 0.8:
        columns[-1].insert(0, columns[-2].pop())
        if not columns[-2]:
            columns.pop(-2)

    collage_width = len(columns) * target_width
    collage_height = max(sum(img.height for img in col) for col in columns)
    print(f"Final collage dimensions will be approximately {collage_width}px wide by {collage_height}px high.")

    collage = Image.new("RGB", (collage_width, collage_height), (0, 0, 0))
    print("Creating collage canvas with a black background...")

    x_offset = 0
    for col_num, col in enumerate(columns, start=1):
        y_offset = 0
        for img in col:
            collage.paste(img, (x_offset, y_offset))
            y_offset += img.height
        print(f"Placed column {col_num} at x offset {x_offset}.")
        x_offset += target_width

    print("Collage creation complete!")
    return collage

def main():
    parser = argparse.ArgumentParser(description="Generate an image collage from multiple folders.")
    parser.add_argument("--miniature_width", type=int, default=300, help="Width of each image in the collage")
    parser.add_argument("folders", nargs="+", help="Paths to folders containing images")
    parser.add_argument("--to", type=str, default="bigfusion.jpg", help="Output file name for the collage")

    args = parser.parse_args()

    print("Starting image loading and resizing process...")
    images = load_and_resize_images_from_folders(args.folders, target_width=args.miniature_width)
    if not images:
        print("No images found in the specified folders.")
        return

    print("Starting collage creation process...")
    collage = create_collage(images, target_width=args.miniature_width)
    collage.save(args.to, "JPEG")
    print(f"Big fusion saved as '{args.to}'.")

if __name__ == "__main__":
    main()
