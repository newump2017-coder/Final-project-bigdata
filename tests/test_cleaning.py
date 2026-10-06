"""Basic tests for cleaning/classification rules (midterm)."""
import pytest


def clean_arabic_numbers(value: str) -> str:
    table = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
    return value.translate(table)


def test_arabic_numbers():
    assert clean_arabic_numbers("١٢٣") == "123"
    assert clean_arabic_numbers("٥٠٠٠") == "5000"


def test_currency_strip():
    def strip_currency(v: str) -> str:
        for token in ["ريال", "ريال يمني", "YER"]:
            v = v.replace(token, "")
        return v.strip()
    assert strip_currency("5000 ريال") == "5000"
    assert strip_currency("1000 YER") == "1000"


def test_thousands_separator():
    def strip_sep(v: str) -> str:
        return v.replace(",", "")
    assert strip_sep("125,000.00") == "125000.00"
