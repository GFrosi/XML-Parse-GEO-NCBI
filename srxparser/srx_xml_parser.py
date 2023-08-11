import pandas as pd
import tarfile 
import os
import xml.etree.ElementTree as ET
import os.path
from pathlib import Path
import sys
import tqdm



def open_df(file_name):
    '''open a csv file 
    as dataframe'''

    # df = pd.read_csv(file_name)
    # return df
    return pd.read_csv(file_name, usecols=['GSM'])


def get_srx_adress(df, path_base_dir):
    '''Receives a df with a GSM column. 
    Return a list of tuple containing GSM and its
    respective SRX address'''

    list_gsm = df['GSM'].to_list()
    list_no_dup = list(set(list_gsm))
    print(len(list_no_dup))

    
    # print(list_gsm)
    list_gsm_srx_address = []
    pathlist = Path(path_base_dir).glob('**/*.tgz')
    count = 0

    for path in pathlist:
        t = tarfile.open(path, 'r')
        file_name =t.getnames()
        # print(file_name)
        # sys.exit()

        for file in file_name:
            try:
                f = t.extractfile(file)
            except KeyError:
                print('ERROR: Did not find %s in tar archive' % file)
            else:
                for line in f.readlines():
                    # convert byte-like object to str
                    try:
                        line = line.decode(encoding="ascii", errors="surrogateescape")

                        if "<Sample iid=" in line:
                            gsm = line.replace('<Sample iid="','')[:-3].strip()


                            if gsm in list_gsm:
                                count = 1
                                #print('OK')


                        if '<Relation type="SRA" target=' in line and  count == 1:

                            target  = line.split('=')
                            srx = target[2].replace('"', '') + '='+ target[3].replace("/>",'').replace('"', '').strip()
                            list_gsm_srx_address.append([gsm, srx]) #append gsm as well
                            count = 0
                    except:
                        print("Error in ", file)
                        sys.exit(1)

    return list_gsm_srx_address


def no_dup_list_tuples(list_of_tuples):
    '''This function reveices a list of tuple
    generated by the previous function. Return a
    list without duplicates'''

    no_dup = set(tuple(row) for row in list_of_tuples)
    list_srx_address_complete_nodup = list(no_dup)
    print('list_srx_address_complete_nodup:', len(list_srx_address_complete_nodup))

    return list_srx_address_complete_nodup


def save_gsm_srx(list_srx, out_file_name):
    '''Receives a list of tuples without 
    duplicates and the output file name. 
    Returns a file separated by tab'''
    
    file_counter = 0
    srx_gsm_address_file = open(out_file_name + "_chunk-" + str(file_counter) + ".tsv","w")

    print("file opened" + out_file_name + "_chunk-" + str(file_counter) + ".tsv")
    for cnt, i in enumerate(list_srx):

        line = "\t".join(i)
        line += "\n"
        srx_gsm_address_file.write(line)

        if (cnt + 1) % 1000 == 0:

            file_counter += 1

            srx_gsm_address_file.close()
            print("file closed " + out_file_name + "_chunk-" + str(file_counter -1) + ".tsv")
            srx_gsm_address_file = open(out_file_name + "_chunk-" + str(file_counter) + ".tsv","w")
            print("file opened " + out_file_name + "_chunk-" + str(file_counter) + ".tsv")

    srx_gsm_address_file.close()

    print(out_file_name, 'successful saved')

    


