#!/bin/bash
#SBATCH --time=48:00:00
#SBATCH --account=
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --mail-user=user@usherbrooke.ca
#SBATCH --mail-type=END
#SBATCH --job-name=parse-xml


module load python/3.8.0
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip

pip install --no-index -r requirements.txt



echo "Starting parse xml"

python xml_parse_gsm.py backup_mp2b_project/GEO_files/XML-files-webscrp/XML_missed_gsm_1177/xml_2023 backup_mp2b_project/GEO_files/XML-files-webscrp/Characteristics_fields_2023-01-31.csv

echo "Finished parse xml"
