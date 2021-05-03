import pandas as pd
import matplotlib.pyplot as plt
# VISUALIZE IT
##########################
# all data is attached to the state....so for instance, we can record the average ethnic breakdown or something.
# essentially visualize the updator returned lists.
# N_points = 100000
# n_bins =
#
# # Generate a normal distribution, center at x=0 and y=5
# x = np.random.randn(N_points)
# y = .4 * x + np.random.randn(100000) + 5
#
# fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)

# We can set the number of bins with the `bins` kwarg
# axs[0].hist(x, bins=n_bins)

plurality_data = pd.read_csv("outputs/pluralities_by_race.csv")

ax = plurality_data.plot(kind='bar', stacked=True, figsize=(10, 6))
ax.set_ylabel('Districts (51 total)')
ax.set_xlabel('Distribution Space')
plt.legend(title='Pluralities', bbox_to_anchor=(1.0, 1), loc='upper left')
# plt.savefig('stacked.png')  # if needed
plt.show()

threshold_data = pd.read_csv("outputs/threshold_by_race.csv.csv")
ax.set_ylabel('Districts (51 total)')
ax.set_xlabel('Distribution Space')

# hist = threshold_data.hist(bins=250)
# threshold_data.hist(by=np.random.randint(0, 4, 1000), figsize=(6, 4));
threshold_data["white"].hist()
# threshold_data[]
# threshold_data[]
# threshold_data[]
# threshold_data[]
# threshold_data[]
# plurality_data.hist
## Histograms

# For # districts  < > (x)median
# MSE of median incomes to total median income?

# For Population, per race, % of districts where race > x%
# Per race, std across each states (across distrsicts)

## STacked Bar Charts
# Stacked bar chart of # of districts where each race has plurality, per state....

#     print(count)
#     # pops.append(each["population"])
#     # if count % 100 == 0:
#         # with open("log.txt", "w") as f:
#             # f.write(pops)
#             # in this example, not reseting data bc only 1000.
#
# # can write data to file every so often if needed.
#
# # Visualization
#
# # all data is attached to the state....so for instance, we can record the average ethnic breakdown or something.
# # seems can do this with updater functions as well as the markove iterator?
#
