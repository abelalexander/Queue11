import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE
import joblib

# Load the first dataset (current 911 call data)
df1 = pd.read_csv('911_call_data.csv')

# Drop unnecessary columns and fill missing values (adapt as needed)
df1 = df1[['PRIORITY', 'CALL_TYPE']]
initial_rows_df1 = df1.shape[0]
df1.dropna(subset=['PRIORITY', 'CALL_TYPE'], inplace=True)
rows_dropped_df1 = initial_rows_df1 - df1.shape[0]
print(f"Rows dropped from df1 due to NaN values: {rows_dropped_df1}")

# Load the second dataset (Baltimore 911 call data)
df2 = pd.read_csv('baltimore_911_calls.csv')

# Drop rows with missing values in priority or description
df2 = df2[['priority', 'description']]
initial_rows_df2 = df2.shape[0]
df2.dropna(subset=['priority', 'description'], inplace=True)
rows_dropped_df2 = initial_rows_df2 - df2.shape[0]
print(f"Rows dropped from df2 due to NaN values: {rows_dropped_df2}")

# Inspect unique values in the priority column to understand possible mapping issues
print("Unique values in the priority column before mapping:", df2['priority'].unique())

# Map Baltimore priority levels to match the existing scale
priority_mapping = {
    'Non-Emergency': 1,  # Non-emergency (low priority)
    'Low': 2,  # Low priority
    'Medium': 3,  # Medium priority
    'High': 5,  # Higher priority
    'Emergency': 6,  # Emergency (high priority)
    'Out of Service': np.nan  # Exclude or handle separately
}
df2['priority'] = df2['priority'].map(priority_mapping)

# Check how many values are being replaced
total_nan_before = df2['priority'].isna().sum()
print(f"Total NaN values before replacement: {total_nan_before}")

# Drop rows with NaN priorities instead of replacing them
# This avoids incorrectly assigning a default priority level to unknown categories
initial_rows_after_mapping = df2.shape[0]
df2.dropna(subset=['priority'], inplace=True)
rows_dropped_after_mapping = initial_rows_after_mapping - df2.shape[0]
print(f"Rows dropped from df2 after mapping due to NaN values: {rows_dropped_after_mapping}")

# Rename columns to match the first dataset
df2.rename(columns={'priority': 'PRIORITY', 'description': 'CALL_TYPE'}, inplace=True)

# Combine both datasets
df_combined = pd.concat([df1, df2], ignore_index=True)

# Drop any remaining NaN values
initial_rows_combined = df_combined.shape[0]
df_combined.dropna(subset=['PRIORITY', 'CALL_TYPE'], inplace=True)
rows_dropped_combined = initial_rows_combined - df_combined.shape[0]
print(f"Rows dropped from combined dataset due to NaN values: {rows_dropped_combined}")


# Save combined call descriptions to a CSV file
df_combined[['CALL_TYPE']].to_csv('combined_call_descriptions.csv', index=False)

# Assign features and target variable
X = df_combined['CALL_TYPE']
y = df_combined['PRIORITY']



# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Vectorize the text data
tfidf = TfidfVectorizer()
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

# Reintroduce SMOTE to balance the data
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train_tfidf, y_train)

# Print the number of new samples generated by SMOTE
from collections import Counter
print(f"Original class distribution: {Counter(y_train)}")
print(f"Resampled class distribution: {Counter(y_train_resampled)}")

# Train the RandomForestClassifier
classifier = RandomForestClassifier(n_estimators=20, random_state=42, class_weight='balanced')
classifier.fit(X_train_resampled, y_train_resampled)

# Predict the priorities for the test set
y_pred = classifier.predict(X_test_tfidf)

# Evaluate the model
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred, zero_division=0))

# Save the trained pipeline to a file
joblib.dump((tfidf, classifier), 'priority_prediction_model.pkl')

# Function to predict priority for a new call description (external usage)
def predict_priority(call_description, model_path='priority_prediction_model.pkl'):
    tfidf, classifier = joblib.load(model_path)
    call_description_tfidf = tfidf.transform([call_description])
    return classifier.predict(call_description_tfidf)[0]

# Example usage
test_scenarios = [
    "Person with severe chest pain",
    "Car accident with injuries",
    "Suspicious person near the store",
    "Fire alarm triggered in a building",
    "Child missing from the park"
]

# Additional test scenarios for each priority level
priority_1_scenarios = [
    "Loud music complaint from a neighborhood",
    "Barking dog reported",
    "Trash left on the street",
    "Report of illegal parking",
    "Request for public information"
]

priority_2_scenarios = [
    "Minor traffic accident without injuries",
    "Lost property report at a store",
    "Suspicious vehicle parked for hours",
    "Minor shoplifting incident",
    "Report of vandalism to property"
]

priority_3_scenarios = [
    "Person with mild breathing difficulty",
    "Report of a possible theft in progress",
    "Child locked in a vehicle",
    "Person with a broken leg from a fall",
    "Fight reported in a public park"
]

priority_5_scenarios = [
    "Armed robbery in progress",
    "Major car accident with injuries",
    "House fire with people inside",
    "Person trapped under heavy equipment",
    "Multiple injuries reported at an industrial site"
]

priority_6_scenarios = [
    "Hostage situation in a residential area",
    "Building collapse with people inside",
    "Explosion at a chemical factory",
    "Active shooter situation",
    "Medical emergency involving multiple people"
]

# Combine all test scenarios
test_scenarios.extend(priority_1_scenarios)
test_scenarios.extend(priority_2_scenarios)
test_scenarios.extend(priority_3_scenarios)
test_scenarios.extend(priority_5_scenarios)
test_scenarios.extend(priority_6_scenarios)

# Loop through each scenario and predict the priority
for scenario in test_scenarios:
    predicted_priority = predict_priority(scenario)
    print(f"Call Description: \"{scenario}\" -> Predicted Priority: {predicted_priority}")