#!/usr/bin/env python
import xlrd
from uszipcode import SearchEngine
from geopy.distance import geodesic


def main():
    search = SearchEngine(simple_zipcode=True)
    zipcode = search.by_zipcode("10001")
    print zipcode
    print zipcode.lat
    print zipcode.lng

main()
