import requests
import sys
import pandas as pd
import os
import shutil
import glob
import argparse

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('input_metabolomics_features', help='input_metabolomics_features')
    parser.add_argument('input_metabolomics_feature_metadata', help='input_metabolomics_feature_metadata')
    parser.add_argument('import_microbial_features', help='import_microbial_features')
    parser.add_argument('import_microbial_feature_metadata', help='import_microbial_feature_metadata')
    parser.add_argument('output_folder', help='output_folder')
    parser.add_argument("conda_activate_bin")
    parser.add_argument("conda_environment")
    args = parser.parse_args()

    #Checking if header names are appropriate, if not, then lets correct them
    temp_reformatted_metadata_filename = "reformatted_metabolomics_identifications.tsv"
    metabolomics_metadata_df = pd.read_csv(args.input_metabolomics_feature_metadata, sep="\t")
    if "Feature Information" in metabolomics_metadata_df:
        print("Copying")
        shutil.copyfile(args.input_metabolomics_feature_metadata, temp_reformatted_metadata_filename)
    #Checking for scan numbers in the header
    elif "#Scan#" in metabolomics_metadata_df:
        headers = list(metabolomics_metadata_df.keys())
        metabolomics_metadata_df["Feature Information"] = metabolomics_metadata_df["#Scan#"]
        headers = ["Feature Information"] + headers
        metabolomics_metadata_df.to_csv(temp_reformatted_metadata_filename, headers=headers, sep="\t", index=False)
    else:
        print("Copying")
        shutil.copyfile(args.input_metabolomics_feature_metadata, temp_reformatted_metadata_filename)

    #Making sure the input files are qza

    #TODO: Implement this by checking extensions


    #Running Qiime2 mmvec
    LATENT_DIM = 5
    LEARNING_RATE = 0.001
    EPOCHS = 10

    mmvec_output_directory = args.output_folder

    metabolite_qza = args.input_metabolomics_features
    microbiome_qza = args.import_microbial_features

    local_metabolite_metadata_filename = temp_reformatted_metadata_filename
    local_microbial_metadata_filename = args.import_microbial_feature_metadata

    conditional_biplot = os.path.join(mmvec_output_directory, "conditional_biplot.qza")
    output_emperor = os.path.join(mmvec_output_directory, "emperor.qzv")
    

    all_cmd = []

    all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
        qiime rhapsody mmvec \
        --p-latent-dim {} \
        --p-learning-rate {} \
        --p-epochs {} \
        --i-microbes {} \
        --i-metabolites {} \
        --output-dir {}".format(args.conda_activate_bin, args.conda_environment, \
        LATENT_DIM, LEARNING_RATE, EPOCHS, \
        metabolite_qza, microbiome_qza, mmvec_output_directory))

    all_cmd.append("LC_ALL=en_US && export LC_ALL && source {} {} && \
        qiime emperor biplot \
        --i-biplot %s \
        --m-sample-metadata-file %s \
        --m-feature-metadata-file %s \
        --o-visualization %s \
        --p-ignore-missing-samples" % (conditional_biplot, local_metabolite_metadata_filename, local_microbial_metadata_filename, output_emperor))


    # """Calling remote server to do the calculation"""
    # SERVER_BASE = "http://dorresteinappshub.ucsd.edu:5025"
    # files = {'microbial_qza': open(input_microbial_qza, 'rb'), \
    # 'metabolite_qza': open(input_metabolomics_qza, 'rb'), \
    # 'microbial_metadata': open(input_microbial_metadata, 'rb'), \
    # 'metabolite_metadata': open(temp_reformatted_metadata_filename, 'rb'), \
    # }

    # r_post = requests.post(SERVER_BASE + "/mmvec", files=files)
    # output_tgz = os.path.join(output_folder, 'rhapsody_results.tgz')
    # open(output_tgz, 'wb').write(r_post.content)
    # temp_folder = "temp"
    # try:
    #     os.mkdir(temp_folder)
    # except:
    #     print("can't make temp folder")
    # os.system("tar xzvf %s -C %s" % (output_tgz, temp_folder))


    # for qza_file in glob.glob(os.path.join(temp_folder, "**", "*.qza"), recursive=True):
    #     print(qza_file)
    #     shutil.copy(qza_file, os.path.join(output_folder, os.path.basename(qza_file)))
    # for qzv_file in glob.glob(os.path.join(temp_folder, "**", "*.qzv"), recursive=True):
    #     print(qza_file)
    #     shutil.copy(qzv_file, os.path.join(output_folder, os.path.basename(qzv_file)))

    for cmd in all_cmd:
        os.system(cmd)

if __name__ == "__main__":
    main()
