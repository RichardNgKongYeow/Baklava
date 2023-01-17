import json
import datetime
import pandas as pd
import os
import glob
import csv
from csv import writer
from csv import reader



def generate_file_name(report_name:str):
    e = datetime.datetime.now()
    date="%s-%s-%s" % (e.day, e.month, e.year)
    time="%s.%s.%s" % (e.hour, e.minute, e.second)
    file_name=f"{report_name}D{date}T{time}.csv"
    return file_name

def write_to_json(data:list,file_name):
    with open(file_name, 'w') as file_object:  #open the file in write mode
        json.dump(data, file_object)   # json.dump() function to stores the set of numbers in numbers.json file

def write_to_csv(data:list,file_name,columns=[]):
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(file_name, index=False)

def find_csv(name):
    path = os.getcwd()
    extension = 'csv'
    os.chdir(path)
    result = glob.glob((name+'*.{}').format(extension))
    return result[0]

def read_csv(name)->list:
    file=open(find_csv(name))
    csvreader=csv.reader(file)
    header=next(csvreader)
    rows=[]
    for row in csvreader:
        rows.append(row)
    return rows


def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)

def add_column_in_csv(input_file, output_file, transform_row):
    """ Append a column in existing csv using csv.reader / csv.writer classes"""
    # Open the input_file in read mode and output_file in write mode
    with open(input_file, 'r') as read_obj, \
            open(output_file, 'w', newline='') as write_obj:
        # Create a csv.reader object from the input file object
        csv_reader = reader(read_obj)
        # Create a csv.writer object from the output file object
        csv_writer = writer(write_obj)
        # Read each row of the input csv file as list
        for row in csv_reader:
            # Pass the list / row in the transform function to add column text for this row
            transform_row(row, csv_reader.line_num)
            # Write the updated row / list to the output file
            csv_writer.writerow(row)