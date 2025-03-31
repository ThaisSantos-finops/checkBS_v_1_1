import os
import csv
import re

# Function to check just the deployment.yaml file
def check_deployment(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            # Look for the specific structure of labels in the text
            if '{{- with $.Values.ownershipLabels }}' not in content:
                return ['Missing deployment structure']
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
    return []

# Function to check ownershipLabels in values files
def check_values_labels(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            # Look for the specific structure of ownershipLabels in the text
            if 'ownershipLabels:' not in content or not all(key in content for key in ['businessStructure:', 'director:', 'valueStream:', 'teamName:']):
                return ['Missing ownershipLabels structure']
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
    return []

# Create CSV report
def create_csv_report(report_data, save_path):
    with open(save_path + '/result.csv', 'w', newline='') as csvfile:
        fieldnames = ['Source', 'file_path', 'Missing Info']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in report_data:
            # Extract the repository name from the file path
            repository_name = data['file_path'].split('/')[5]  # Adjust the index as needed
            writer.writerow({'Source': repository_name, 'file_path': data['file_path'], 'Missing Info': data['missing_labels']})

def execute_validation(repo_path, save_path):
   print("Execute validation")
   report_data = []
   for root, dirs, files in os.walk(repo_path):
        for file in files:
            # Consider only deployment files inside 'templates'
            if 'templates' in root and (re.match(r'(?:[a-zA-Z]+-)?deployment(?:-[a-zA-Z]+)?\.yaml', file) or re.match(r'(?:[a-zA-Z]+-)?deployment(?:-[a-zA-Z]+)?\.yml', file)):
                file_path = os.path.join(root, file)
                missing_labels = check_deployment(file_path)
                if missing_labels:
                    report_data.append({'file_path': file_path, 'missing_labels': ', '.join(missing_labels)})
            # Consider only values files outside 'templates'
            elif (file.endswith('values.yaml') or file.endswith('values.yml')):
                file_path = os.path.join(root, file)
                missing_keys = check_values_labels(file_path)
                if missing_keys:
                    report_data.append({'file_path': file_path, 'missing_labels': ', '.join(missing_keys)})
        create_csv_report(report_data, save_path)

# Traverse files and check for inconsistencies
def main():
    # Destination path
    new_path = '/home/thais/PycharmProjects/checkBS_v_1_1/'

    # Base path for charts
    base_path = '/home/thais/PycharmProjects/bees-microservices/charts'
    execute_validation(base_path, new_path)
    

if __name__ == '__main__':
    main() 