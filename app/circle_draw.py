from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_annulus_with_wrapped_text(outer_radius=160, font_size=20, text="Hurfadurfdoo! Slapasmappy!") -> ImageDraw:
    # Create an image with a transparent background
    image_size = [int(outer_radius * 2.2)] * 2
    inner_radius = int(outer_radius * 0.5)

    # Define the center of the image
    center = (image_size[0] // 2, image_size[1] // 2)

    # Step 1: Create an RGBA image with a transparent background
    image = Image.new("RGBA", image_size, (255, 255, 255, 0))

    # Step 2: Create a separate mask for the annulus shape
    mask = Image.new("L", image_size, 0)  # Grayscale (L) mask, fully transparent initially
    mask_draw = ImageDraw.Draw(mask)

    # Draw the outer circle in the mask (opaque area)
    mask_draw.ellipse(
        [image_size[0] // 2 - outer_radius, image_size[1] // 2 - outer_radius,
         image_size[0] // 2 + outer_radius, image_size[1] // 2 + outer_radius],
        fill=255  # Opaque
    )

    # Cut out the inner circle (transparent area)
    mask_draw.ellipse(
        [image_size[0] // 2 - inner_radius, image_size[1] // 2 - inner_radius,
         image_size[0] // 2 + inner_radius, image_size[1] // 2 + inner_radius],
        fill=0  # Transparent
    )

    # Step 3: Create the annulus with blue fill and apply the mask
    annulus = Image.new("RGBA", image_size, "red")  # Fill annulus with blue
    annulus.putalpha(mask)  # Apply transparency mask

    # Step 4: Paste the annulus onto the main image
    image.paste(annulus, (0, 0), annulus)


    # Add wrapped text in the center of the annulus
    # try:
    font = ImageFont.truetype("Symbola_hint.ttf", font_size)
    #except IOError:
    #    # Use a simple default font if truetype font is not available
        # TODO: Add better exception reporting
    #    font = ImageFont.load_default()

    # Determine general letter height and width
    dummy_image = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_image)
    bbox = draw.textbbox((0,0), 'A', font=font)
    A_width = (bbox[2] - bbox[0])
    A_height = (bbox[3] - bbox[1]) * 1.25

    # Calculate the maximum width for text wrapping
    max_text_width = inner_radius * 2 + 10  
    wrapped_text = textwrap.fill(
        text, 
        width=max_text_width // A_width,
        break_long_words=False
    )

    # Center the text vertically in the annulus
    lines = wrapped_text.split("\n")
    text_height = len(lines) * A_height
    y_offset = image_size[1] // 2 - text_height // 2

    draw = ImageDraw.Draw(image)
    for line in lines:
        text_width = font.getlength(line)
        x_offset = image_size[0] // 2 - text_width // 2
        draw.text((x_offset, y_offset), line, fill="black", font=font)
        y_offset += A_height
    
    return image

   


# Example usage
if __name__ == '__main__':
    output_path = "annulus_with_text.png"
    
    image = create_annulus_with_wrapped_text(font_size=50, text='7')
     # Save the image to the specified path
    image.save(output_path)
