import os
import tarfile
from contextlib import closing
from xml.dom import minidom
import xml.etree.ElementTree as ET
import os.path
from pathlib import Path
import sys



def charFields(term:str, child, local_list:list, field:str, ctn):
    '''Receives the parameters to search a field in Characteristics
    block in the XML files. Returns local_list
    with the desired info'''

    # print(field)
    if term in child.tag:
        field_list = [] 
        for char in child.iter():
            if 'Characteristics' in char.tag:
                field_list.append(char.attrib.get('tag'))  
                                           
                if char.attrib.get('tag') == field:
                    # local_list.append(char.text.strip())
                    local_list.insert(ctn, char.text.strip())
                    break

        if len(field_list) > 0: #checking if we have the term in our list, if not, we are adding a string referring to this field            
            # print(field_list) 
            if field not in field_list: #this line changes
                # local_list.append('no_'+field) #this line changes
                local_list.insert(ctn, 'no_'+field) #this line 
                # print(local_list)


def flatten_dict(list_of_records):
    '''Receives a list and returns
    a flatten list to be appended to
    biglist'''

    flat_list = []
    for tag in list_of_records:
        
        # in case the tag is not a dictionary
        if type(tag) is str:
            flat_list.append(tag)
            continue
            
        for k,v in tag.items():
            flat_list.append(v)
            
    return(flat_list)



def sampleParser(base_dir, all_fields):
    """Receives a base dir (path) containing 
    all XML files, and a list of all fields
    of interest. Returns a list containig
    all the desired metadata"""

    pathlist = Path(base_dir).glob('**/*.tgz') #get all tgz files in all subdirectories
    big_list = []
    local_list = []
    ctn = 7 #index to characteristics fields (fixed fields)

    for path in pathlist:

        gse_name = os.path.basename(path).replace('_family.xml.tgz', '')

        with tarfile.open(path) as archive:
            for member in archive:
                if member.isreg() and member.name.endswith('.xml'): # regular xml file

                    with closing(archive.extractfile(member)) as xmlfile:
                        tree = ET.parse(xmlfile)
                        root = tree.getroot()
                        root.tag #ok
                        # print(root.tag)
        
                    
                        for sample in root.iter('{http://www.ncbi.nlm.nih.gov/geo/info/MINiML}Sample'):    
                            if len(local_list) > 0:
                                # flatten dict and append to big_list
                                
                                local_list_flatten = flatten_dict(local_list)
                                    
                                if local_list_flatten not in big_list:    
                                    big_list.append(local_list_flatten)
                                
                                local_list = []
                               

                            
                            for child in sample:

                                #get library-strategy
                                if 'Library-Strategy' in child.tag:
                                    # local_list.append(gse_name)
                                    # local_list.append(sample.attrib)
                                    # local_list.append(child.text)
                                    local_list.insert(0,gse_name)
                                    local_list.insert(1,sample.attrib)
                                    local_list.insert(2,child.text)

                                #get title
                                if 'Title' in child.tag:
                                    # local_list.append(child.text)
                                    local_list.insert(3,child.text)

                                #get GPL 
                                if 'Platform-Ref' in child.tag:
                                    # local_list.append(child.attrib)
                                    local_list.insert(4,child.attrib)
            
                                #get release date - same case below
                                if 'Status' in child.tag:
#                                 print(child.tag)
                                    for char in child.iter():
                                        if 'Release-Date' in char.tag:
                                            # local_list.append(char.text.strip())
                                            local_list.insert(5,char.text.strip())

                                #Get organism and source
                                if 'Channel' in child.tag:
                                    for char in child.iter():
                                        if 'Organism' in char.tag:
                                            # local_list.append(char.text.strip())
                                            local_list.insert(6,char.text.strip())
                                            
                                # #get source          
                                if 'Channel' in child.tag:
                                    for char in child.iter():
                                        if 'Source' in char.tag:
                                            # local_list.append(char.text.strip())
                                            local_list.insert(7,char.text.strip())


                                #Characteristics -> plenty of fields
                                
                                for field in all_fields:
                               
                                    ctn = ctn + 1
                                    # print(ctn)
                                    charFields('Channel', child, local_list, field, ctn)

                               
                               

    for i in big_list:
        print('List length:',len(i))
        break
        
    # print(big_list)
    print('BigList samples:',len(big_list))

    return big_list



def filter_list(big_list, num_len):
    """Receives a list of lists and 
    an integer. Retruns a list of lists
    of correct size"""

    result_list = []
    wrong_list = []

    for sublist in big_list:
        if len(sublist) == int(num_len):
            result_list.append(sublist)
            
        else:
            wrong_list.append(sublist)
    
    return result_list
