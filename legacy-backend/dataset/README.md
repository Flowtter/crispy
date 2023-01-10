# How to create a dataset
## Add the videos
The videos should be saved in `backend/resources/video`.

## Generate the frames
Run the following command:
```
python backend/src/create_dataset.py --extract
```

## Add a values.json
A file named `values.json` should be created in the `backend/dataset` folder.\
This file will be used to create the dataset.\
A template is available.\
The range corresponds to the frame where a kill should be detected.

## Generate the dataset
Run the following command:
```
python backend/src/create_dataset.py --to-csv
```

# Usage
The dataset will be saved as a csv file in the `backend/dataset` folder.\
Its name is `result.csv`.

# Understanding the dataset
- The dataset is a csv file.
- each line is a frame.
- the first column is a boolean indicating if a kill should be detected.
- the other columns are the values of the frame in gray scale.
