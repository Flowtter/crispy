# How to create a dataset

## Add the videos

The videos should be saved in `crispy-api/resources/video`.

## Generate the dataset

Run the following command:

```
python -m api --dataset --game="valorant"
```

game can be any game supported by the api.

## Add a values.json

A file named `dataset_values.json` should be created in the `crispy-api/` folder.\
This file will be used to create the dataset.\
A template is available.\
The range corresponds to the frame where a kill should be detected.

# Usage

The dataset will be saved as a csv file in the `crispy-api/dataset` folder.\
Its name is `result.csv`.

# Understanding the dataset

- The dataset is a csv file.
- each line is a frame.
- the first column is a boolean indicating if a kill should be detected.
- the other columns are the values of the frame in gray scale.
