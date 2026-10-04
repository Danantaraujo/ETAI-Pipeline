
# Daniel Araújo 20260669

# Week 2 progress

The logistic regresion model is the better model, as it achieves a higher test accuracy (67.9%) compared to the decision tree (62.9%).It also shows no overfitting, with a 0.0% train-test gap, while the decision tree has a 20.0% gap. Additionally, its F1-score (0.67) is higher than the decision tree’s (0.62), indicating better overall performance and generalization.


# Week 3 progress

Before evaluating the performance of the models once again, changes were made to the "raw" dataset with the purpose of completing the data cleaning step. Taking in consideration that such changes were made it is natural that the results of each model change. Comparisons between models of the "raw" and "cleaned" datasets were not made.

### Model Performance on the Cleaned Dataset

| Model | Train Accuracy | Test Accuracy | Macro F1 | Train-Test Gap |
|---|---:|---:|---:|---:|
| Logistic Regression | 67.8% | 65.5% | 0.64 | 2.3% |
| Decision Tree | 79.9% | 60.6% | 0.59 | 19.3% |~

On the cleaned database, logistic regression performs better than the decision tree, with a test accuracy of 65.5% vs. 60.6%, an F1-score of 0.64 vs. 0.59, and a much smaller train-test gap (2.3% vs. 19.3%). In the previous results, logistic regression also performed better (67.9% vs. 62.9% accuracy) and had a smaller gap (0.0% vs. 20.0%). However, the results before and after cleaning should not be directly compared, since the models were trained and tested on different versions of the dataset. Therefore, the most meaningful comparison is between the two models within the same dataset.


# Week 4 progress

Updates
- Improved data cleaning with invalid values, placeholders, duplicates and missing-value handling.
- Preprocessing is now included inside the model pipeline.
- Replaced the single train/test split with 5-fold stratified cross-validation.
- Comparing Models.

Model Comparison
The models were compared using the same 5-fold stratified cross-validation setup, with the same preprocessing pipeline and random state.


| Model | Train Accuracy | Test Accuracy | Macro F1 | Train-Test Gap |
|---|---:|---:|---:|---:|
| Logistic Regression | 67.5% | 67.2% | 0.66 | 0.3% |
| Decision Tree | 69.5% | 61.0% | 0.60 | 8.5% |
| Random Forest | 73.3% | 65.0% | 0.64 | 8.3% |


For now, I am comparing the models mainly using the mean validation accuracy, its standard deviation, and the train–validation gap. I am not completely sure whether this is the best model comparison approach for this project, so this should be confirmed with the professor.
Logistic Regression currently shows the best overall cross-validation performance. Random Forest still requires hyperparameter tuning, so its current results should be considered preliminary.