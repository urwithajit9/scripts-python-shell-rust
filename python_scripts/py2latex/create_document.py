import os
import argparse
from jinja2 import Template

def read_template(template_path):
    """Reads the Jinja template from the specified file path."""
    with open(template_path, 'r') as file:
        return file.read()

def get_tex_files_from_directory(directory):
    """Returns a list of .tex files in the specified directory."""
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.tex')]

def convert_files(input_files, template_path, output_file, overwrite=False):
    """Renders the LaTeX template with the given list of input files and saves to output file."""
    # Read the template from the file
    latex_template = read_template(template_path)

    # Create a Template object
    template = Template(latex_template)

    # Render the template with the list of filenames
    rendered_latex = template.render(input_files=input_files)

    # Check if output file exists and handle overwrite
    if not overwrite and os.path.exists(output_file):
        print(f"Output file '{output_file}' already exists. Use '-O' to overwrite.")
        return

    # Output the rendered LaTeX code
    with open(output_file, 'w') as file:
        file.write(rendered_latex)

    print(f"Rendered LaTeX saved to {output_file}")

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Convert .tex files to a LaTeX document using a Jinja template.")

    # Argument for directory
    parser.add_argument('-d', '--directory', type=str, help="Directory path to filter .tex files.")

    # Argument for list of files
    parser.add_argument('-f', '--files', nargs='+', help="List of .tex files to convert.")

    # Argument for output file name
    parser.add_argument('-o', '--output', type=str, default='output_document.tex', help="Output LaTeX file name (default: output_document.tex).")

    # Argument for overwrite option
    parser.add_argument('-O', '--overwrite', action='store_true', help="Overwrite output file if it already exists.")

    # Argument for template file
    parser.add_argument('-t', '--template', type=str, default='latex_template.jinja', help="Path to the Jinja template file (default: latex_template.jinja).")

    args = parser.parse_args()

    # Get the list of input files
    if args.directory:
        input_files = get_tex_files_from_directory(args.directory)
    elif args.files:
        input_files = args.files
    else:
        print("Please provide either a directory with '-d' or a list of files with '-f'.")
        exit(1)

    # Convert files using the specified template and output file
    convert_files(input_files, args.template, args.output, args.overwrite)
