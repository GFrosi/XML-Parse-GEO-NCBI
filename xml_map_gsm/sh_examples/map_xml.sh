#!/bin/bash
#SBATCH --time=5:00:00
#SBATCH --account=
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --mail-user=user@usherbrooke.ca
#SBATCH --mail-type=END
#SBATCH --job-name=map-missed-xml


module load python/3.8.0
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip

pip install --no-index -r requirements.txt



echo "Starting parse xml"

python map_gsm_missed_metadata.py GEO_metadata_xml_624.tsv Histones_basedDBs_57566_2023_08_03.tsv

echo "Finished parse xml"
