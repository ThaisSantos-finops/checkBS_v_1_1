import os
import csv
import re
import yaml
import json
import subprocess
from pathlib import Path
from .helper.log import log_info, log_error, log_warning, log_debug

debug_file = open("debug.txt", "w")

# Function to load labels from CSV
def load_labels_from_csv(input_path):
    """
    Loads labels from a CSV file.
    
    Args:
        input_path (str): Path to the CSV file.
        
    Returns:
        list: List of dictionaries containing labels and file paths.
    """
    result = []
    with open(input_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            result.append({
                'file_paths': row['path'].split(';'),
                'labels': {
                    'businessStructure': row['businessStructure'],
                    'director': row['director'],
                    'valueStream': row['valueStream'],
                    'teamName': row['teamName']
                }
            })
    return result

# Function to build the complete file path
def build_file_path(repo_path, file_path):
    """
    Builds the complete file path.
    
    Args:
        repo_path (str): Repository path.
        file_path (str): Relative file path.
        
    Returns:
        str: Complete file path.
    """
    repo_path_cleaned = repo_path.strip()
    file_path_cleaned = file_path.strip()
    if file_path_cleaned.startswith('/'):
        file_path_cleaned = file_path_cleaned[1:]
    
    return os.path.join(repo_path_cleaned, file_path_cleaned)

# Function to find the values.yaml file
def find_values_file(deployment_file_path):
    """
    Finds the values.yaml or values.yml file.
    
    Args:
        deployment_file_path (str): Path to the deployment file.
        
    Returns:
        str: Path to the values file or None if not found.
    """
    values_file_dir = os.path.dirname(os.path.dirname(deployment_file_path))
    for filename in ['values.yaml', 'values.yml']:
        potential_path = os.path.join(values_file_dir, filename)
        if os.path.exists(potential_path):
            return potential_path
    return None

# Function to add or update labels in the values.yaml file
def update_values_file(values_file_path, labels):
    """
    Updates labels in the values.yaml file.
    
    Args:
        values_file_path (str): Path to the values file.
        labels (dict): Dictionary of labels to be added.
    """
    try:
        with open(values_file_path, 'r') as file:
            values_content = yaml.safe_load(file) or {}

        # Update or add the 'ownershipLabels' key with the new labels
        values_content['ownershipLabels'] = labels

        with open(values_file_path, 'w') as file:
            yaml.dump(values_content, file, default_flow_style=False, sort_keys=False)
        log_info(f"Successfully updated values file: {values_file_path}")
    except Exception as e:
        log_error(f"Error updating values file {values_file_path}: {e}")
        raise

# Function to update the deployment file
def update_deployment_file(deployment_file_path):
    """
    Updates the deployment file with labels.
    
    Args:
        deployment_file_path (str): Path to the deployment file.
    """
    try:
        log_info(f"Processing deployment: {deployment_file_path}")
        
        # Primeiro, verificamos se já existe algum bloco ownershipLabels no arquivo
        # Usamos a função check_ownership_labels_exists para uma verificação mais robusta
        exists, count = check_ownership_labels_exists(deployment_file_path)
        if exists:
            log_info(f"Deployment file {deployment_file_path} already has {count} ownershipLabels block(s). No changes needed.")
            return
            
        # Se não existe um bloco ownershipLabels, continuamos com o processamento normal
        with open(deployment_file_path, 'r') as file:
            content = file.readlines()

        # Define patterns to identify the ownershipLabels structure
        ownership_labels_patterns = [
            re.compile(r'^\s*{{-?\s*with\s*\.?Values\.ownershipLabels\s*}}\s*$'),  # Matches both {{- with .Values... and {{- with $.Values...
            re.compile(r'^\s*{{-?\s*toYaml\s*\..*\s*}}\s*$'),                      # Matches {{ toYaml . | indent 4 }} and variants
            re.compile(r'^\s*{{-?\s*end\s*}}\s*$')                                 # Matches {{- end }} and {{ end }}
        ]
        label_keys_to_remove = ['businessStructure', 'director', 'teamName', 'valueStream']

        # Iterate through the content to find all 'metadata:' sections
        i = 0
        metadata_sections_found = 0
        labels_sections_updated = 0
        
        while i < len(content):
            if content[i].strip() == 'metadata:':
                metadata_sections_found += 1
                log_debug(f"Found metadata section at line {i+1}")
                
                # Find the indentation of 'metadata:'
                metadata_indentation = len(re.match(r"^\s*", content[i]).group())
                j = i + 1
                labels_section_found = False

                # Se não existe um bloco ownershipLabels, procuramos pela seção labels
                while j < len(content):
                    line_indentation = len(re.match(r"^\s*", content[j]).group())
                    # If the current line is at the same indentation level as 'metadata:', we stop
                    if line_indentation <= metadata_indentation and j > i + 1:
                        break

                    if content[j].strip() == 'labels:' and line_indentation == metadata_indentation + 2:
                        labels_section_found = True
                        labels_sections_updated += 1
                        log_debug(f"Found labels section at line {j+1}")
                        
                        # Remove any existing ownershipLabels blocks
                        k = j + 1
                        while k < len(content):
                            # If we've moved out of the labels section, break
                            line_indent = len(re.match(r"^\s*", content[k]).group())
                            if line_indent <= line_indentation and k > j + 1:
                                break
                                
                            # Check if this line starts an ownershipLabels block
                            if any(pattern.match(content[k]) for pattern in ownership_labels_patterns[:1]):
                                log_debug(f"Found ownershipLabels block at line {k+1}")
                                # Found the start of an ownershipLabels block
                                start_k = k
                                # Find the end of the block
                                while k < len(content):
                                    if any(pattern.match(content[k]) for pattern in ownership_labels_patterns[2:]):
                                        # Found the end of the block
                                        k += 1
                                        break
                                    k += 1
                                # Remove the entire block
                                log_debug(f"Removing ownershipLabels block from line {start_k+1} to {k}")
                                del content[start_k:k]
                                continue
                            
                            # Check for individual ownership label keys
                            line_strip = content[k].strip()
                            if any(key + ':' in line_strip for key in label_keys_to_remove):
                                log_debug(f"Removing individual label at line {k+1}: {line_strip}")
                                del content[k]
                                continue
                                
                            k += 1
                            
                        # Insert the 'ownershipLabels' structure with the correct indentation
                        log_debug(f"Inserting new ownershipLabels block at line {k+1}")
                        helm_labels_structure_indented = ' ' * (line_indentation + 2) + '{{- with $.Values.ownershipLabels }}\n'
                        helm_labels_structure_indented += ' ' * (line_indentation + 2) + f'{{{{- toYaml . | nindent {2 + line_indentation} }}}}\n'
                        helm_labels_structure_indented += ' ' * (line_indentation + 2) + '{{- end }}\n'
                        content.insert(k, helm_labels_structure_indented)
                        break  # No need to search further after 'labels:'
                    j += 1

                # If 'labels:' was not found, insert 'labels:' and the Helm structure
                if not labels_section_found:
                    labels_sections_updated += 1
                    log_debug(f"No labels section found, inserting new section after line {i+1}")
                    labels_structure = ' ' * (metadata_indentation + 2) + 'labels:\n'
                    helm_labels_structure_indented = ' ' * (metadata_indentation + 4) + '{{- with $.Values.ownershipLabels }}\n'
                    helm_labels_structure_indented += ' ' * (metadata_indentation + 4) + f'{{{{- toYaml . | nindent {4 + metadata_indentation} }}}}\n'
                    helm_labels_structure_indented += ' ' * (metadata_indentation + 4) + '{{- end }}\n'
                    content.insert(i + 1, labels_structure + helm_labels_structure_indented)
                    i += len((labels_structure + helm_labels_structure_indented).splitlines())  # Update the index i to continue after the new insertion

            i += 1

        # Save the file with the new labels inserted
        with open(deployment_file_path, 'w') as file:
            file.writelines(content)
            
        log_info(f"Successfully updated deployment file: {deployment_file_path}")
        log_info(f"Found {metadata_sections_found} metadata sections and updated {labels_sections_updated} labels sections")
    except Exception as e:
        log_error(f"Error updating deployment file {deployment_file_path}: {e}")
        raise

# Function to verify the Helm template
def verify_helm_template(chart_dir):
    """
    Verifies if the Helm template is correct.
    
    Args:
        chart_dir (str): Helm chart directory.
        
    Returns:
        bool: True if the template is correct, False otherwise.
    """
    try:
        log_info(f"Running helm template for verification in {chart_dir}")
        subprocess.run(["helm", "template", chart_dir], check=True)
        log_info(f"Helm template completed successfully in {chart_dir}")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Error running helm template in {chart_dir}: {e}")
        return False

# Function to process a single file
def process_file(repo_path, file_path, labels):
    """
    Processes a single file.
    
    Args:
        repo_path (str): Repository path.
        file_path (str): Relative file path.
        labels (dict): Dictionary of labels to be added.
    """
    full_file_path = build_file_path(repo_path, file_path)
    
    if not os.path.exists(full_file_path):
        log_warning(f"File not found: {full_file_path}. Skipping to next file.")
        return
        
    # Verificar se já existe um bloco ownershipLabels no arquivo
    exists, count = check_ownership_labels_exists(full_file_path)
    if exists:
        log_info(f"File {full_file_path} already has {count} ownershipLabels block(s). Skipping deployment update.")
    else:
        try:
            update_deployment_file(full_file_path)
        except Exception as e:
            log_error(f"Error updating deployment file {full_file_path}: {e}")
            return
    
    # Find and update the values file
    values_file_path = find_values_file(full_file_path)
    if values_file_path:
        log_info(f"Updating values file: {values_file_path}")
        try:
            update_values_file(values_file_path, labels)
        except Exception as e:
            log_error(f"Error updating values file {values_file_path}: {e}")
    else:
        log_warning(f"Values file not found for {full_file_path}")
    
    # Verify the Helm template
    if values_file_path:
        chart_dir = os.path.dirname(values_file_path)
        try:
            verify_helm_template(chart_dir)
        except Exception as e:
            log_error(f"Error verifying Helm template in {chart_dir}: {e}")

# Function to check if ownershipLabels block exists
def check_ownership_labels_exists(file_path):
    """
    Verifica se já existe o bloco {{- with $.Values.ownershipLabels }} independente da indentação.
    
    Args:
        file_path (str): Caminho do arquivo a ser verificado.
        
    Returns:
        tuple: (bool, int) - Indica se o bloco existe e quantos blocos foram encontrados.
    """
    try:
        log_info(f"Verificando existência de blocos ownershipLabels em: {file_path}")
        
        # Carrega o conteúdo do arquivo
        with open(file_path, 'r') as file:
            content = file.read()
            
        # Define o padrão para identificar a estrutura ownershipLabels independente da indentação
        ownership_pattern = re.compile(r'{{-?\s*with\s*\.?Values\.ownershipLabels\s*}}')
        
        # Encontra todas as ocorrências do padrão
        matches = ownership_pattern.findall(content)
        count = len(matches)
        
        # Retorna se existe pelo menos um bloco e quantos blocos foram encontrados
        exists = count > 0
        log_info(f"Arquivo {file_path}: {'Contém' if exists else 'Não contém'} blocos ownershipLabels. Total: {count}")
        
        return exists, count
    except Exception as e:
        log_error(f"Erro ao verificar blocos ownershipLabels em {file_path}: {e}")
        return False, 0

# Main function to execute the fix
def execute_fix(repo_path, input_path, fix_duplicates_only=False, skip_duplicate_fix=False):
    """
    Executes the file fixes.
    
    Args:
        repo_path (str): Repository path.
        input_path (str): Path to the input CSV file.
        fix_duplicates_only (bool): If True, only fix duplicate ownership labels without updating values.
        skip_duplicate_fix (bool): If True, skips the duplicate fix step (useful when it's already been done).
    """
    log_info(f"Starting label update process. Repository: {repo_path}, Input file: {input_path}")
    try:
        data = load_labels_from_csv(input_path)
        log_info(f"Loaded {len(data)} entries from CSV file")
        
        # Manter um registro de arquivos já processados para evitar duplicações
        processed_files = set()
        
        for item in data:
            log_info(f"Processing files: {item['file_paths']}")
            for file_path in item['file_paths']:
                full_file_path = build_file_path(repo_path, file_path)
                
                # Verificar se o arquivo já foi processado
                if full_file_path in processed_files:
                    log_info(f"File {full_file_path} already processed. Skipping.")
                    continue
                    
                if not os.path.exists(full_file_path):
                    log_warning(f"File not found: {full_file_path}. Skipping to next file.")
                    continue

                # Usar apenas process_file que já contém a lógica necessária
                process_file(repo_path, file_path, item['labels'])
                
                # Adicionar o arquivo à lista de processados
                processed_files.add(full_file_path)
                
        log_info("Label update process completed successfully")
    except Exception as e:
        log_error(f"Error in execute_fix: {e}")
        raise