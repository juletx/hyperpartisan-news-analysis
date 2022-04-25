# Data for PAN at SemEval 2019 Task 4: Hyperpartisan News Detection

Task: https://webis.de/events/semeval-19/

Dataset: https://webis.de/data.html#pan-semeval-hyperpartisan-news-detection-19 | https://doi.org/10.5281/zenodo.5776081

Paper: https://webis.de/publications.html#kiesel_2019c

Training, validation, and test data for the PAN @ SemEval 2019 Task 4: Hyperpartisan News Detection.

The data is split into multiple files. The articles are contained in the files with names starting with "articles-" (which validate against the XML schema article.xsd). The ground-truth information is contained in the files with names starting with "ground-truth-" (which validate against the XML schema ground-truth.xsd).

The first part of the data (filename contains "bypublisher") is labeled by the overall bias of the publisher as provided by BuzzFeed journalists or MediaBiasFactCheck.com. It contains a total of 750,000 articles, half of which (375,000) are hyperpartisan and half of which are not. Half of the articles that are hyperpartisan (187,500) are on the left side of the political spectrum, half are on the right side. This data is split into a training set (80%, 600,000 articles) and a validation set (20%, 150,000 articles), where no publisher that occurs in the training set also occurs in the validation set. Similarly, none of the publishers in those sets occurs in the test set.

The second part of the data (filename contains "byarticle") is labeled through crowdsourcing on an article basis. The data contains only articles for which a consensus among the crowdsourcing workers existed. It contains a total of 645 articles. Of these, 238 (37%) are hyperpartisan and 407 (63%) are not, We will use a similar (but balanced!) test set. Again, none of the publishers in this set occurs in the test set.

Note that article IDs are only unique within the parts.

Moreover, filenames containing "meta" contain data for the respective meta-classification task. See the task's paper for more information.

The collection (including labels) are licensed under a Creative Commons Attribution 4.0 International License.

Acknowledgements: Thanks to Jonathan Miller for his assistance in cleaning the data!
