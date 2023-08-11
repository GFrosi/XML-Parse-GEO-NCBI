import argparse
from sampleparser import sample_parser_xml as pxsample
from sampleparser import df_xml as dx
from gsetitleparser import gse_parser_xml as pxgse
from gpltitleparser import gpl_parser_xml as pxgpl
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys




def main():

    print('Starting XML test...')

    #creating lists to be parsed
    df_char = pd.read_csv(args.char) #char fields
    
    target_fields = df_char['Target'].dropna().tolist()
    catalog_fields = df_char['Catalog'].dropna().tolist()
    cell_fields = df_char['Cell'].dropna().tolist()
    disease_fields = df_char['Disease'].dropna().tolist()
    sex_fields = df_char['Sex'].dropna().tolist()
    all_fields = target_fields + catalog_fields + cell_fields + disease_fields + sex_fields
    print(len(all_fields))
    # print(all_fields)
    # sys.exit()

    # generating biglist for samples, gse and gpl title
    print('Parsing XML files...')
    big_list = pxsample.sampleParser(args.path, all_fields)
    big_list_gse = pxgse.gseParser(args.path)
    big_list_gpl = pxgpl.gplParser(args.path)


    #filtering biglists to get the correct samples according to len_list
    #if the characteristics fields change, you will need to re-check the sample_result length
    sample_result = pxsample.filter_list(big_list, 504) #check size here
    gse_result = pxsample.filter_list(big_list_gse, 2)
    gpl_result = pxsample.filter_list(big_list_gpl, 2)

    #merging dfs
    df_merged = dx.merge_dfs(sample_result, gse_result, gpl_result, all_fields)
    print('Df merged done/ Length:', len(df_merged))

    #concatenating and dropping columns
    print('Concatenating and dropping columns...')
    df_rename = dx.drop_rename_df(df_merged, all_fields, target_fields,catalog_fields,cell_fields,disease_fields,sex_fields)

    #Filtering Human and ChIP-Seq samples
    print('Filtering Human and ChIP-Seq samples')
    df_Hs_chipseq, df_Hs_chipseq_no_dup = dx.filter_Hs_chipseq(df_rename)


    # # Saving the GEO dfs
    # print('Saving Dfs...')
    date = datetime.now().strftime("%Y_%m_%d")
    dx.save_df(df_rename, args.out_df) #whole df without filter
    dx.save_df(df_Hs_chipseq, 'GEO_2023_filtered_Hs_ChIP' + date + '.csv') #filter by Hs and ChIP
    dx.save_df(df_Hs_chipseq_no_dup, 'GEO_2023_filtered_Hs_ChIP_nodup' + date + '.csv') #removing duplicates (GSM col)

    print("Dataframes saved, done!")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="A script to create a dataframe from xmls files related to Chip-Seq and Homo sapiens from GEO-NCBI")

    parser.add_argument('-p', '--path', action="store",
                        type=Path,
                        help='The root path (base dir) to parse function. It will return a list of list for each sample for each series',
                        required=True)

    parser.add_argument('-c', '--char', action="store",
                        type=Path,
                        help='csv file containing Target, Chip-ant, Cell, Disease and Sex cols asociated to all desired fields to be extracted from Characteristics',
                        required=True)

    parser.add_argument('-d', '--out_df', action="store",
                        type=Path,
                        help='output file with xml results',
                        required=True)


    args = parser.parse_args()
    main()