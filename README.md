# Kubernetes Ownership Labels Management

This project provides tools to check and fix ownership labels in Kubernetes deployment and values YAML files within a given directory structure. It helps ensure consistent labeling across your Kubernetes resources.

## Features

- **Check Labels**: Scans deployment and values files for required ownership labels and generates a CSV report of any inconsistencies.
- **Fix Labels**: Automatically adds or updates ownership labels in deployment and values files based on a CSV input.
- **GUI Interface**: Provides a graphical user interface for easy interaction with the tools.
- **Configuration File**: Supports a `config.yaml` file to store and load paths automatically.

## Prerequisites

- Python 3.x
- Required Python packages:
  - `pyyaml`
  - `tkinter` (for GUI)

## Setup

1. Clone the repository or download the scripts to your local machine.
2. Ensure you have Python 3.x installed.
3. Install the required Python packages using pip:
   ```bash
   pip install pyyaml
   ```

## Configuration

The application uses a `config.yaml` file to store paths. If this file doesn't exist, it will be created with default values when the application starts.

Example `config.yaml`:
```yaml
# Arquivo de configuração para o Ownership Labels Management
# Este arquivo armazena os caminhos utilizados pela aplicação

# Caminho do repositório a ser analisado
repo_path: /home/ana/ABInbev/workArea/bees-microservices

# Caminho do arquivo CSV para atualização
update_path: /home/ana/ABInbev/developArea/checkBS/docs/fix_it.csv

# Caminho para salvar os resultados da extração
extract_path: /home/ana/ABInbev/developArea/checkBS/docs
```

You can edit this file manually or use the "Save Configuration" button in the GUI to update it with the current values.

## How to Run

### GUI Mode

1. Navigate to the project directory.
2. Run the main script:
   ```bash
   python main.py
   ```
3. Use the GUI to:
   - Set the repository path
   - Extract data (check labels)
   - Fix labels using a CSV file
   - Save your configuration for future use

### Command Line Mode

#### Check Labels

```bash
python -c "from pkg.execution import run_validation; run_validation('/path/to/repo', '/path/to/save')"
```

#### Fix Labels

```bash
python -c "from pkg.execution import update_labels_script; update_labels_script('/path/to/repo', '/path/to/input.csv')"
```

## Project Structure

- `main.py`: Entry point for the GUI application
- `config.yaml`: Configuration file for paths
- `pkg/`: Package containing the core functionality
  - `__init__.py`: Package initialization
  - `execution.py`: Main execution functions
  - `gui.py`: GUI implementation
  - `run_validation.py`: Functions for validating labels
  - `run_fix.py`: Functions for fixing labels
  - `config.py`: Functions for managing configuration

## Input/Output Files

### Check Labels Output

The script generates a `result.csv` file containing:
- Source file path
- Missing or incorrect label structures

### Fix Labels Input

The input CSV file should contain the following columns:
- `path`: Semicolon-separated list of file paths to fix
- `businessStructure`: Business structure label value
- `director`: Director label value
- `valueStream`: Value stream label value
- `teamName`: Team name label value

## Troubleshooting

- Ensure the directory paths in the script are correct and accessible.
- Check for any syntax errors in the YAML files if the script reports issues.
- For file not found errors, verify the paths in the CSV file.
- If Helm template verification fails, check the Helm chart structure.
- If the configuration file is corrupted, delete it and restart the application to create a new one.

## License

This project is licensed under the MIT License. 