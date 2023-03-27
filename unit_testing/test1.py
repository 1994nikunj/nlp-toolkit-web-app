import os
import warnings
from collections import Counter, defaultdict
from math import log

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import pyLDAvis.gensim
from gensim.corpora import Dictionary
from gensim.models.ldamodel import LdaModel
from pandas import DataFrame
from pyvis.network import Network
from scipy.stats import entropy
from wordcloud import WordCloud

warnings.filterwarnings("ignore", '.*the imp module.*')
warnings.filterwarnings("ignore", category=DeprecationWarning, module='wordcloud')
warnings.filterwarnings("ignore", category=FutureWarning, module='pyLDAvis')


class TextAnalysis:
    def __init__(self, data: dict):
        # Files
        self.input_filename: str = data.get('input_file')
        self.raw_words: list = [val.decode('utf-8') for val in data.get('input_raw')]
        self.stopword_filename: str = data.get('stopword_file')
        self.stop_words: list = [val.decode('utf-8') for val in data.get('stopword_raw')]
        self.additional_stopwords: list = data.get('additional_stopwords')
        self.stop_words.extend(self.additional_stopwords)

        # Checkboxes
        self.save_graph: bool = data.get('save_graph')
        self.save_wordcloud: bool = data.get('save_wordcloud')
        self.save_text_statistics: bool = data.get('save_text_statistics')

        # Inputs
        self.n_size: int = data.get('ngram_size')
        self.num_topics: int = data.get('ngram_size')
        self.word_window: int = data.get('word_window')
        self.min_word_length: int = data.get('min_word_length')
        self.num_similar: int = data.get('n_sim_element')

        self.ngrams: list = []
        self.top_comm: list = []
        self.final_output: list = []
        self.vocabulary: set = set()
        self.filtered_words: list = []
        self.result_return: dict = {
            'total_words': 0,
            'unique_words': 0,
            'text_entropy': 0.0,
            'top_ngrams': [],
            'top_topics': []
        }

        self.lda = None
        self.wordcloud = None
        self.top_ngrams = None

    def run_analysis(self) -> dict:
        self.final_output.append(f"This is an analysis for: {self.input_filename}")

        # if self.save_graph:
        #     self._visualize_adjacency_matrix()

        self._text_cleaning(self.raw_words)
        self._generate_ngrams()
        self._calculate_frequency()
        self._print_most_frequent_ngrams()

        # if self.save_graph:
        #     self._generate_wordcloud()

        self._topic_modeling()
        self._calculate_stats()
        self._get_text_statistics()

        # if self.save_text_statistics:
        #     self._write_to_output_file()

        print(self.final_output)

        return self.result_return

    def _visualize_adjacency_matrix(self) -> None:
        adj_matrix = self._co_occurrence()
        # print (adj_matrix)

        G = nx.from_pandas_adjacency(adj_matrix)
        visual_graph = Network(
            height="500px",
            bgcolor="#222222",
            font_color="white"
        )
        visual_graph.from_nx(G)
        visual_graph.show_buttons(filter_=['physics'])

        graph_name = '{}.{}'.format(self.input_filename.replace('.txt', ''), 'html')
        visual_graph.save_graph(graph_name)

    def _text_cleaning(self, words) -> None:
        # Split the modified text into individual words
        words = ' '.join(words).split()

        # Filter out stop words and non-alphabetic words
        filtered_words = [word.lower() for word in words if
                          word.lower() not in self.stop_words and word.isalpha() and len(word) > self.min_word_length]

        # Update the filtered words and vocabulary lists
        self.filtered_words = filtered_words
        self.vocabulary = set(filtered_words)

    def _generate_ngrams(self) -> None:
        self.ngrams = ['_'.join(self.filtered_words[i:i + self.n_size]) for i in
                       range(len(self.filtered_words) - self.n_size + 1)]

    def _calculate_frequency(self) -> None:
        self.top_comm = [ngram for ngram, count in Counter(self.ngrams).most_common(self.num_similar)]

    def _print_most_frequent_ngrams(self) -> None:
        self.top_ngrams = ["{}. {}".format(_id + 1, ngram) for _id, ngram in enumerate(self.top_comm)]
        self.result_return['top_ngrams'] = self.top_ngrams
        self.final_output.append(
            '\nThe following are the top {}-grams: \n\t{}'.format(self.n_size, '\n\t'.join(self.top_ngrams)))

    def _generate_wordcloud(self) -> None:
        all_words_string = ' '.join(self.filtered_words + self.top_comm)
        all_stopwords_string = set(' '.join(self.stop_words))

        # defining the wordcloud parameters
        self.wordcloud = WordCloud(background_color="white",
                                   max_words=2000,
                                   stopwords=all_stopwords_string)

        # generate words cloud
        self.wordcloud_generated = self.wordcloud.generate(all_words_string)

        _file = '{}.{}'.format(self.input_filename.replace('.txt', ''), 'png')
        self.wordcloud.to_file(filename=_file)

        plt.imshow(self.wordcloud)
        plt.axis('off')
        plt.show()

    def _topic_modeling(self) -> None:
        tokens = [x.split() for x in self.filtered_words]
        dictionary = Dictionary(tokens)
        corpus = [dictionary.doc2bow(text) for text in tokens]

        self.lda = LdaModel(corpus=corpus,
                            num_topics=self.num_topics,
                            id2word=dictionary)

        self.final_output.append(f'\nThe following are the top {self.num_topics} topics:')
        for i, topic in enumerate(self.lda.show_topics(num_topics=self.num_topics)):
            top_words = self.lda.show_topics(self.num_topics)[i][1]
            self.final_output.append(f"\tTopic {i + 1}: {top_words}")
            self.result_return['top_topics'].append(f"Topic {i + 1}: {top_words}")

        lda_display = pyLDAvis.gensim.prepare(self.lda, corpus, dictionary, sort_topics=False)

        return pyLDAvis.display(lda_display)

    def _co_occurrence(self) -> DataFrame:
        d = defaultdict(int)
        vocab = set()
        for text in self.raw_words:
            text = text.lower().split()
            self._text_cleaning(text)
            for i in range(len(self.filtered_words)):
                token = self.filtered_words[i]
                vocab.add(token)
                next_token = self.filtered_words[i + 1: i + 1 + self.word_window]
                for t in next_token:
                    key = tuple(sorted([t, token]))
                    d[key] += 1

        vocab = sorted(vocab)
        df = pd.DataFrame(data=np.zeros((len(vocab), len(vocab)), dtype=np.int16),
                          index=vocab,
                          columns=vocab)

        for key, value in d.items():
            df.at[key[0], key[1]] = value
            df.at[key[1], key[0]] = value

        return df

    def _calculate_stats(self) -> None:
        words_counter = Counter(self.filtered_words)
        word_freq_lst = list(words_counter.values())

        self.result_return['text_entropy'] = round(log(entropy(word_freq_lst, base=10), 10), 2)
        self.result_return['total_words'] = len(self.filtered_words)
        self.result_return['unique_words'] = len(self.vocabulary)

    def _get_text_statistics(self) -> None:
        message = '\nThe following are some basic statistics on the input text:' \
                  f'\n\tTotal Words: {self.result_return["total_words"]}' \
                  f'\n\tTotal Unique words: {self.result_return["unique_words"]}' \
                  f'\n\tTotal Text Entropy: {self.result_return["text_entropy"]}'
        self.final_output.append(message)

    def _write_to_output_file(self):
        output_file = f'{os.getcwd()}\\output_{self.input_filename}'
        with open(output_file, 'w') as fr:
            fr.write('\n'.join(self.final_output))


if __name__ == '__main__':
    _data = {'input_file_name': 'Robert_Liu.txt',
             'input_raw': [b'My', b'name', b'is', b'Robert', b'Liu', b'and', b"i'm", b'a', b'mathematician', b'and',
                           b'quickly', b'pivoted', b'to', b'becoming', b'an', b'IT', b'engineer.', b'Strategic',
                           b'coding',
                           b'helped', b'me', b'join', b'Deloitte.', b'Worked', b'in', b'the', b'domains', b'of',
                           b'data',
                           b'science,', b'predictive', b'analytics', b'in', b'the', b'US', b'Navy.', b'Few', b'years',
                           b'ago,', b'I', b'left', b'Deloitte', b'and', b'joined', b'a', b'multi-national', b'bank',
                           b'as',
                           b'a', b'Data', b'Science', b'Director.', b'Currently', b'work', b'as', b'a', b'Chief',
                           b'Data',
                           b'officer', b'and', b'a', b'Chief', b'Technical', b'Officer.', b'I', b'consider', b'some',
                           b'of',
                           b'the', b'understanding', b'has', b'to', b'be', b'technical', b'and', b'some', b'skills',
                           b'needed', b'to', b'push', b'things', b'forward', b'are', b'non-technical.', b'I', b'think',
                           b'Digital', b'Engineering', b'is', b'one', b'of', b'those', b'buzz', b'words', b'that',
                           b'are',
                           b'going', b'on', b'in', b'the', b'industry.', b'Being', b'digital', b"doesn't",
                           b'necessarily',
                           b'mean', b'you', b'need', b'to', b'have', b'a', b'digital', b'background.', b'Humans',
                           b'use',
                           b'Artificial', b'Intelligence', b'and', b'Machine', b'Learning', b'in', b'business', b'for',
                           b'automating', b'several', b'tasks.', b'In', b'recent', b'years', b'we', b'have', b'the',
                           b'capability', b'to', b'go', b'beyond', b'Artificial', b'Intelligence', b'for', b'autonomy.',
                           b'Today', b'we', b'have', b'a', b'narrow', b'type', b'of', b'Artificial', b'Intelligence',
                           b'\xe2\x80\x93', b'play', b'a', b'game', b'or', b'decide', b'what', b'documents', b'belongs',
                           b'to', b'which', b'class', b'and', b'it', b'has', b'a', b'narrow', b'task.', b'In', b'the',
                           b'past,', b'automation', b'was', b'what', b'we', b'considered', b'Artificial',
                           b'Intelligence,',
                           b'it', b'is', b'different', b'today.', b'Narrow', b'tasks', b'that', b'rely', b'on',
                           b'machine',
                           b'learning', b'are', b'the', b'primary', b'driver', b'in', b'the', b'workforce.', b'When',
                           b'I',
                           b'was', b'working', b'in', b'the', b'bank', b'back', b'in', b'2014', b'with', b'the',
                           b'Data',
                           b'Science', b'team,', b'it', b'was', b'the', b'first', b'time', b'I', b'used', b'the',
                           b'term',
                           b'Data', b'Science.', b'I', b'think', b'Data', b'Science', b'and', b'Data', b'Analytics',
                           b'are',
                           b'the', b'pathway', b'for', b'getting', b'into', b'Artificial', b'Intelligence.', b'First',
                           b'half', b'is', b'that', b'the', b'scientific', b'endeavor', b'that', b'the', b'scientists',
                           b'perform', b'can', b'take', b'the', b'experiments', b'beyond', b'outside', b'of', b'their',
                           b'work.', b'The', b'second', b'half', b'is', b'the', b'Artificial', b'Intelligence',
                           b'\xe2\x80\x93', b'data', b'collected', b'from', b'the', b'sensors', b'and', b'perception.',
                           b'All', b'three', b'definitions', b'are', b'somewhat', b'narrow,', b'and', b'I', b'think',
                           b'we',
                           b'have', b'to', b'simplify', b'them', b'a', b'bit.', b'I', b"don't", b'disagree', b'with',
                           b'these', b'definitions.', b'They', b'are', b'correct', b'but', b'narrow.', b'Core',
                           b'skillset',
                           b'is', b'to', b'be', b'able', b'to', b'recognize', b'the', b'potential', b'for', b'data',
                           b'as',
                           b'a', b'decision', b'tool', b'and', b'understand', b'how', b'a', b'business', b'operates.',
                           b'Critical', b'skills', b'\xe2\x80\x93', b"I'd", b'think', b'of', b'it', b'as', b'a',
                           b'task',
                           b'to', b'become', b'the', b'Chief', b'Technical', b'Officer.', b"I'd", b'look', b'for',
                           b'someone', b'from', b'the', b'80s', b'or', b'90s', b'who', b'have', b'a', b'good',
                           b'understanding', b'of', b'digital', b'engineering', b'and', b'business', b'analysis.',
                           b'The',
                           b'folks', b'at', b'two', b'camps', b'used', b'the', b'sensors', b'to', b'capture', b'data',
                           b'and', b'used', b'Artificial', b'Intelligence', b'and', b'Machine', b'Learning',
                           b'algorithms',
                           b'to', b'work', b'on', b'domains', b'from', b'Computer', b'Vision', b'to', b'Auditory',
                           b'to',
                           b'chemical', b'sign', b'detection.', b'First', b'half', b'has', b'a', b'certain', b'part',
                           b'of',
                           b'the', b'responsibility', b'of', b'collecting', b'data,', b'curating', b'and',
                           b'preprocessing',
                           b'the', b'data.', b'The', b'other', b'half', b'\xe2\x80\x93', b'the', b'Data', b'science',
                           b'folks', b'and', b'people', b'who', b'work', b'in', b'psychology', b'or', b'neuroscience',
                           b'use', b'artificial', b'intelligence', b'and', b'machine', b'learning,', b'robotic',
                           b'process',
                           b'automation,', b'the', b'IT', b'technician', b'must', b'have', b'the', b'ability', b'to',
                           b'use',
                           b'Artificial', b'Intelligence', b'and', b'Machine', b'Learning', b'algorithms.', b'Small',
                           b'unit', b'maneuver,', b'vehicles', b'can', b'do', b'things', b'that', b'humans', b'used',
                           b'to',
                           b'do', b'before', b'using', b'Machine', b'Learning,', b'sensors,', b'robotics.', b'Data',
                           b'Analytics', b'has', b'been', b'used', b'for', b'the', b'past', b'two', b'decades.', b'I',
                           b'think', b'the', b'days', b'of', b'a', b'database', b'technician', b'are', b'numbered.',
                           b'The',
                           b'data', b'is', b'collected', b'in', b'an', b'unstructured', b'lake,', b'can', b'be',
                           b'central',
                           b'or', b'distributed.', b'Data', b'Analytics', b'include', b'multiple', b'types', b'of',
                           b'data,',
                           b'systems,', b'APIs,', b'basic', b'machine', b'learning', b'algorithms,', b'predictive',
                           b'analytics.', b'Top', b'tier', b'data', b'scientists,', b'data', b'analytics', b'that',
                           b'have',
                           b'the', b'ability', b'to', b'use', b'neural', b'networks,', b'adversarial', b'networks,',
                           b'Reinforcement', b'Learning.', b'Data', b'modeling', b'is', b'the', b'key', b'piece',
                           b'here.',
                           b'We', b'need', b'to', b'get', b'a', b'lot', b'better', b'with', b'digital', b'engineering.',
                           b'There', b'is', b'a', b'lot', b'of', b'data', b'out', b'there', b'and', b'using', b'the',
                           b'curated', b'data', b'for', b'learning', b'is', b'great.', b'Failure', b'of', b'big',
                           b'data',
                           b'era', b'that', b'came', b'and', b'went.', b'Humans', b"can't", b'understand', b'the',
                           b'data',
                           b"that's", b'coming', b'in', b'which', b'makes', b'digital', b'engineering', b'important.',
                           b'I',
                           b'think', b'digital', b'engineering,', b'software', b'literacy,', b'digital', b'literacy',
                           b'needs', b'to', b'be', b'addressed.', b'Everything', b'needs', b'to', b'be', b'addressed.',
                           b'Natural', b'Language', b'processing', b'\xe2\x80\x93', b'not', b'there', b'yet.', b'We',
                           b'used', b'a', b'number', b'of', b'natural', b'language', b'systems', b'at', b'the', b'bank',
                           b'which', b'involved', b'curating', b'and', b'characterizing', b'the', b'data', b'in',
                           b'the',
                           b'backend.', b'A', b'lot', b'of', b'work', b'needs', b'to', b'be', b'done', b'there', b'in',
                           b'the', b'navy.', b'Data', b'analytics', b'involves', b'layered', b'and', b'semantic',
                           b'complexity.', b'Data', b'is', b'what', b'a', b'human', b'can', b'see', b'and',
                           b'perceive.',
                           b'Most', b'of', b'the', b'data', b'is', b'unstructured.', b'Tagging', b'the', b'data', b'is',
                           b'a', b'challenge.', b'Learning', b'new', b'algorithms', b'and', b'constant', b'training',
                           b'is',
                           b'required.', b'Interested', b'in', b'all', b'of', b'those', b'areas.', b'There', b'are',
                           b'folks', b'that', b"don't", b'understand', b'hardware', b'and', b'software.', b'Folks',
                           b'are',
                           b'not', b'a', b'neural', b'network,', b'reinforcement', b'learning', b'expert,', b'not',
                           b'a',
                           b'psychologist,', b'neuroscientist.', b'Will', b'need', b'many', b'years', b'to', b'become',
                           b'an', b'expert', b'in', b'all', b'of', b'these', b'areas.'],
             'stopword_file': 'stopwords_en.txt',
             'stopword_raw': [b'a', b'about', b'above', b'across', b'after', b'afterwards', b'again', b'against',
                              b'all',
                              b'almost', b'alone', b'along', b'already', b'also', b'although', b'always', b'am',
                              b'among',
                              b'amongst', b'amoungst', b'amount', b'amp', b'ams', b'an', b'and', b'another', b'any',
                              b'anyhow', b'anyone', b'anything', b'anyway', b'anywhere', b'are', b'around', b'as',
                              b'at',
                              b'back', b'be', b'became', b'because', b'become', b'becomes', b'becoming', b'been',
                              b'before',
                              b'beforehand', b'behind', b'being', b'below', b'beside', b'besides', b'between',
                              b'beyond',
                              b'bill', b'both', b'bottom', b'but', b'by', b'call', b'can', b'cannot', b'cant', b'co',
                              b'con',
                              b'could', b'couldnt', b'cry', b'de', b'describe', b'detail', b'do', b'done', b'dont',
                              b'down',
                              b'due', b'during', b'each', b'eg', b'eight', b'either', b'eleven', b'else', b'elsewhere',
                              b'empty', b'enough', b'est', b'etc', b'even', b'ever', b'every', b'everyone',
                              b'everything',
                              b'everywhere', b'except', b'few', b'fifteen', b'fify', b'fill', b'find', b'fire',
                              b'first',
                              b'five', b'for', b'former', b'formerly', b'forty', b'found', b'four', b'from', b'front',
                              b'full', b'further', b'get', b'give', b'go', b'had', b'has', b'hasnt', b'have', b'he',
                              b'hence', b'her', b'here', b'hereafter', b'hereby', b'herein', b'hereupon', b'hers',
                              b'herself', b'him', b'himself', b'his', b'how', b'however', b'http', b'https', b'hundred',
                              b'i', b'ie', b'if', b'im', b'in', b'inc', b'indeed', b'interest', b'into', b'is', b'it',
                              b'its', b'itself', b'keep', b'last', b'latter', b'latterly', b'least', b'less', b'ltd',
                              b'made', b'many', b'may', b'me', b'meanwhile', b'might', b'mill', b'mine', b'more',
                              b'moreover', b'most', b'mostly', b'move', b'much', b'must', b'my', b'myself', b'name',
                              b'namely', b'neither', b'never', b'nevertheless', b'next', b'new', b'newyork', b'nine',
                              b'no',
                              b'nobody', b'none', b'noone', b'nor', b'not', b'nothing', b'now', b'nowhere', b'of',
                              b'off',
                              b'often', b'on', b'once', b'one', b'only', b'onto', b'or', b'other', b'others',
                              b'otherwise',
                              b'our', b'ours', b'ourselves', b'out', b'over', b'own', b'part', b'per', b'perhaps',
                              b'please',
                              b'pm', b'put', b'rather', b're', b'same', b'see', b'seem', b'seemed', b'seeming',
                              b'seems',
                              b'serious', b'several', b'she', b'should', b'show', b'side', b'since', b'sincere', b'six',
                              b'sixty', b'so', b'some', b'somehow', b'someone', b'something', b'sometime', b'sometimes',
                              b'somewhere', b'still', b'such', b'system', b'take', b'ten', b'than', b'that', b'thats',
                              b'the', b'their', b'them', b'themselves', b'then', b'thence', b'there', b'thereafter',
                              b'thereby', b'therefore', b'therein', b'thereupon', b'these', b'they', b'thick', b'thin',
                              b'third', b'this', b'those', b'though', b'three', b'through', b'throughout', b'thru',
                              b'thus',
                              b'to', b'together', b'too', b'top', b'toward', b'towards', b'twelve', b'twenty', b'two',
                              b'un',
                              b'under', b'until', b'up', b'upon', b'us', b'very', b'via', b'was', b'we', b'well',
                              b'were',
                              b'what', b'whatever', b'when', b'whence', b'whenever', b'where', b'whereafter',
                              b'whereas',
                              b'whereby', b'wherein', b'whereupon', b'wherever', b'whether', b'which', b'while',
                              b'whither',
                              b'who', b'whoever', b'whole', b'whom', b'whose', b'why', b'will', b'with', b'within',
                              b'without', b'would', b'yet', b'york', b'you', b'your', b'yours', b'yourself',
                              b'yourselves'],
             'additional_stopwords': ['data,', 'digital,', 'today,', 'use'], 'save_graph': False,
             'save_wordcloud': False,
             'save_text_statistics': False, 'ngram_size': 2, 'number_of_topics': 5, 'min_word_length': 2,
             'word_window': 4,
             'n_sim_element': 2}

    text_analyzer = TextAnalysis(data=_data)
    res = text_analyzer.run_analysis()
    print(res)
