1. Macro F1 score

I think using macro F1 to evaluate the model’s final predictions across the seven skin-lesion categories would be a good fit for this project. F1 combines precision (how often a prediction for a diagnosis is correct) and recall (how many actual examples of that diagnosis the model finds). We would calculate F1 for each category and average the seven scores equally. I suggest macro F1 because we want the model to recognize a range of lesions, even if there are some categories with less training images than others. Eg, Melanoma. We want it to identify actual melanoma images while avoiding incorrectly labeling other lesions as melanoma. Macro F1 captures both kinds of mistakes and gives every category equal weight.

[scikit-learn F1 documentation](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html)

 2. Macro average precision (AP)

I also propose macro AP to evaluate the scores of the model predictions. This summarizes the balance between precision and recall even as the score threshold changes for identifying diagnosis. We would calculate AP separately for each category versus the other six (so equal weight), then average the seven results equally. From what I understand, this helps us see whether actual examples of a diagnosis are prone to get higher scores than images from other categories. For example, it can show whether the model ranks melanoma images very high without also assigning high melanoma scores to other lesions that aren't melanomas.

[scikit-learn average precision documentation](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)

