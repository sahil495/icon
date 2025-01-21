import streamlit as st
from huggingface_hub import InferenceClient
from PIL import Image as PILImage
import svgwrite  # For SVG generation
import os
import time

# Initialize the client for Hugging Face API
client = InferenceClient("ostris/Flex.1-alpha", token="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")

# Function to generate an icon using Hugging Face API
def generate_icon(icon_name, width, height):
    if not icon_name:
        st.warning("Please enter an icon name.")
        return None, None

    # Use descriptive words to generate simple, clear, minimalist icons
    description = f"simple, clean, minimalist icon of a {icon_name} with clear lines in black and white, like Bootstrap icons"
    st.info(f"Generating image for: {description} ...")

    try:
        start_time = time.time()
        image = client.text_to_image(description)
        end_time = time.time()
        st.success(f"Image generated in {end_time - start_time:.2f} seconds.")
    except Exception as e:
        st.error(f"Error generating image: {e}")
        return None, None

    # Resize the image
    image = image.resize((width, height))
    return image, None

# Function to convert an image to SVG
def convert_to_svg(image):
    bw_image = image.convert("L")  # Convert to grayscale
    bw_image = bw_image.point(lambda x: 0 if x < 128 else 255, '1')  # Binarize the image
    width, height = bw_image.size
    pixels = bw_image.load()

    # Create SVG file
    svg_output_path = "output_image.svg"
    dwg = svgwrite.Drawing(svg_output_path, size=(width, height))
    for y in range(height):
        for x in range(width):
            if pixels[x, y] == 0:  # Add a black square for each black pixel
                dwg.add(dwg.rect(insert=(x, y), size=(1, 1), fill='black'))
    dwg.save()

    with open(svg_output_path, "r") as svg_file:
        svg_code = svg_file.read()
    return svg_output_path, svg_code

# Streamlit App UI
st.title("Icon Generator App with SVG Support")

# Icon name input
icon_name = st.text_input("Enter the icon name:", "")

# Fixed width and height
width = 512
height = 512

# Inform the user about the default size
st.write("The image will be generated with a default size of 512x512.")

# Generate button
if st.button("Generate"):
    if icon_name:
        image, _ = generate_icon(icon_name, width, height)

        if image:
            # Convert to SVG
            svg_path, svg_code = convert_to_svg(image)
            st.success(f"SVG file generated.")
            st.download_button("Download SVG", data=svg_code, file_name="output_image.svg", mime="image/svg+xml")
