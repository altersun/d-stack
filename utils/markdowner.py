import os
import argparse
import markdown
import html

def convert_markdown_to_html(input_file, custom_header):
    # Check if the input file exists
    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' does not exist.")
        return

    # Read the Markdown content
    with open(input_file, 'r', encoding='utf-8') as file:
        markdown_content = file.read()

    # Convert Markdown to HTML with fenced code block support
    html_content = markdown.markdown(markdown_content, extensions=['fenced_code'])

    # Escape special characters to ensure proper rendering
    html_content = html.unescape(html_content)

    # Determine the output file name
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}.html"

    # Write the HTML content to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(custom_header)
        file.write(html_content)

    print(f"Conversion successful! HTML file saved as '{output_file}'.")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Convert a Markdown file to HTML.")
    parser.add_argument(
        "-i", "--input_file",
        help="Path to the Markdown file to convert."
    )
    parser.add_argument(
        "-c", "--css_file",
        help="Path to css file to reference.", 
        default=None
    )     

    # Parse the arguments
    args = parser.parse_args()

    # Custom HTML header
    header_raw = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '<title>About</title>',
        '</head>',
    ]
    if args.css_file:
        css_line = f'<link rel="stylesheet" href="{args.css_file}">'
        header_raw.insert(len(header_raw) - 1, css_line)
    header = '\n'.join(header_raw)

    # Call the conversion function
    convert_markdown_to_html(args.input_file, header)

if __name__ == "__main__":
    main()
