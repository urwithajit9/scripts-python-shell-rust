import os
import argparse
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import LatexFormatter

def convert_file_to_latex(input_file, output_file):
    """Converts a single file to LaTeX format using Pygments."""
    with open(input_file, 'r') as f:
        code = f.read()

    # Use the Pygments lexer for Python (or adjust as needed)
    lexer = get_lexer_by_name("python", stripall=True)
    formatter = LatexFormatter()

    # Convert the code to LaTeX
    latex_code = highlight(code, lexer, formatter)

    # Save the LaTeX code to the output file
    with open(output_file, 'w') as f:
        f.write(latex_code)

    print(f"Converted {input_file} to {output_file}")

def convert_files_in_directory(directory, file_extension):
    """Converts files with a specific extension in the given directory to LaTeX format."""
    for filename in os.listdir(directory):
        if filename.endswith(file_extension):
            input_file = os.path.join(directory, filename)
            if os.path.isfile(input_file):
                output_file = os.path.join(directory, f"{os.path.splitext(filename)[0]}.tex")
                convert_file_to_latex(input_file, output_file)

def convert_files(file_list):
    """Converts a list of files to LaTeX format."""
    for input_file in file_list:
        if os.path.isfile(input_file):
            output_file = f"{os.path.splitext(input_file)[0]}.tex"
            convert_file_to_latex(input_file, output_file)

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Convert Python files to LaTeX format using Pygments.")

    # Add argument for directory
    parser.add_argument('-d', '--directory', type=str, help="Directory path to convert all files in the directory.")

    # Add argument for list of files
    parser.add_argument('--files', nargs='+', help="List of files to convert.")

    # Add argument for file extension
    parser.add_argument('-e', '--extension', type=str, default='.py', help="File extension to filter files by (default: .py).")

    args = parser.parse_args()

    # If directory is specified, convert all files in the directory
    if args.directory:
        convert_files_in_directory(args.directory, args.extension)

    # If a list of files is specified, convert those files
    if args.files:
        convert_files(args.files)

    # If neither is provided, show a message
    if not args.directory and not args.files:
        print("Please provide a directory with -d or a list of files with --files.")
