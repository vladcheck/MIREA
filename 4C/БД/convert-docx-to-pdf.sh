#!/bin/bash

# Check if a filename was provided
if [ -z "$1" ]; then
    echo "Usage: $0 <filename.docx>"
    exit 1
fi

INPUT_FILE="$1"

# Check if the file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: File '$INPUT_FILE' not found!"
    exit 1
fi

# Use LibreOffice (which is installed on this Mac) to run in headless mode and convert the document
# It will place the converted PDF in the same directory as the input file
/Applications/LibreOffice.app/Contents/MacOS/soffice --headless --convert-to pdf "$INPUT_FILE" --outdir "$(dirname "$INPUT_FILE")"

if [ $? -eq 0 ]; then
    echo "Successfully converted '$INPUT_FILE' to PDF in the same directory."
else
    echo "Conversion failed!"
    exit 1
fi
