import pandas as pd
import numpy as np

# ---------------------------------------------------------
# STEP 1: LOAD THE DATA
# ---------------------------------------------------------
# Load the raw CSV file
df = pd.read_csv("Crime_Data_from_2020_raw.csv", low_memory=False)

# Let's see the initial size of the mess we are cleaning
print(f"Initial Row Count: {len(df)}")

#Check Missing values
print(df.isnull().sum())

# check basic info
print(df.info())
print(df.shape)
print(df.dtypes)

#Check statics and outliers
print(df.describe())

print(df.duplicated().sum())

# ---------------------------------------------------------
# STEP 2: REMOVE UNWANTED COLUMNS
# ---------------------------------------------------------
# These columns have too many missing values to be useful for charts
cols_to_drop = ['Crm Cd 2', 'Crm Cd 3', 'Crm Cd 4', 'Cross Street', 'Mocodes']
df = df.drop(columns=cols_to_drop)

# ---------------------------------------------------------
# STEP 3: CLEAN THE PRIMARY KEY (DR_NO)
# ---------------------------------------------------------
# IDs should be 9 digits. We remove the .0 and keep only 9-digit rows.
df['DR_NO'] = df['DR_NO'].astype(str).str.split('.').str[0]
df = df[df['DR_NO'].str.len() == 9].copy()


# ---------------------------------------------------------
# DATE CLEANING (DATA PRESERVATION)
# ---------------------------------------------------------

# 1. We use errors='coerce'. This prevents the AssertionError crash.
# It turns anything it can't read into 'NaT' (Not a Time) instead of crashing.
df['Date Rptd'] = pd.to_datetime(df['Date Rptd'], errors='coerce')
df['DATE OCC'] = pd.to_datetime(df['DATE OCC'], errors='coerce')
 
# many NaT values so  try "Flex Format" to catch the remaining ones.
df['Date Rptd'] = df['Date Rptd'].fillna(pd.to_datetime(df['Date Rptd'], dayfirst=False, errors='coerce'))
df['DATE OCC'] = df['DATE OCC'].fillna(pd.to_datetime(df['DATE OCC'], dayfirst=False, errors='coerce'))

# 3. Clean up the time part so it looks professional (YYYY-MM-DD)
df['Date Rptd'] = df['Date Rptd'].dt.date
df['DATE OCC'] = df['DATE OCC'].dt.date

# 4. FINAL SAFETY: For the tiny few rows that are still missing (if any), 
#  fill them with the most frequent date (Mode) 
df['Date Rptd'] = df['Date Rptd'].fillna(df['Date Rptd'].mode()[0])
df['DATE OCC'] = df['DATE OCC'].fillna(df['DATE OCC'].mode()[0])

print(f"Final Date Check: {df['Date Rptd'].isnull().sum()} missing values.")
print(f"Total Rows Saved: {len(df)}")

# Now check the count of missing values after convert into date from string
print("Missing Dates after Precision Fix:")
print(df[['Date Rptd', 'DATE OCC']].isnull().sum())

# ---------------------------------------------------------
# STEP 5: VICTIM DEMOGRAPHICS (Age, Sex, Descent)
# ---------------------------------------------------------
# Age: Fix negative ages 
df['Vict Age'] = df['Vict Age'].mask(df['Vict Age'] < 0, np.nan)

# Fill those  missing ages with the Median (middle) age
# Using median is safer than mean for age!
df['Vict Age'] = df['Vict Age'].fillna(df['Vict Age'].median())

# Fill the  missing Premis Codes with 0
df['Premis Cd'] = df['Premis Cd'].fillna(0)

# Sex: Map codes to full words
sex_dict = {'M': 'Male', 'F': 'Female', 'X': 'Unknown'}
df['Vict Sex'] = df['Vict Sex'].map(sex_dict).fillna('Unknown')

# Descent: Map ethnicity codes to full names
descent_dict = {
    'H': 'Hispanic', 'W': 'White', 'B': 'Black', 
    'A': 'Asian', 'O': 'Other', 'I': 'Native American'
}
df['Vict Descent'] = df['Vict Descent'].map(descent_dict).fillna('Unknown')

# ---------------------------------------------------------
# STEP 6: FILL REMAINING MISSING VALUES
# ---------------------------------------------------------
# Fill Weapon and Premise gaps so they show up in Power BI slicers
df['Weapon Desc'] = df['Weapon Desc'].fillna('No Weapon Reported')
df['Weapon Used Cd'] = df['Weapon Used Cd'].fillna(0)
df['Premis Desc'] = df['Premis Desc'].fillna('Unknown')
df['Status'] = df['Status'].fillna('UNK')
df['Crm Cd 1'] = df['Crm Cd 1'].fillna(0)

# ---------------------------------------------------------
# STEP 7: GEOGRAPHY AND TEXT POLISHING
# ---------------------------------------------------------
# Fix LAT/LON: Remove zeros and drop missing rows (essential for maps)
df['LAT'] = df['LAT'].replace(0, np.nan)
df['LON'] = df['LON'].replace(0, np.nan)
df = df.dropna(subset=['LAT', 'LON'])

# Make text look professional (Title Case: "hollywood" -> "Hollywood")
pretty_cols = ['AREA NAME', 'Crm Cd Desc', 'Premis Desc', 'Weapon Desc', 'Status Desc', 'LOCATION']
for col in pretty_cols:
    df[col] = df[col].astype(str).str.strip().str.title()


# ---------------------------------------------------------
# STEP : FINAL TYPE CONVERSION (FLOAT TO INT)
# ---------------------------------------------------------
# Converting numerical columns to Integers to remove the ".0"
int_cols = ['Vict Age', 'Premis Cd', 'Weapon Used Cd', 'Crm Cd 1']

for col in int_cols:
    df[col] = df[col].astype(int)

# Force the columns back to true datetime objects
df['Date Rptd'] = pd.to_datetime(df['Date Rptd'])
df['DATE OCC'] = pd.to_datetime(df['DATE OCC'])

# Now check dtypes again
print(df[['Date Rptd', 'DATE OCC']].dtypes)



#Checking age outliers

# Show only the rows where Vict Age is 120
extreme_ages = df[df['Vict Age'] == 120]
print("--- Victims aged 120 ---")
print(extreme_ages[['DR_NO', 'Crm Cd Desc', 'Vict Age', 'Vict Sex']])


#The "Victim Age 0" Problem
age_zero_count = len(df[df['Vict Age'] == 0])
print(f"Victims with age 0: {age_zero_count}")

#Cleaning the outliers by median

# 1. Calculate the median of people whose age we actually know (Age > 0 and < 100)
real_median = df[(df['Vict Age'] > 0) & (df['Vict Age'] < 100)]['Vict Age'].median()

# 2. Replace the 120-year-old and all the 0s with that median
# This "saves" the data while making the charts look realistic
df['Vict Age'] = df['Vict Age'].replace([0, 120], real_median)

# 3. Convert Age to Integer (removes the .0)
df['Vict Age'] = df['Vict Age'].astype(int)

"""check future date outliers"""

# Convert today's date into a pandas timestamp 
future_dates = df[df['DATE OCC'] > pd.Timestamp.now()]
print(f"Crimes reported in the future: {len(future_dates)}")

# ---------------------------------------------------------
#  GEOGRAPHIC CLEANUP (THE GEO-FENCE)
# ---------------------------------------------------------

# 1. Any LAT or LON that is 0 is a placeholder and must be removed
df = df[(df['LAT'] != 0) & (df['LON'] != 0)]

# 2. Filter out any points that are mathematically outside the LA area
# This removes "Ghost Points" that are thousands of miles away
df = df[(df['LAT'] > 33.3) & (df['LAT'] < 34.8)]
df = df[(df['LON'] > -119.3) & (df['LON'] < -117.5)]

print(f"Final Row Count after Geo-Cleaning: {len(df)}")


# ---------------------------------------------------------
#  FINAL CHECK AND SAVE
# ---------------------------------------------------------
print("\n--- FINAL DATA QUALITY REPORT ---")
print(f"Final Row Count: {len(df)}")
print(f"Missing Values: \n{df.isnull().sum()}")
print("\n--- ID LENGTH CHECK ---")
print(df['DR_NO'].str.len().value_counts())
print(df.describe())
print(df.dtypes)
print(df.head())





# Save the perfectly cleaned file
df.to_csv("LA_Crime_Cleaned_Final.csv", index=False)

print("\nSuccess! Your cleaned file is saved .")