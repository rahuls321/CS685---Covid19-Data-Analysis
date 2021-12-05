# CS685-Covid19-Data-Analysis

Packages dependencies
python==3.5.5
numpy==1.16.0
pandas==0.23.0
python-Levenshtein==0.12.2
json
matplotlib==2.2.2

This folder contains following directories and files 
1. data - contains all the data used in this assignment 1
2. notebook - contains all the solutions code in jupyter notebook format
3. python - contains all the solutions code in python format
4. output - output folder

Rest all are the script files which are according to the problems set and assign1.sh is the top-level script that runs the entire assignment.

To run the entire assignment, go to home directory where this README file is there and use --> ./assign1.sh 
To run the assignment question-wise use following

Entire assignment --> ./assign1.sh
Question 1 --> ./neighbor-districts-generator.sh
Question 2 --> ./edge-generator.sh
Question 3 --> ./case-generator.sh
Question 4 --> ./peaks-generator.sh
Question 5 --> ./vaccinated-count-generator.sh
Question 6 --> ./vaccination-population-ratio-generator.sh
Question 7 --> ./vaccine-type-ratio-generator.sh
Question 8 --> ./vaccinated-ratio-generator.sh
Question 9 --> ./complete-vaccination-generator.sh

# ./assign1.sh -- this will generate all the results in the output folder. 
# Some questions uses previous question's results so it is advisable to run the code from beginning or from question 1.
# For better visualizations, comments or code-by-code results, I'll recommend you to run the program using notebooks.
# For running notebooks go to notebook directory, and run --> jupyter notebook 
  to access all the notebooks question-wise
# Question 1 takes around 10 min to execute because I used automated method to find similar method according to cowin data not by manually except for few districts. Other questions code won't take too much time to run.
# Incase you face any issue in running the code, just let me know here
