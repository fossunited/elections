"""
* https://yingtongli.me/blog/2020/12/24/pyrcv2.html
* https://yingtongli.me/rcv/
* https://yingtongli.me/git/pyRCV2/about/docs/blt.md
* https://opavote.com/
* https://opavote.com/methods/recommended
"""

from collections import Counter
import pathlib

import pandas as pd

candidates_filename = "Election Candidate.csv"
votes_filename = "Candidate Vote.csv"
results_filename = "results.blt"
vote_counter = Counter()

candidates_df = pd.read_csv(pathlib.Path(".") / candidates_filename)

# Please note that before the file can be loaded, it needs to be manually
# edited. This is because the first votes cast in this election required
# people to select 15 options, which was later modified to 5. The original
# votes therefore need to be edited to remove the 10 additional options
# selected by the people.
votes_df = pd.read_csv(pathlib.Path(".") / votes_filename)

# Add a new column to the candidates dataframe which contains a numerical ID
# for each candidate. This numerical ID will be used in the BLT file.
# Ref https://yingtongli.me/git/pyRCV2/about/docs/blt.md for additional info
# regarding the file format
candidates_df["numericalID"] = range(1, len(candidates_df) + 1)

# The ID column contains NA values. This is because the first row of a vote
# contains the vote ID but the 4 subsequent rows contain empty string as vote
# ID. With `ffill`, we forward fill the NA values until we hit the next
# non-NA value
votes_df.ffill(inplace=True)

# Voting preferences in the votes dataframe ("Candidate (Candidate Tiers)" column)
# contains a unique hash values. These unique hash values map to the "ID" value
# in the candidates_df dataframe.
# We simply replace the hash values with a numerical ID of the candidate
for candidate in candidates_df.iterrows():
    votes_df.replace(candidate[1]["ID"], candidate[1]["numericalID"], inplace=True)

# Get the unique hashes/values of votes
votes = votes_df["ID"].unique()

for vote in votes:
    # Get the choices submitted in this vote
    ballot = votes_df[votes_df["ID"] == vote]

    # The rows are already sorted by rank but we want to assert this.
    # Incorrect order will lead to the votes being counted incorrectly
    assert (ballot["Rank (Candidate Tiers)"].values == [1, 2, 3, 4, 5]).all()

    # "Candidate (Candidate Tiers)" uses numpy int64 dtype and mapping the int
    # function to these values means we create a collection of ints
    # And we store this tuple/container in the Counter object
    vote_counter[tuple(map(int, ballot["Candidate (Candidate Tiers)"].values))] += 1

with open(pathlib.Path(".") / results_filename, "w") as results_file:
    # The first line of the results file should contain
    # the number of candidates
    # followed by a space
    # followed by the number of seats
    results_file.write("15 5\n")
    # The subsequent lines contain the number of ballots
    # and the preference in those ballots
    # followed by "0"
    for p, count in vote_counter.items():
        # p stands for preference
        results_file.write(f"{count} {p[0]} {p[1]} {p[2]} {p[3]} {p[4]} 0\n")
    # The line after vote information should contain a "0"
    results_file.write("0\n")
    # The subsequent lines should contain the names of the candidates
    for candidate in candidates_df.iterrows():
        name_col = "Full Name"
        results_file.write(f"\"{candidate[1][name_col]}\"\n")
    # The last line of the file should be the title of the election
    results_file.write("\"FOSS United elections 2025\"")
    # No empty line at the end of the file
