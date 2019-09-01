#!/usr/bin/env python
import sys
import xlrd
from math import radians, cos, sin, asin, sqrt
from uszipcode import SearchEngine
from pyzipcode import ZipCodeDatabase

# classes for data organization
class zipStruct:
    def __init__(self, zipcode, latitude, longitude):
        self.zipcode    = zipcode
        self.latitude   = latitude
        self.longitude  = longitude


class hospitalDistance:
    def __init__(self,
                 distance,
                 hospital):
        self.distance = distance
        self.hospital = hospital


class hospitalStruct:
    def __init__(self,
                 center_id,
                 zipcode,
                 liver,
                 lung,
                 heart,
                 heart_lung,
                 kidney,
                 pancreas,
                 kidney_pancreas):
        self.center_id      = int(center_id)
        self.zipStruct      = getCoords(formatZip(zipcode))
        self.liver          = int(liver)
        self.heart          = int(heart)
        self.lung           = int(lung)
        self.heart_lung     = int(heart_lung)
        self.kidney         = int(kidney)
        self.pancreas       = int(pancreas)
        self.kidney_pancreas= int(kidney_pancreas)

# Helper Functions
def formatZip(zipcode):
    """
    Formats Zipcode into 5 digit string
    """
    entry = int(zipcode)
    return ('%05d' % entry)


def loadWorkbook(file):
    return xlrd.open_workbook(file)


def getColumn(sheet, cnumber):
    """
    Gets Column from excel spreadsheet
    """
    column = []
    for i in xrange(sheet.nrows):
        column.append(sheet.cell_value(i, cnumber))
    return column


def loadHospitals(sheet):
    """
    Loads Hospital data into structs for later use
    """
    hospital = []
    for i in xrange(sheet.nrows - 1):
        row = sheet.row_values(i + 1)
        hospital.append(hospitalStruct(row[0],
                                       row[1],
                                       row[2],
                                       row[3],
                                       row[4],
                                       row[5],
                                       row[6],
                                       row[7],
                                       row[8]))

    return hospital


def loadPatients(sheet):
    """
    Loads Patient data into structs for later use
    """
    tempPatients = getColumn(sheet, 2)
    tempPatients.pop(0)
    patients = []
    for zipcode in tempPatients:
        patients.append(getCoords(formatZip(zipcode)))
    return patients


def getCoords(zipcode):
    zcdb    = ZipCodeDatabase()
    search  = SearchEngine()

    try:
        entry   = zcdb[zipcode]
        tempZip = zipStruct(zipcode,
                            entry.latitude,
                            entry.longitude)
        return tempZip
    except IndexError:
        entry   = search.by_zipcode(zipcode)
        tempZip = zipStruct(zipcode,
                            entry.lat,
                            entry.lng)
        return tempZip


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r


def calculateClosestHospitals(patient, hospitals):
    """
    calculate the closest hospitals to a patient
    returns a list of hospitals sorted in distance
    from patient from shortest to longest
    """
    hospitalList = []

    for hospital in hospitals:
        hospitalList.append(hospitalDistance(haversine(
                                            hospital.zipStruct.latitude,
                                            hospital.zipStruct.longitude,
                                            patient.latitude,
                                            patient.longitude), hospital))

    hospitalList.sort(key=sortFirst)
    return hospitalList


def sortFirst(val):
    """
    indexing function for hospitalList sorting
    """
    return val.distance


def checkProgram(hospital, program):
    """
    checks if a hospital has the desired program
    ex. checking for "liver" programs
    """
    return True if vars(hospital)[program] else False


def findClosestCenter(patient, hospitals, program):
    """
    Completes all calculations to find closest center
    """
    if (patient.latitude or patient.longitude) is None:
        return None

    closestHospitals = calculateClosestHospitals(patient, hospitals)

    for hospital in closestHospitals:
        if checkProgram(hospital.hospital, program):
            return hospital


# Main Function for distance calculation
def main():
    """
    Uses argv 1 for excel file name and argv 2 for
    program to find
    """
    workbook        = loadWorkbook(sys.argv[1])
    patientSheet    = workbook.sheet_by_index(0)
    hospitalSheet   = workbook.sheet_by_index(1)

    hospitals   = loadHospitals(hospitalSheet)
    patients    = loadPatients(patientSheet)

    # Prints distance between center and patient
    # if patient does not exist, None is returned
    for patient in patients:
        center = findClosestCenter(patient, hospitals, sys.argv[2])
        if center is not None:
            print center.distance
        else:
            print None


main()
