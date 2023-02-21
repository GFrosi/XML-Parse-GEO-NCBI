# XML-Parse-GEO-NCBI
Script to download and parse the XMLs files (MINiML formatted file) referring to experiments (GSEs) deposited in the public database (GENE EXPRESSION OMNIBUS - GEO/NCBI) 

# Requirements
```python 3```, and see requirements.txt (available)


We have six main scripts:

1) get-xml.py (to download the xmls files related to each series from GEO-NCBI)
2) main-parse.py (parse xmls files using several tags (characteristics fields)
3) main-srx.py (parse xmls files to recover the SRX information to access the SRR ids)
4) main-srr.py (web scraping to recover the SRR ids for each sample (GSM)) 


- get-xml.py

You should pass as the first argument a list of address - .txt file (i.e ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE156nnn/GSE156377/miniml/GSE156377_family.xml.tgz). The second argument is the output root path (i.e $PWD/GEO). New subdirectories will be created every 300 files downloaded within the directory specified on the command line (i.e $PWD/GEO/GEO_1).


The command line:
```
python get-xml.py list-ftp-address.txt 
path_to_GEO_dir
```


- check_char_fields_GEO.py

This script receives a path to the XML files, and returns all fields associated to Characteristics char.tag with a GSE as example for each field in a tsv format. 

You should manipulate this output file to select the desired fields to create Target,Catalog,Cell,Disease,Sex columns using parser_xml.py. The filtered csv file should be like exemplified below: 

| Target | Catalog | Cell | Disease | Sex |
| ------ | ------- | ---- | ------- | --- |
| antibody | catalog number | cell | cancer type | donor_sex |


To check the Characteristics fields used in this version, please check `input_check_char/Characteristics_fields_2023-01-31.csv`

To run the script:
```
python check_char_fields_GEO.p PATH_TO_XMLs
```

To run via slurm please check `sh_examples` folder (run-char-xml.sh). 


- parser_xml.py

This script will extract 10 fixed tags from XMLs. In addition, all Characteristics fields selected by the user will be placed into four additional columns. The fixed tags are:

- 1 GSE
- 2 GSM
- 3 Library-strategy
- 4 Release-date
- 5 GSM_title
- 6 Organism
- 7 Source
- 8 GPL
- 9 GSE-title
- 10 GPL-title

The additional columns:

- 11 Target
- 12 ChIP-antibody-catalog
- 13 Cell
- 14 Disease
- 15 Sex_GEO

**Attention**: If we have more the one char_field for the same category (e.g chip_antibody and antibody for Target), the information will be concatenated by '&&&'.


The script returns three output files:

- 1 GEO_xml_2023_fields.csv (all extracted GSM available in the XMLs)
- 2 GEO_2023_filtered_Hs_ChIP.csv (all GSMs associated to Human and ChIP-Seq)
- 3 GEO_2023_filtered_Hs_ChIP_nodup.csv (no duplicated GSM)


```
usage: main-parser.py [-h] -p PATH -c CHAR -d OUT_DF

A script to create a dataframe from xmls files related to Chip-Seq and Homo sapiens from GEO-NCBI

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  The root path (base dir) to parse function. It will return a list of list for each sample for each series
  -c CHAR, --char CHAR  csv file containing Target, Chip-ant, Cell, Disease and Sex cols asociated to all desired fields to be extracted
                        from Characteristics
  -d OUT_DF, --out_df OUT_DF
                        output file with xml results
```

To run via slurm please check `sh_examples` folder (run-parse-xml.sh)


- main-srx.py

You should pass a csv file with a GSM (samples) column as -d (--df_path). You also should pass the directory with the downloaded XMLs files (-p, --path_xml). For each gsm the SRX information will be scrapped. The last argument (-o, --out_file_name) is the output file name. 

The command line: 
```
python main-srx.py -d $PATH/df_with_GSM_column.csv -p $PATH_DIR_XML_FILES -o $PATH/output_file_name.csv
```


```
usage: main-srx.py [-h] -d DF_PATH -p PATH_XML -o OUT_FILE_NAME

A script to parse XMLs from GEO-NCBI. Returns the GSM and SRX information as
a tsv file.

optional arguments:
  -h, --help            show this help message and exit
  -d DF_PATH, --df_path DF_PATH
                        The absolute path to open a df with GSM column
  -p PATH_XML, --path_xml PATH_XML
                        The root path (base dir) to srx parse function. It
                        will return a list of list for each sample for each
                        series
  -o OUT_FILE_NAME, --out_file_name OUT_FILE_NAME
                        The output name file to save the output with gsm and
                        srx address
```

To run via slurm: see previous topic
The command line to run via slurm:

```
python main-srx.py -d $PATH/df_with_GSM_column.csv -p $PATH_DIR_XML_FILES -o $PATH/DIR_RESULT/output_file_name #(Do not put extension here)
```

4) main-srr.py

The requirements.txt file is available in srrparser folder.

The output files generated by main-srx.py will be passed here. You shoud generate the .sh files with the command line to run the main-srr.py. The run_srr_chunck.sh files will be generated by create_srr_run.py. You also should pass a run_template.sh file (available) as the third argument.

To run create_srr_run.py:

```
python create_srr_run.py PATH/SRX_OUTPUT run_template.sh (you should adjust the run_template with your slurm information - account)
```

After run the create_srr.py you can submit all of the run_chunk.sh.

Example run.sh file generated by create_srr.py:

```
#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --account=
#SBATCH --cpus-per-task=8
#SBATCH --mem=20G
#SBATCH --job-name=get-srr

module load python/3.8.0
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip

pip install --no-index -r PATH/srrparser/requirements.txt
pip install retry

python $PATH/main-srr.py -p PATH/SRX_OUTPUT/srx_chuncked_0.tsv -o output.csv
```

The main-srr.py:

```
usage: main-srr.py [-h] -p PATH -o OUT

A script to return a file with the GEO-NCBI samples (GSM) with their
respectives SRR Ids

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to the dataframe containing the GSM and SRX
                        address generated by main-srx.py (file separated by
                        tab)
  -o OUT, --out OUT     name of output file
```

For each `run_chunk` a `srr_srx.output.csv` will be generated. If you want to concatenate the **srx_srr outputs** you can run the `concat-csv.sh` script available in `srrparser`.