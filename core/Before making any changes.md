Before making any changes
git branch -> make sure you are on the main branch
if you are not on the main branch use the following command to shift to the main branch

git checkout main -> to go back to the main change
git branch ====> for reconfirming whether you are in the main branch
git pull


# Now you can go ahead and add new changes
git branch -m update-leaderboard
git add .
git commit -m "new updates"
git push --set-upstream origin update-scores
#
Repeat the process everytime you are adding new changes