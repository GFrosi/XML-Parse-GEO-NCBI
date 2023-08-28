import sys

#=================================================
#Script to generate the wget command to dowload
#the xml files (for GSM) to fill the Histones_DBs
#metadata file
#==================================================



def main():

    xml_sample = open(sys.argv[1], 'r')

    print('#!bin/bash')
    for gsm in xml_sample:
        gsm  = str(gsm.strip())
        gsm_xml = gsm+'.xml'
        gsm_log = gsm+'.log'

        gsm_adr = 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc='+gsm.lower()+'&targ=self&view=full&form=xml'

        #Checking 
        # print('gsm:{0}, gsm_xml:{1}, gsm_log:{2}, gsm_adr:{3}'.format(gsm,gsm_xml,gsm_log,gsm_adr))
        print('wget -O {0} -o {1} {2}'.format(gsm_xml,gsm_log,gsm_adr))
        print('sleep 3')



if __name__ == "__main__":


    main()