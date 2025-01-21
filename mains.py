import streamlit as st
from transformers import pipeline
from PIL import Image as PILImage
import svgwrite  # For SVG generation
import os
import time

# Initialize the pipeline for Stable Diffusion
text_to_image = pipeline(
    task="text-to-image",
    model="stabilityai/stable-diffusion-3.5-large",
    use_auth_token="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"
)

# Function to generate an icon using Stable Diffusion
def generate_icon(icon_name, selected_colors, width, height):
    if not selected_colors:
        st.warning("Please select at least one color.")
        return None, None

    if not icon_name:
        st.warning("Please enter an icon name.")
        return None, None

    description = f"icon of a {icon_name} in {' and '.join(selected_colors)} color clear"
    st.info(f"Generating image for: {description} ...")

    try:
        start_time = time.time()
        images = text_to_image(description)
        end_time = time.time()
        st.success(f"Image generated in {end_time - start_time:.2f} seconds.")
        image = PILImage.fromarray(images[0])
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

# Sidebar for color selection
st.sidebar.header("Select Colors")
colors = {
    "gray": "Black & White",
    "violet": "Violet",
    "indigo": "Indigo",
    "blue": "Blue",
    "green": "Green",
    "yellow": "Yellow",
    "orange": "Orange",
    "red": "Red",
}
selected_colors = [color for color, name in colors.items() if st.sidebar.checkbox(name, value=color == "gray")]

# Icon name input
icon_name = st.text_input("Enter the icon name:", "")

# Dimensions input
col1, col2 = st.columns(2)
with col1:
    width = st.number_input("Width:", value=512, min_value=1, max_value=2048, step=1)
with col2:
    height = st.number_input("Height:", value=512, min_value=1, max_value=2048, step=1)

# Format selection
image_format = st.selectbox("Select image format:", ["PNG", "JPG", "JPEG", "SVG"])

# Generate button
if st.button("Generate"):
    if icon_name and selected_colors:
        image, _ = generate_icon(icon_name, selected_colors, width, height)

        if image:
            if image_format == "SVG":
                # Convert to SVG
                svg_path, svg_code = convert_to_svg(image)
                st.success(f"SVG file generated.")
                st.download_button("Download SVG", data=svg_code, file_name="output_image.svg", mime="image/svg+xml")
            else:
                # Save the image in the selected format
                output_path = f"output_image.{image_format.lower()}"
                image.save(output_path, format=image_format.upper())
                st.image(image, caption="Generated Icon", use_column_width=True)
                with open(output_path, "rb") as file:
                    st.download_button(label="Download Image", data=file, file_name=output_path)

