import os
from pathlib import Path

# Define paths and make sure that exists
ROOT_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent
MODELS_PATH = ROOT_PATH.joinpath('models')
OUTPUTS_PATH = ROOT_PATH.joinpath('outputs')
PLOTS_PATH = ROOT_PATH.joinpath('plots')

# Make sure that paths have been created
MODELS_PATH.mkdir(parents=True, exist_ok=True)
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)
PLOTS_PATH.mkdir(parents=True, exist_ok=True)
