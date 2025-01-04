import argparse
from PIL import Image, ImageDraw, ImageFont

def generate_street_sign_raw(street_name, street_type):
    # Convert to uppercase
    street_name = street_name.upper()
    street_type = street_type.upper()

    # Base dimensions and colors
    sign_height = 200
    base_sign_width = 800
    background_color = "green"
    text_color = "white"
    border_color = "white"
    border_thickness = 5

    # Padding and font sizes
    padding = 20
    name_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
    type_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)

    # Calculate text sizes
    name_bbox = name_font.getbbox(street_name)
    name_width, name_height = name_bbox[2], name_bbox[3]

    type_bbox = type_font.getbbox(street_type)
    type_width, type_height = type_bbox[2], type_bbox[3]

    # Calculate required sign width
    total_text_width = name_width + type_width + padding * 3  # Account for spacing
    sign_width = max(base_sign_width, total_text_width)

    # Create an image with a white border
    image = Image.new("RGB", (sign_width, sign_height), border_color)
    draw = ImageDraw.Draw(image)

    # Draw the green rectangle (inner area)
    draw.rectangle(
        [border_thickness, border_thickness, sign_width - border_thickness, sign_height - border_thickness],
        fill=background_color
    )

    # Calculate positions for the text
    name_x = border_thickness + padding
    name_y = (sign_height - name_height) // 2
    type_x = name_x + name_width + padding
    type_y = name_y + (name_height - type_height)

    # Draw the text
    draw.text((name_x, name_y), street_name, font=name_font, fill=text_color)
    draw.text((type_x, type_y), street_type, font=type_font, fill=text_color)

    return image


def generate_street_sign(street_name, street_type, output_file="streetsign.png"):
    image = generate_street_sign_raw(street_name, street_type)
    image.save(output_file)
 

def main():
    parser = argparse.ArgumentParser(description="Generate a street sign image.")
    parser.add_argument("street_name", type=str, help="The name of the street.")
    parser.add_argument("street_type", type=str, help="The type of the street (e.g., RD, ST).")
    parser.add_argument(
        "-o", "--output", type=str, default="streetsign.png", help="Output file name (default: streetsign.png)."
    )

    args = parser.parse_args()
    generate_street_sign(args.street_name, args.street_type, args.output)

if __name__ == "__main__":
    main()
