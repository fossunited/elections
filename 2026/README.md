Please use [starpy](https://github.com/Equal-Vote/starpy/) Python package to tabulate the
results locally. The steps to tabulate results are shown below.

```python
import pandas as pd
from starpy.STAR import STAR

filename = "ballot-data.csv"
# 3 members are being elected to the Governing Board in 2026
numwinners = 3

df = pd.read_csv(filename, header=0)

# Ballot contains empty data if the voter didn't specifically select 0-5 stars for a candidate
df.fillna(0, inplace=True)
# Column 0 contains a unique Ballot ID and Column 1 is an empty "precinct" column
df.drop(labels= ["ballot_id", "precinct"], axis=1, inplace=True)

print(STAR(df, numwinners=numwinners)["elected"])
```
