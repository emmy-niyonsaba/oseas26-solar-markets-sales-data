import re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, parse_qs, unquote
from html import unescape

import pandas as pd
import requests


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "SECTION_A2.csv"
OUTPUT_FILE = BASE_DIR / "SECTION_A2_readable.csv"

DICTIONARY_URL = (
    "https://microdata.worldbank.org/index.php/"
    "catalog/6429/data-dictionary/F9?file_name=SECTION_A2"
)

VARIABLE_BASE_URL = (
    "https://microdata.worldbank.org/index.php/"
    "catalog/6429/variable/F9/"
)


# ============================================================
# HTTP SESSION
# ============================================================

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/154.0.0.0 Safari/537.36"
    )
})


# ============================================================
# HTML ANCHOR PARSER
# ============================================================

class AnchorParser(HTMLParser):

    def __init__(self):
        super().__init__()

        self.anchors = []

        self.current_href = None
        self.current_text = []

    def handle_starttag(self, tag, attrs):

        if tag.lower() != "a":
            return

        attrs = dict(attrs)

        self.current_href = attrs.get("href")
        self.current_text = []

    def handle_data(self, data):

        if self.current_href is not None:
            self.current_text.append(data)

    def handle_endtag(self, tag):

        if tag.lower() != "a":
            return

        if self.current_href is not None:

            text = " ".join(
                self.current_text
            ).strip()

            self.anchors.append({
                "href": self.current_href,
                "text": text
            })

        self.current_href = None
        self.current_text = []


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(value):

    if value is None:
        return ""

    value = unescape(value)

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# ============================================================
# NORMALISE ENCODED VALUES
# ============================================================

def normalise_value(value):

    value = str(value).strip()

    if value == "":
        return ""

    # 1.0 -> 1
    # 2.0 -> 2
    # 10.0 -> 10

    if re.fullmatch(
        r"-?\d+\.0+",
        value
    ):
        return value.split(".")[0]

    return value


# ============================================================
# DOWNLOAD PAGE
# ============================================================

def get_html(url):

    response = session.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    return response.text


# ============================================================
# GET ALL OFFICIAL VARIABLE LABELS
# ============================================================

def get_variable_labels():

    print()
    print("Reading official SECTION_A2 dictionary...")

    html = get_html(
        DICTIONARY_URL
    )

    parser = AnchorParser()
    parser.feed(html)

    labels = {}

    for anchor in parser.anchors:

        href = anchor["href"]
        text = clean_text(
            anchor["text"]
        )

        if not href or not text:
            continue

        absolute_url = urljoin(
            DICTIONARY_URL,
            href
        )

        parsed = urlparse(
            absolute_url
        )

        if "/catalog/6429/variable/F9/" not in parsed.path:
            continue

        query = parse_qs(
            parsed.query
        )

        if "name" not in query:
            continue

        variable_name = unquote(
            query["name"][0]
        ).strip()

        if not variable_name:
            continue

        # The page has a link containing the
        # variable code and another link containing
        # the human-readable label.
        #
        # Ignore the code link itself.

        if text.upper() == variable_name.upper():
            continue

        labels[variable_name] = text

    return labels


# ============================================================
# GET OFFICIAL VALUE LABELS FOR ONE VARIABLE
# ============================================================

def get_value_labels(variable_name):

    variable_url = (
        VARIABLE_BASE_URL
        + "?name="
        + variable_name
    )

    html = get_html(
        variable_url
    )

    mappings = {}

    # --------------------------------------------------------
    # Find every table row
    # --------------------------------------------------------

    rows = re.findall(
        r"<tr\b[^>]*>(.*?)</tr>",
        html,
        flags=re.IGNORECASE | re.DOTALL
    )

    for row in rows:

        cells = re.findall(
            r"<t[dh]\b[^>]*>(.*?)</t[dh]>",
            row,
            flags=re.IGNORECASE | re.DOTALL
        )

        if len(cells) < 2:
            continue

        cleaned = []

        for cell in cells:

            # Remove HTML tags
            cell = re.sub(
                r"<[^>]+>",
                " ",
                cell
            )

            cell = unescape(cell)

            cell = re.sub(
                r"\s+",
                " ",
                cell
            ).strip()

            cleaned.append(cell)

        value = cleaned[0]
        category = cleaned[1]

        if not value or not category:
            continue

        # Ignore headers
        if value.lower() in {
            "value",
            "code",
            "category",
            "value/category"
        }:
            continue

        mappings[
            normalise_value(value)
        ] = category

    return mappings


# ============================================================
# DECODE A SINGLE CELL
# ============================================================

def decode_cell(value, value_labels):

    value = str(value)

    # Empty cell stays empty
    if value.strip() == "":
        return value

    normalised = normalise_value(
        value
    )

    # Official mapping exists
    if normalised in value_labels:

        return value_labels[
            normalised
        ]

    # No official mapping:
    # NEVER GUESS.
    return value


# ============================================================
# MAKE COLUMN NAMES UNIQUE
# ============================================================

def make_unique_columns(
    original_columns,
    labels
):

    result = []
    used = set()

    for code, label in zip(
        original_columns,
        labels
    ):

        # Keep both:
        #
        # A001 — Human readable question
        #
        # This means we never lose the original
        # MTF variable identifier.

        new_name = f"{code} — {label}"

        if new_name not in used:

            result.append(new_name)
            used.add(new_name)

            continue

        counter = 2

        candidate = (
            f"{new_name} ({counter})"
        )

        while candidate in used:

            counter += 1

            candidate = (
                f"{new_name} ({counter})"
            )

        result.append(candidate)
        used.add(candidate)

    return result


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 75)
    print("RWANDA MTF 2022 — SECTION_A2 FULL DECODER")
    print("=" * 75)

    # --------------------------------------------------------
    # Check input
    # --------------------------------------------------------

    if not INPUT_FILE.exists():

        print()
        print(
            f"ERROR: {INPUT_FILE.name} "
            f"was not found."
        )

        return

    # --------------------------------------------------------
    # Read original encoded CSV
    # --------------------------------------------------------

    print()
    print("Reading original SECTION_A2.csv...")

    df = pd.read_csv(
        INPUT_FILE,
        dtype=str,
        keep_default_na=False
    )

    original_columns = list(
        df.columns
    )

    print(
        f"Rows:    {len(df):,}"
    )

    print(
        f"Columns: {len(df.columns):,}"
    )

    # --------------------------------------------------------
    # Get variable names + human labels
    # --------------------------------------------------------

    variable_labels = get_variable_labels()

    print(
        f"Official variable labels found: "
        f"{len(variable_labels):,}"
    )

    # --------------------------------------------------------
    # Store human-readable column labels
    # --------------------------------------------------------

    readable_labels = []

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    decoded_cells = 0
    variables_with_value_dictionary = 0

    print()
    print("=" * 75)
    print("DECODING COLUMNS + ROWS + CELLS")
    print("=" * 75)

    # ========================================================
    # PROCESS EVERY COLUMN
    # ========================================================

    for column in original_columns:

        print()
        print(
            f"[{column}]"
        )

        # ----------------------------------------------------
        # COLUMN DECODING
        # ----------------------------------------------------

        human_label = variable_labels.get(
            column,
            column
        )

        print(
            f"  Column: {human_label}"
        )

        readable_labels.append(
            human_label
        )

        # ----------------------------------------------------
        # CELL DECODING
        # ----------------------------------------------------

        try:

            value_labels = get_value_labels(
                column
            )

        except Exception as error:

            print(
                f"  WARNING: Could not get "
                f"value dictionary: {error}"
            )

            value_labels = {}

        if value_labels:

            variables_with_value_dictionary += 1

            print(
                f"  Official cell mappings: "
                f"{len(value_labels)}"
            )

        else:

            print(
                "  Official cell mappings: 0"
            )

        # ----------------------------------------------------
        # Decode every row/cell in this column
        # ----------------------------------------------------

        def decoder(value):

            nonlocal decoded_cells

            original_value = str(value)

            decoded_value = decode_cell(
                original_value,
                value_labels
            )

            if decoded_value != original_value:

                decoded_cells += 1

            return decoded_value

        df[column] = df[column].map(
            decoder
        )

    # ========================================================
    # COLUMN RENAMING
    # ========================================================

    print()
    print(
        "Renaming columns..."
    )

    df.columns = make_unique_columns(
        original_columns,
        readable_labels
    )

    # ========================================================
    # SAVE
    # ========================================================

    print()
    print(
        "Saving readable dataset..."
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 75)
    print("DECODING COMPLETE")
    print("=" * 75)

    print(
        f"Original rows:             {len(df):,}"
    )

    print(
        f"Original columns:          {len(original_columns):,}"
    )

    print(
        f"Variables with dictionaries: "
        f"{variables_with_value_dictionary:,}"
    )

    print(
        f"Cells decoded:             "
        f"{decoded_cells:,}"
    )

    print()
    print(
        f"Created: {OUTPUT_FILE.name}"
    )

    print()
    print(
        "Original SECTION_A2.csv was NOT modified."
    )

    print(
        "All values without an official mapping "
        "were left unchanged."
    )

    print()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()