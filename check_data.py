import pandas as pd

features = pd.read_csv("data/ml_feature_dataset.csv")
print("FEATURES:", features.shape)
print(features.columns.tolist())
print(features.head(3))

labels = pd.read_csv("data/labeling_candidates.csv")
print("\nLABELS:", labels.shape)
print(labels.columns.tolist())
print(labels.head(3))