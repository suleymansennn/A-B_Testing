import pandas as pd
import matplotlib
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from scipy.stats import shapiro, levene, ttest_ind

matplotlib.use("Qt5Agg")

pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", lambda x: "%.5f" % x)

colors = ['#FFB6B9', '#FAE3D9', '#BBDED6', '#61C0BF', "#CCA8E9", "#F67280"]

df_control = pd.read_excel("ab_testing.xlsx", sheet_name="Control Group")
df_test = pd.read_excel("ab_testing.xlsx", sheet_name="Test Group")

df_control.head()
"""
    Impression      Click  Purchase    Earning
0  82529.45927 6090.07732 665.21125 2311.27714
1  98050.45193 3382.86179 315.08489 1742.80686
2  82696.02355 4167.96575 458.08374 1797.82745
3 109914.40040 4910.88224 487.09077 1696.22918
4 108457.76263 5987.65581 441.03405 1543.72018
"""
df_test.head()
"""
    Impression      Click  Purchase    Earning
0 120103.50380 3216.54796 702.16035 1939.61124
1 134775.94336 3635.08242 834.05429 2929.40582
2 107806.62079 3057.14356 422.93426 2526.24488
3 116445.27553 4650.47391 429.03353 2281.42857
4 145082.51684 5201.38772 749.86044 2781.69752
"""


def num_summary(dataframe, col_name, target):
    quantiles = [.01, .05, .1, .5, .9, .95, .99]
    print("#" * 70)
    print(dataframe[col_name].describe(percentiles=quantiles))
    print("#" * 70)

    plt.figure(figsize=(15, 10))
    plt.suptitle(col_name.capitalize(), size=16)
    plt.subplot(1, 3, 1)
    plt.title("Histogram")
    sns.histplot(dataframe[col_name], color="#FFB6B9")

    plt.subplot(1, 3, 2)
    plt.title("Box Plot")
    sns.boxplot(data=dataframe, y=col_name, color="#F67280")

    plt.subplot(1, 3, 3)
    sns.scatterplot(data=dataframe, x=col_name, y=target, palette=colors, estimator=np.mean)
    plt.title(f"Average of {col_name.capitalize()} by {target.capitalize()}")
    plt.tight_layout(pad=1.5)
    plt.show(block=True)


for col in df_control.columns:
    num_summary(df_control, col, "Purchase")

for col in df_control.columns:
    num_summary(df_test, col, "Purchase")

df = pd.concat([df_control, df_test], ignore_index=True)
df.loc[0:39, "Control-Test"] = "Control"
df.loc[40:80, "Control-Test"] = "Test"
df.to_csv("df", index=False)
df.sample(5)
"""
     Impression      Click  Purchase    Earning Control-Test
10  83676.93601 4273.40021 386.09788 2174.09357      Control
53 117281.76759 2617.80386 372.12579 1947.74713         Test
65 113732.66846 3251.84904 610.74232 2366.82241         Test
1   98050.45193 3382.86179 315.08489 1742.80686      Control
6   95110.58627 3555.58067 512.92875 1815.00661      Control
"""

"""
H0: M1 = M2 
--> There is no statistical difference between the average purchase earned,
    by the control and test groups.
H1: M1 != M2 
--> There is a statistical difference between the average purchase earned, 
    by the control and test groups.

"""

df.groupby("Control-Test").agg({"Purchase": "mean"})

"""
              Purchase
Control-Test          
Control      550.89406
Test         582.10610

When we analyze the mean of the two groups mathematically, there seems to be a difference. We can say that the test 
group is better. But to prove this statistically, we need to run a hypothesis test.
"""
# Ho: There is no statistically significant difference between the means of the two groups distribution
# Ha: There is statistically significant difference between the means of the two groups

# 1. Normality Assumption
test_stat, pvalue = shapiro(df.loc[df["Control-Test"] == "Control", "Purchase"])
print("Test Stat = %.4f, pvalue = %.4f" % (test_stat, pvalue)) # Test Stat = 0.9773, pvalue = 0.5891

test_stat, pvalue = shapiro(df.loc[df["Control-Test"] == "Test", "Purchase"])
print("Test Stat = %.4f, pvalue = %.4f" % (test_stat, pvalue)) # Test Stat = 0.9589, pvalue = 0.1541

"""
Determining the distribution of the variable Purchase was important for choosing an appropriate statistical method. 
So a Shapiro-Wilk test was performed and did not show evidence of non-normality. Based on this outcome(p-value > 0.05),
and after visual examination of the histogram of Purchase, I decided to use a parametric (ttest_ind) test.)
"""
# 2. Variance Assumption
# Ho: The compared groups have equal variance.
# Ha: The compared groups do not have equal variance.
test_stat, pvalue = levene(df.loc[df["Control-Test"] == "Control", "Purchase"],
                           df.loc[df["Control-Test"] == "Test", "Purchase"])
print("Test Stat = %.4f, pvalue = %.4f" % (test_stat, pvalue)) # Test Stat = 2.6393, pvalue = 0.1083
"""
The p-value of the Levene’s test is not significant, suggesting that there is not a significant difference between the
variances of the two groups. Therefore, we’ll use a standard independent 2 sample test that assumes equal population
variances.
"""

test_stat, pvalue = ttest_ind(df.loc[df["Control-Test"] == "Control", "Purchase"],
                              df.loc[df["Control-Test"] == "Test", "Purchase"], equal_var=True)

print("Test Stat = %.4f, pvalue = %.4f" % (test_stat, pvalue)) # Test Stat = -0.9416, pvalue = 0.3493
"""
p-value => 0.3493 Since the p-value is not less than 0.05 , the Ho hypothesis cannot be rejected. So, there is no 
statistically significant difference between the mean of the Control group and Test group
"""


