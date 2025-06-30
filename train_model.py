import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

def load_and_prepare_data():
    df = pd.read_csv("processed_task_features.csv")

    # Target column
    y = df['completed']

    # Feature columns exclude the target
    X = df.drop(columns=['completed'])

    # Fix sklearn issue with mixed column types by ensuring all column names are strings
    X.columns = X.columns.astype(str)

    return X, y

def train_and_evaluate():
    X, y = load_and_prepare_data()

    # Split data 80% train / 20% test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"Model accuracy: {accuracy:.4f}")

    # Save the trained model
    joblib.dump(clf, "rf_model.joblib")
    print("Saved trained model to 'rf_model.joblib'")

    return clf

if __name__ == "__main__":
    print("Training model...")
    train_and_evaluate()
