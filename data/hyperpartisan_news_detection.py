# coding=utf-8
# Copyright 2020 The TensorFlow Datasets Authors and the HuggingFace Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
"""Hyperpartisan News Detection"""


import os
import textwrap
import string
from lxml import etree
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

import datasets


_CITATION = """\
@article{kiesel2019data,
  title={Data for pan at semeval 2019 task 4: Hyperpartisan news detection},
  author={Kiesel, Johannes and Mestre, Maria and Shukla, Rishabh and Vincent, Emmanuel and Corney, David and Adineh, Payam and Stein, Benno and Potthast, Martin},
  year={2019}
}
"""

_DESCRIPTION = """\
Hyperpartisan News Detection was a dataset created for PAN @ SemEval 2019 Task 4.
Given a news article text, decide whether it follows a hyperpartisan argumentation, i.e., whether it exhibits blind, prejudiced, or unreasoning allegiance to one party, faction, cause, or person.

There are 2 parts:
- byarticle: Labeled through crowdsourcing on an article basis. The data contains only articles for which a consensus among the crowdsourcing workers existed.
- bypublisher: Labeled by the overall bias of the publisher as provided by BuzzFeed journalists or MediaBiasFactCheck.com.
"""
_URL_BASE = "https://zenodo.org/record/5776081/files/"

PUNCTUATION = string.punctuation + "‘’“”«»–…•"
STOPWORDS = set(stopwords.words('english'))
ENTITIES = set(["lt", "amp", "gt", "quot", "apos"])
IMAGE = set(["img", "alt", "src", "width", "height", "https", "datarecalcdims", "aligncenter"])
class HyperpartisanNewsDetection(datasets.GeneratorBasedBuilder):
    """Hyperpartisan News Detection Dataset."""

    VERSION = datasets.Version("1.0.0")
    BUILDER_CONFIGS = [
        datasets.BuilderConfig(
            name="byarticle",
            version=datasets.Version("1.0.0", "Version Training and validation v1"),
            description=textwrap.dedent(
                """
                    This part of the data (filename contains "byarticle") is labeled through crowdsourcing on an article basis.
                    The data contains only articles for which a consensus among the crowdsourcing workers existed. It contains
                    a total of 645 articles. Of these, 238 (37%) are hyperpartisan and 407 (63%) are not, We will use a similar
                    (but balanced!) test set. Again, none of the publishers in this set will occur in the test set.
                """
            ),
        ),
        datasets.BuilderConfig(
            name="bypublisher",
            version=datasets.Version("1.0.0", "Version Training and validation v1"),
            description=textwrap.dedent(
                """
                    This part of the data (filename contains "bypublisher") is labeled by the overall bias of the publisher as provided
                    by BuzzFeed journalists or MediaBiasFactCheck.com. It contains a total of 750,000 articles, half of which (375,000)
                    are hyperpartisan and half of which are not. Half of the articles that are hyperpartisan (187,500) are on the left side
                    of the political spectrum, half are on the right side. This data is split into a training set (80%, 600,000 articles) and
                    a validation set (20%, 150,000 articles), where no publisher that occurs in the training set also occurs in the validation
                    set. Similarly, none of the publishers in those sets will occur in the test set.
                """
            ),
        ),
    ]

    def _info(self):
        features = {
            "id": datasets.Value("string"),
            "text": datasets.Value("string"),
            "clean_text": datasets.Value("string"),
            "title": datasets.Value("string"),
            "hyperpartisan": datasets.Value("bool"),
            "url": datasets.Value("string"),
            "published_at": datasets.Value("string"),
        }

        if self.config.name == "bypublisher":
            # Bias is only included in the bypublisher config
            features["bias"] = datasets.ClassLabel(names=["right", "right-center", "least", "left-center", "left"])

        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(features),
            supervised_keys=("text", "label"),
            homepage="https://pan.webis.de/semeval19/semeval19-web/",
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        urls = {
            datasets.Split.TRAIN: {
                "articles_file": _URL_BASE + "articles-training-" + self.config.name + "-20181122.zip?download=1",
                "labels_file": _URL_BASE + "ground-truth-training-" + self.config.name + "-20181122.zip?download=1",
            },
            datasets.Split.TEST: {
                "articles_file": _URL_BASE + "articles-test-" + self.config.name + "-20181207.zip?download=1",
                "labels_file": _URL_BASE + "ground-truth-test-" + self.config.name + "-20181207.zip?download=1",
            },
        }
        if self.config.name == "bypublisher":
            urls[datasets.Split.VALIDATION] = {
                "articles_file": _URL_BASE + "articles-validation-" + self.config.name + "-20181122.zip?download=1",
                "labels_file": _URL_BASE + "ground-truth-validation-" + self.config.name + "-20181122.zip?download=1",
            }
            urls[datasets.Split.TEST] = {
                "articles_file": _URL_BASE + "articles-test-" + self.config.name + "-20181212.zip?download=1",
                "labels_file": _URL_BASE + "ground-truth-test-" + self.config.name + "-20181212.zip?download=1",
            }

        data_dir = {}
        for key in urls:
            data_dir[key] = dl_manager.download_and_extract(urls[key])

        splits = []
        for split in data_dir:
            for key in data_dir[split]:
                data_dir[split][key] = os.path.join(data_dir[split][key], os.listdir(data_dir[split][key])[0])
            splits.append(datasets.SplitGenerator(name=split, gen_kwargs=data_dir[split]))
        return splits

    def _clean_text(self, text):
        """Tokenize text, convert words to lowercase, remove puntuation,
        numbers, stop words, xml entities and image tags.

        Args:
            text (str): text to be cleaned

        Returns:
            str: cleaned text
        """
        # split into tokens
        words = word_tokenize(text)
        # convert to lower case and remove punctuation
        table = str.maketrans('', '', PUNCTUATION)
        words = [str.lower(word.translate(table)) for word in words]
        # remove numbers, stop words, xml entities and image tags
        words = [word for word in words if word.isalpha() and word not in STOPWORDS | ENTITIES | IMAGE]
        # join words to string
        text = " ".join(words)
        # remove extra whitespace
        text = " ".join(text.split())
        # strip whitespace at start and end
        text = text.strip()
        return text

    def _get_class_dict(self, class_tree):
        """Get dictionary of article ids and their hyperpartisan class.

        Args:
            class_tree (xml.etree.ElementTree): class xml document tree

        Returns:
            dict: dictionary of article ids, class, bias and url
        """
        class_dict = {}
        for article in class_tree.xpath("/articles/article"):
            labels = {"hyperpartisan": article.get("hyperpartisan") == "true",
                        "url": article.get("url")}
            if self.config.name == "bypublisher":
                labels["bias"] = article.get("bias")
            class_dict[article.get("id")] = labels
        return class_dict

    def _generate_examples(self, articles_file=None, labels_file=None):
        """Yields examples."""

        # discard whitespace nodes
        parser = etree.XMLParser(remove_blank_text=True)

        # parse article document
        article_tree = etree.parse(articles_file, parser)

        # parse class document
        class_tree = etree.parse(labels_file, parser)

        # get class dict
        class_dict = self._get_class_dict(class_tree)

        # yield examples
        for idx, article in enumerate(article_tree.xpath("/articles/article")):
            example = {}
            example["id"] = article.get("id")
            example["title"] = article.get("title")
            example["published_at"] = article.get("published-at", "")
            example = {**example, **class_dict[example["id"]]}
            example["text"] = article.xpath("string(.)")
            example["clean_text"] = self._clean_text(example["text"])
            yield idx, example
