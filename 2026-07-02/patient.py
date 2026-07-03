import pandas as pd

import pandas as pd

pd.set_option("display.width", 160)
pd.set_option("display.max_columns", None)

data = {
    "Patient_ID": [301, 302, 303, 304, 305, 306],
    "Name": ["Ava", "Leo", "Mia", "Ethan", "Ella", "Noah"],
    "Age": [45, 70, 30, 65, 27, 72],
    "Disease": ["Diabetes", "Hypertension", "Asthma", "Heart Disease", "Fever", "Diabetes"],
    "Doctor": ["Dr. Kim", "Dr. Singh", "Dr. Chen", "Dr. Patel", "Dr. Kim", "Dr. Chen"]
}

df = pd.DataFrame(data)

df["Age_Group"] = df["Age"].apply(lambda x: "Senior" if x >= 60 else "Adult")

print("Full Patient DataFrame:")
print(df)

print("\nSenior Patients:")
print(df[df["Age_Group"] == "Senior"])

print("\nDisease Count:")
print(df["Disease"].value_counts())

print("\nAverage Age:")
print(df["Age"].mean())

print("\nOldest Patient:")
print(df.loc[df["Age"].idxmax()])import pandas as pd

import pandas as pd

pd.set_option("display.width", 160)
pd.set_option("display.max_columns", None)

data = {
    "Patient_ID": [301, 302, 303, 304, 305, 306],
    "Name": ["Ava", "Leo", "Mia", "Ethan", "Ella", "Noah"],
    "Age": [45, 70, 30, 65, 27, 72],
    "Disease": ["Diabetes", "Hypertension", "Asthma", "Heart Disease", "Fever", "Diabetes"],
    "Doctor": ["Dr. Kim", "Dr. Singh", "Dr. Chen", "Dr. Patel", "Dr. Kim", "Dr. Chen"]
}

df = pd.DataFrame(data)

df["Age_Group"] = df["Age"].apply(lambda x: "Senior" if x >= 60 else "Adult")

print("Full Patient DataFrame:")
print(df)

print("\nSenior Patients:")
print(df[df["Age_Group"] == "Senior"])

print("\nDisease Count:")
print(df["Disease"].value_counts())

print("\nAverage Age:")
print(df["Age"].mean())

print("\nOldest Patient:")
print(df.loc[df["Age"].idxmax()])