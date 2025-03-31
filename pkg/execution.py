from pkg.run_validation import execute_validation
from pkg.run_fix import execute_fix
from pkg.helper.log import log_info, log_error
# Function to run the validation of labels and deployment files
def run_validation(repo_path, save_path):
    # Logic to execute the validation
    log_info(f"Running check_labels on: {repo_path}")
    try:
        execute_validation(repo_path, save_path)
        log_info(f"Validation completed successfully for {repo_path}")
    except Exception as e:
        log_error(f"Error during validation: {e}")
        raise

# Function to update the files deployment and values
def update_labels_script(repo_path, input_path, skip_duplicate_fix=False):
    """
    Updates labels in deployment and values files.
    
    Args:
        repo_path (str): Repository path.
        input_path (str): Path to the input CSV file.
        skip_duplicate_fix (bool): If True, skips the duplicate fix step (useful when it's already been done).
    """
    log_info(f"Updating labels: {repo_path}")
    try:
        # Use the skip_duplicate_fix parameter to control whether to skip duplicate fixing
        execute_fix(repo_path, input_path, fix_duplicates_only=False, skip_duplicate_fix=skip_duplicate_fix)
        log_info(f"Labels updated successfully for {repo_path}")
    except Exception as e:
        log_error(f"Error updating labels: {e}")
        raise

