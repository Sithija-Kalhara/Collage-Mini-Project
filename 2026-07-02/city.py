import pandas as pd
data ={
    "student_ID":[101,102,103],
    "Name":["john","Emma","David"],
    "Age":[20,21,22],
    "City":["Tokyo","Osaka","Kyoto"]
}
df = pd.DataFrame(data)
print(df)