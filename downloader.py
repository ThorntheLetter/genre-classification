#!/usr/bin/env python3
"""Downloads a bunch of books from Project Gutenberg."""

from bs4 import BeautifulSoup
import csv
import os
import urllib.request
import re
import gutenberg.acquire
import gutenberg.cleanup
from tqdm import tqdm

CSV_LABEL = ["Number", "Title",
             "Fantasy", "Horror", "Mystery", "Romance", "Sci-Fi"]
DL_DIR = "data/text/"
CSV_FN = "data/labels.csv"
BOOKSHELF_BASE = "https://www.gutenberg.org/wiki/"
BOOKSHELF_END = "_(Bookshelf)"
GUTENBERG_BOOKSHELVES = {
        "Fantasy": 1,
        "Horror": 2,
        "Mystery_Fiction": 3,
        "Crime_Fiction": 3,
        "Detective_Fiction": 3,
        "Romantic_Fiction": 4,
        "Science_Fiction": 5}


def main():
    """Execute this when file is ran as a script."""
    os.makedirs(DL_DIR, exist_ok=True)
    csv_data = {}
    for shelf_url in GUTENBERG_BOOKSHELVES:
        print("Shelf: " + shelf_url)
        shelf = _get_bookshelf(shelf_url)
        for number, title in tqdm(shelf):
            raw_text = gutenberg.acquire.load_etext(number)
            stripped = gutenberg.cleanup.strip_headers(raw_text)

            ofile = open(DL_DIR + str(number) + ".txt", "w")
            ofile.write(stripped)
            ofile.close()

            if number in csv_data.keys():
                csv_data[number][GUTENBERG_BOOKSHELVES[shelf_url]] = True
            else:
                row = [title, False, False, False, False, False]
                row[GUTENBERG_BOOKSHELVES[shelf_url]] = True
                csv_data[number] = row

    csv_file = open(CSV_FN, "w")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(CSV_LABEL)
    for book_number in csv_data:
        csv_writer.writerow([book_number] + csv_data[book_number])


def _get_bookshelf(shelf):
    f = urllib.request.urlopen(BOOKSHELF_BASE + shelf + BOOKSHELF_END)
    soup = BeautifulSoup(f, "html.parser")
    book_tags = soup("a", title=re.compile("ebook:"))
    text_books = filter(_is_textual_book, book_tags)
    numbers = map(_extract_book_number, text_books)
    titles = map(_extract_book_titles, text_books)
    return zip(numbers, titles)


def _is_textual_book(tag):
    icon_tag = tag.find_next("img")
    if icon_tag["alt"] == "AudioIcon.png":
        return False
    return True


def _extract_book_number(tag):
    return int(tag["title"].split(":")[1])


def _extract_book_titles(tag):
    return tag.text


if __name__ == '__main__':
    main()
