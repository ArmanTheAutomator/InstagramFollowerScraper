import pandas as pd
import os
from sys import exit

def read_txt(file_name, warning=False, exit_on_missing_file=False):
    data = []
    file_dir = os.getcwd() + "/" + file_name + ".txt"
    try:
        with open(file_dir, "r") as file:
            str_data = file.read()
            list = str_data.split("\n")
            for line in list:
                data.append(line.strip())
    except:
        if warning:
            print(f'{file_name} file not found in {file_dir}')
        if exit_on_missing_file:
            exit()
    # data = ['a', 'b', 'c', 'd']
    return data

def write_to_txt(data, lable=False, file_name='Output'):
    file_dir = os.getcwd() + "/" + file_name + ".txt"
    try:
        with open(file_dir, "w") as file:
            # data = ['a', 'b', 'c', 'd']
            if lable:
                file.write(f'{lable}\n')
            for line in data:
                file.write(f'{line}\n')
    except PermissionError:
        print(f'Permission error, please close the file {file_dir}')
        exit()
    except:
        print(f'{file_name} file not found in {file_dir}')
        exit()

def read_csv(file_name, list_of_dictionaries = False, exit_on_empty=False):
    file_dir = os.getcwd() + "/" + file_name + ".csv"
    data = []
    try:
        df = pd.read_csv(file_dir)
        if list_of_dictionaries:
            data = df.to_dict('records')
        else:
            data = df.values.tolist()
    except:
        if exit_on_empty:
            print('csv file is empty')
            exit()
    # Returning data as a list
    return data

def write_to_csv(data, labels=None, file_name = 'output', alternative_filename = ''):
    file_dir = os.getcwd() + "/" + file_name + ".csv"
    if alternative_filename:
        alt_file_dir = os.getcwd() + "/" + alternative_filename + ".csv"
        
    header = True if labels else False
    
    try:
        pd.DataFrame(data, columns=labels).to_csv(file_dir, index=False, header=header)
    except PermissionError:
        if alternative_filename != '':
            pd.DataFrame(data, columns=labels).to_csv(alt_file_dir, index=False, header=header)
        else:
            print(f"PermissionError: Can't write to {file_dir} file, Close the csv file first")
            exit()

def write_to_excel(data, labels=None, filename = 'output.xlsx', alternative_filename= ''):
    header = True if labels else False
    
    try:
        pd.DataFrame(data, columns=labels).to_excel(filename, index=False, header=header)
    except PermissionError:
        if alternative_filename != '':
            pd.DataFrame(data, columns=labels).to_excel(alternative_filename, index=False, header=header)
        else:    
            print("PermissionError: Can't write to excel, Close the excel file first")
            exit()
        
