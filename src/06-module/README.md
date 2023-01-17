

## Directory Structure


├── LICENSE
├── README.md          <- README explains this Python module to both developers and users.
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│   └── my_module      <- A symbolic link to the 'my_module' directory
│                         On Linux/Mac: cd notebooks ; ln -s ../my_module .
│
├── requirements.txt   <- The requirements file for creating the Python environment. Install in a venv/conda environment.
│                         `conda activate my_env`
│                         my_env> `pip install -r requirements.txt`
│
├── setup.py           <- Make this project pip installable with `pip install -e`
├── my_module          <- Source code for this project.
│   ├── __init__.py    <- Makes a Python module
│   │
│   ├── pipelines      <- Feature pipelines, training pipelines, batch inference pipelines.
│   │   │── feature_pipeline.py
│   │   │── training_pipeline.py
│   │   └── batch_inference_pipeline.py
│   │
│   ├── features       <- Python modules to turn raw data into features for use in both training and inference
│   │   └── my_features.py
│   │
│   ├── transformations<- Python modules with model-specific transformation functions
│   │   └── my_transformations.py
│   │
│   ├── tests          <- Pytest unit tests for feature logic
│   │   └── test_features.py
│   │
│   ├── pipeline_tests <- Pytest to run end-to-end tests for pipelines
│   │   └── test_feature_pipelines.py
│   │
│   └── visualization  <- Scripts to create exploratory and results oriented visualizations
│       └── eda_visualize.py
│
└── scripts            <- Bash scripts for the project
