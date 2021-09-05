# openapi-path-extractor

This script solves the problem when you want to get part of your openapi specification. It cuts all data exept the paths (with refs) which you mentioned.

## RUN

`python3 extract_paths.py {input file} {output file} {path1} {path2} {path3} ...`

where path - uri from your specification you want to extract

