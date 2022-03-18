import os
import sys
import ffmpeg
from datetime import datetime


def check_path(path, is_directory):
    if not os.path.exists(path):
        content_type = 'directory' if is_directory else 'file'
        print(f'{path} {content_type} does not exist!')
        raise ValueError

    if is_directory and not os.path.isdir(path):
        print(f'{path} is not a directory!')
        raise ValueError

    if not is_directory and not os.path.isfile(path):
        print(f'{path} is not a file!')
        raise ValueError


def convert_file(filename: str, format: str, error_file: str, verbose: bool, delete_old: bool):
    try:
        check_path(filename, False)
    except ValueError:
        return

    format = '.' + format.strip('.')
    if filename.split('.')[-1] == format:
        print(f'{filename} is already {format}, skipping...')
        return

    output_filename = ''.join(filename.split('.')[:-1]) + format
    print(f'Converting {filename} to {output_filename}')
    try:
        stream = ffmpeg.input(filename)
        stream = ffmpeg.output(stream, output_filename)
        ffmpeg.run(stream, quiet=not verbose, overwrite_output=True)
        if delete_old:
            os.remove(filename)

    except Exception as e:
        if not error_file:
            return

        error_msg = f'{datetime.now()} - Error during converting {filename}\n{str(e)}\n'
        with open(error_file, 'a') as f:
            f.write(error_msg)


def convert_directory(path: str, format: str, error_file: str, recursive: bool, verbose: bool, delete_old: bool):
    try:
        check_path(path, True)
    except ValueError:
        return

    print(f'Converting directory {path}')
    dir_content = [os.path.join(path, i) for i in os.listdir(path)]
    for content in dir_content:
        if os.path.isdir(content) and recursive:
            convert_directory(content, format, error_file,
                              recursive, verbose, delete_old)
            continue

        convert_file(content, format, error_file, verbose, delete_old)


def print_help():
    message = 'This program converts all files in a given directory\n'
    message += 'Usage: python converter.py [OPTIONS] PATH\n\n'
    message += 'Options list:\n'
    message += '-f FORMAT - specify output file format\n'
    message += '-e FILE - specify error output file format\n'
    message += '-r - recursive conversion\n'
    message += '-v - verbose logs\n'
    message += '-d - delete files after successful formatting\n'
    print(message)


def extract_string_arg(option_name: str, arg_name: str, is_required: bool) -> str:
    args = sys.argv
    not_found_msg = f'No {arg_name} is specified!'
    if not option_name in args:
        print(not_found_msg)
        if is_required:
            raise ValueError
        return ''

    option_index = args.index(option_name)
    if option_index == len(args) - 1:
        print(not_found_msg)
        raise ValueError

    return args[option_index+1]


def main():
    global error_file
    args = sys.argv
    if len(args) == 1:
        print('Too few arguments!')
        return

    if '--help' in args:
        print_help()
        return

    format = extract_string_arg('-f', 'format', True)
    error_file = extract_string_arg('-e', 'error file', False)
    recursive = '-r' in args
    verbose = '-v' in args
    delete_old = '-d' in args
    path = args[-1]
    convert_directory(path, format, error_file, recursive, verbose, delete_old)


if __name__ == '__main__':
    main()
