import tkinter as tk
from tkinter import filedialog, messagebox
import os
from pkg.execution import run_validation, update_labels_script
from pkg.helper.config import load_config
from pkg.helper.log import setup_logger, log_info, log_error, log_debug


# Create the main application window
def create_gui():
    
    root = tk.Tk()
    root.title("Ownership Update Script")
    root.geometry("600x350")  # Increased height to accommodate the new button

    # Load settings
    try:
        config = load_config()
        log_info("Settings loaded")
    except Exception as e:
        log_error(f"Error loading settings: {e}")

    log_info("Starting GUI application")
    # Main Frame
    main_frame = tk.Frame(root, padx=5, pady=5)
    main_frame.pack(fill=tk.BOTH, expand=False, pady=5)

    # Repository Frame
    repo_frame = tk.LabelFrame(main_frame, text="Repository", padx=5, pady=5, bd=2, relief=tk.GROOVE)
    repo_frame.pack(fill="x", expand=False, pady=5)

    # Repository Frame: The repository path
    tk.Label(repo_frame, text="Path:", font=('Helvetica', 10)).grid(row=1, column=0, sticky='e', pady=3)
    global repo_path_entry
    repo_path_entry = tk.Entry(repo_frame, width=20)
    repo_path_entry.insert(0, config.get('repo_path', '/home/thais/PycharmProjects/bees-microservices'))  # Use value from config
    repo_path_entry.grid(row=1, column=1, padx=2, pady=2, sticky='ew')
    repo_frame.grid_columnconfigure(1, weight=1)

    # Function to browse for the repository path
    def browse_repo_path():
         path = filedialog.askdirectory()
         repo_path_entry.delete(0, tk.END)
         repo_path_entry.insert(0, path)
         log_info(f"Repository path set to: {path}")
    tk.Button(repo_frame, text="Browse", command=browse_repo_path, bg="#D3D3D3").grid(row=1, column=2, padx=2, pady=2, sticky='w')

    # Action Frame
    action_frame = tk.LabelFrame(main_frame, text="Action", padx=5, pady=5, bd=2, relief=tk.GROOVE)
    action_frame.pack(fill="x", expand=False, pady=5)

    # Extract Data Frame
    extract_frame = tk.LabelFrame(action_frame, text="Extract Data", padx=5, pady=5, bd=2, relief=tk.GROOVE)
    extract_frame.grid(row=1, column=0, columnspan=1, padx=3, pady=3, sticky='ew')
    
    # Set the path for the 'docs' directory from config
    docs_path = config.get('extract_path', os.path.join(os.getcwd(), 'docs'))
    if not os.path.exists(docs_path):
        os.makedirs(docs_path)
        log_info(f"Created docs directory: {docs_path}")

    # Update the input field to show the path from config
    global extract_path_entry
    extract_path_entry = tk.Entry(extract_frame, width=35)
    extract_path_entry.insert(0, docs_path)  # Show the path from config
    extract_path_entry.grid(row=0, column=1, padx=2, pady=2, sticky='ew')
    
    # Browse Button
    def browse_extract_path():
        path = filedialog.askdirectory()
        extract_path_entry.delete(0, tk.END)
        extract_path_entry.insert(0, path)
    
    # Browse Button
    tk.Button(extract_frame, text="Browse", command=browse_extract_path, bg="#D3D3D3").grid(row=0, column=2, padx=1, pady=1)
    # Run Button
    tk.Button(extract_frame, text="Run", command=extract_information, bg="#D3D3D3").grid(row=0, column=3, padx=1, pady=1)

    # Update Frame
    update_frame = tk.LabelFrame(action_frame, text="Update", padx=5, pady=5, bd=2, relief=tk.GROOVE)
    update_frame.grid(row=2, column=0, columnspan=1, padx=3, pady=3, sticky='ew')
    
    # Input File Path
    global update_path_entry
    tk.Label(update_frame, text="File Path:", font=('Helvetica', 10)).grid(row=0, column=0, sticky='e', pady=3)
    update_path_entry = tk.Entry(update_frame, width=40)
    update_path_entry.insert(0, config.get('update_path', '/home/thais/PycharmProjects/checkBS_v_1_1/docs/fix_it.csv'))  # Use value from config
    update_path_entry.grid(row=0, column=1, padx=3, pady=3, sticky='ew')

    # Browse Button
    def browse_update_path():
        # I would need a function to verify if the selected file is a CSV
        # and not allow the user to select another type of file
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path.endswith('.csv'):
            error_msg = "Please select a CSV file"
            log_error(error_msg)
            messagebox.showerror("Error", error_msg)
            return
        update_path_entry.delete(0, tk.END)
        update_path_entry.insert(0, path)
        log_info(f"Input file path set to: {path}")

    tk.Button(update_frame, text="Browse", command=browse_update_path, bg="#D3D3D3").grid(row=0, column=2, padx=3, pady=3)

    # Add 'Fix' button to the GUI
    tk.Button(update_frame, text="Fix", command=lambda: update_deployment_script(), bg="#D3D3D3").grid(row=0, column=3, padx=3, pady=3)
    
    # Configure columns to expand
    extract_frame.grid_columnconfigure(1, weight=1)
    update_frame.grid_columnconfigure(1, weight=1)
    
    # Add frame for saving settings
    config_frame = tk.LabelFrame(main_frame, text="Settings", padx=5, pady=5, bd=2, relief=tk.GROOVE)
    config_frame.pack(fill="x", expand=False, pady=5)
    
    log_info("GUI initialized successfully")
    root.mainloop()

# Function to extract information about the issues found in the repository
def extract_information():
    save_path = extract_path_entry.get()    
    repo_path = repo_path_entry.get()
    log_info(f"Save Path: {save_path}")  # Log of the save path
    log_info(f"Repo Path: {repo_path}")  # Log of the repository path
   
    if not save_path or not repo_path or not update_deployment_script:
        error_msg = "The path of the save and repo are required"
        log_error(error_msg)
        messagebox.showerror("Error", error_msg)
        return
    # Logic to generate the information about the issues found in the repository
    try:
        # Call the label_checker function with the save path
        log_info("Running validation...")  # Log before executing validation
        run_validation(repo_path, save_path)
        success_msg = "File generated successfully!"
        log_info(success_msg)
        messagebox.showinfo("Success", success_msg)
    except Exception as e:
        log_error(f"Exception occurred: {e}")  # Log of the exception
        messagebox.showerror("Error", f"Failed to generate file: {e}")

# Define the function to update ownerships
def update_deployment_script():
    repo_path = repo_path_entry.get()
    input_path = update_path_entry.get()
    log_info(f"Input Path: {input_path}")
    if not input_path or not repo_path:
        error_msg = "Input file path and the repo path are required"
        log_error(error_msg)
        messagebox.showerror("Error", error_msg)
        return
    try:
        # Then update the labels (skipping duplicate fix since it's already done)
        log_info("Running update...")
        update_labels_script(repo_path, input_path, skip_duplicate_fix=True)
        
        success_msg = "Files updated successfully!"
        log_info(success_msg)
        messagebox.showinfo("Success", success_msg)
    except Exception as e:
        log_error(f"Exception occurred: {e}")  # Log of the exception
        messagebox.showerror("Error", f"Failed to update file: {e}")

if __name__ == "__main__":
    create_gui() 