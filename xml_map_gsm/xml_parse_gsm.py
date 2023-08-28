import os
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup,NavigableString, Tag
import sys

##############################################################
'''Script to parse html from GEO (GSM)'''
##############################################################



def list_of_list_to_df(big_list):

    cols = ['Release-date', 'Library-strategy', 'Organism-geo', 'Gpl', 
    'Gpl-title', 'Gse-geo', 'Gse-title', 'Gsm', 'Gsm-title',
    'Cell', 'Disease', 'Sex-geo', 'Source', 'Chip-antibody-catalog', 'Target', 'Adress',
     'Srx', 'Srr']
    
    df = pd.DataFrame(big_list, columns=cols) 
    df['Srx'] = [','.join(map(str,l)) for l in df['Srx']]
    df['Srr'] = [','.join(map(str,l)) for l in df['Srr']]
    df.replace('', '---', inplace=True)

    df.to_csv('GEO_metadata_xml_1010.tsv', index=False, sep='\t')




def xmlParse(input, char_fields):

    pathlist = Path(input).glob('*.xml')
    big_list = []
    local_list = []
    ctn = 0

    df_char = pd.read_csv(char_fields) #char fields
    
    target = df_char['Target'].dropna().tolist()
    chip_ant = df_char['Catalog'].dropna().tolist()
    cell = df_char['Cell'].dropna().tolist()

    for path in pathlist:
        print(path)
        ctn+=1
        
        # local_list = []

        dict_meta = {'Release-date':'----',
            'Library-strategy':'----',
            'Organism-geo':'----',
            'Gpl':'----',
            'Gpl-title':'----',
            'Gse-geo':'----',
            'Gse-title':'----',
            'Gsm':'----',
            'Gsm-title':'----',
            'Cell':'----',
            'Disease':'----',
            'Sex-geo':'----',
            'Source':'----',
            'Chip-antibody-catalog':'----',
            'Target':'----',
            'Address':'----',
            'Srx':[],
            'Srr':[]

        }

        soup = BeautifulSoup(open(path,'r'), 'lxml')

        #GSM
        file_name = os.path.basename(path)
        gsm = file_name.split('.')[0] #getting gsm name
        dict_meta['Gsm'] = gsm


        #Finding them
        for br in soup.findAll('br'):
            next_s = br.nextSibling
            if not (next_s and isinstance(next_s,NavigableString)):
                continue
            
            next2_s = next_s.nextSibling
            if next2_s and isinstance(next2_s,Tag) and next2_s.name == 'br':
                text = str(next_s).strip()
                if text:
                    
                    #target
                    for ele in target:
                        if ele == text.split(':')[0]:
                            # local_list.append(text.split(':')[1].strip())    
                            dict_meta['Target'] = text.split(':')[1].strip()
                            # print("Found:", next_s)

                    #antibody    
                    for ant in chip_ant:
                        if ant == text.split(':')[0]:
                            # local_list.append(text.split(':')[1].strip())
                            dict_meta['Chip-antibody-catalog'] = text.split(':')[1].strip()


                    #cell type
                    for ct in cell:
                        if ct == text.split(':')[0]:
                            # local_list.append(text.split(':')[1].strip())
                            dict_meta['Cell'] = text.split(':')[1].strip()

                  

        #Other metadata fields
        for tables in soup.findAll('table',{"cellpadding":"2"}):
            for tr in tables.findAll('tr',{"valign" : "top"}):

                try:                
                    #GSE and GSE title
                    if 'GSE' in tr.text:
                        a = [] 
                        for td in tr.findAll('td'):
                            a.append(td.text)
                            
                        dict_meta['Gse-geo'] = a[-2]
                        dict_meta['Gse-title'] = a[-1]
                     
                        a= []
        
                    #Release date
                    if 'Submission date' in tr.text:
                        a = [] 
                        for td in tr.findAll('td'):
                            a.append(td.text)
                        
                        dict_meta['Release-date'] = a[-1]
                        a= []

                    #Organism
                    if 'Organism' in tr.text:
                        a = [] 
                        for td in tr.findAll('td'):
                            a.append(td.text)

                        dict_meta['Organism-geo'] = a[-1]
                        a= []

                    #Library strategy
                    if 'Library strategy' in tr.text:
                        a = [] 
                        # print(tr.text)
                        for td in tr.findAll('td'):

                            a.append(td.text)

                        # local_list.append(a[-1])
                        if len(a[-1]) < 20: #sometimes we have library strategy in description field 
                            dict_meta['Library-strategy'] = a[-1] 
                            a= []


                    #GSM title
                    if 'Title' in tr.text:
                        a = []   
                        for td in tr.findAll('td'):
                            a.append(td.text)

                        dict_meta['Gsm-title'] = a[-1]
                        a= []

                    
                    #platform ID - GPL
                    if 'Platform ID' in  tr.text:
                        a = []   
                        for td in tr.findAll('td'):
                            a.append(td.text)

                        dict_meta['Gpl'] = a[-1]
                        a= []
                    

                    #GPL title
                    if 'Instrument model' in  tr.text:
                        a = [] 
                        for td in tr.findAll('td'):
                            a.append(td.text)

                        dict_meta['Gpl-title'] = a[-1]
                        a= []

                    #Source name
                    if 'Source name' in  tr.text:
                        a = [] 
                        for td in tr.findAll('td'):
                            a.append(td.text)

                        dict_meta['Source'] = a[-1]
                        a= []

                    
                    if 'SRX' in tr.text:
                        a=[]
                        for td in tr.findAll('td'):
                            a.append(td.text)
                        
                        dict_meta['Srx'].append(a[-1])
                        a= []


                    #SRX adress
                    for link in soup.findAll('a', href=True):
                        if 'https://www.ncbi.nlm.nih.gov/sra?term=SRX' in link['href']:
                            a = []
                            a.append(link['href'])
                            break
                    
                    dict_meta['Address'] = a[-1]
                    a= []


                    #SRA
                    if 'Characteristics' in tr.text:
                        a = [] 
                        for td in tr.findAll('td'):
                            # a.append(td.text)
                            if 'sra' in td.text:
                                dict_meta['Srr'].append(td.contents[0].strip().split(':')[1].strip()) #get first ele before br; manipulate to get just SRA (i.e sra sample accession: SRS183511)
                  
                            if 'disease' in td.text:
                                # print(type(td.text))
                                content = td.contents
                                for i in content:
                                    if 'disease' in i:
                                        # print(i.split(':')[1].strip())
                                        dict_meta['Disease'] = i.split(':')[1].strip()

                        
                            if 'sex' in td.text:
                                # print(type(td.text))
                                content = td.contents
                                for i in content:
                                    if 'sex' in i:
                                        # print(i.split(':')[1].strip())
                                        dict_meta['Sex-geo'] = i.split(':')[1].strip()

                except:
                    print('This xml in problematic',path)
                    continue

        # print(len(dict_meta))
        # print(dict_meta)
        # sys.exit()            
        local_list = [i for i in dict_meta.values()] #dict to list
        # print(len(local_list))
        # print(local_list)
        # sys.exit()

        big_list.append(local_list) #list of lists
    
    print('Total parsed files: ',ctn)
    return big_list



def main():

    input = sys.argv[1] #path to xml
    char_fields = sys.argv[2] #fields to create target, chip-cat .... columns
    big_list = xmlParse(input,char_fields)
    # sys.exit()
    list_of_list_to_df(big_list)



if __name__ == "__main__":



    main()

