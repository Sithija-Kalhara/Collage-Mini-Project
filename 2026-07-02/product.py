import pandas as pd
data ={
   "Product_ID":["P101","P102","P103"],
   "Product":["Laptop","Mouse","keybord"],
   "Price":[1200,25,45],
}
df = pd.DataFrame(data)
print(df)