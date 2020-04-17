#!/usr/bin/env python3
import argparse

from fpdf import FPDF


def main(args):
    from os import listdir
    from os.path import isfile, join
    image_files = [f for f in listdir(args.directory) if isfile(join(args.directory, f))]
    image_files = sorted(image_files)

    pdf = FPDF('L', 'mm', 'A4')
    for image in image_files:
        pdf.add_page()
        pdf.image(f'{args.directory}/{image}', x=20, y=0, w=240, h=180)
    pdf.output(args.output, "F")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, help='directory with images', default='images')
    parser.add_argument('-o', '--output', type=str, help='output pdf filename', required=True)
    parsed_args = parser.parse_args()

    main(parsed_args)
