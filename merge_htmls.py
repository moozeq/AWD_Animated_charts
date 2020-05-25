#!/usr/bin/env python3
import argparse


def main(args):
    from os import listdir
    from os.path import isfile, join
    html_files = [f for f in listdir(args.directory) if isfile(join(args.directory, f))]
    html_files = sorted(html_files)
    html_files = [f'{args.directory}/{file}' for file in html_files if file.endswith('.html') or file.endswith('.gif')]
    html = ''
    for filename in html_files:
        if filename.endswith('.html'):
            html += f'<div style="text-align: center;"><p align="center"><iframe src="{filename}" width="80%" height="80%"></iframe></p></div>\n'
        elif filename.endswith('.gif'):
            html += f'<div style="text-align: center;"><p align="center"><img src="{filename}" width="90%" height="auto"></img></p></div>\n'
    html += ''

    with open(args.output, 'w') as final:
        final.write(html)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, help='directory with images', default='images')
    parser.add_argument('-o', '--output', type=str, help='output pdf filename', required=True)
    parsed_args = parser.parse_args()

    main(parsed_args)
