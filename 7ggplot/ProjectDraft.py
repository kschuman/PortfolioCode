## Kira Schuman
## ANLY 580 Project


import urllib3
from bs4 import BeautifulSoup
import pandas as pd
import re
import string
import numpy as np
import operator
import metaphone
from difflib import SequenceMatcher
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt
from googletrans import Translator
import googletrans
import seaborn as sns



def get_data(URL):
    # Start urllib3
    http = urllib3.PoolManager()

    # Request data from website
    r = http.request('GET', URL)

    # Parse HTML
    soup = BeautifulSoup(r.data, 'html.parser')

    # Save to file
    with open('rawdata.txt', 'w') as f:
        f.write(soup.get_text())


# From a list of words, returns the one with the most roman letters
# Should choose transliterations over non-roman characters
def get_roman(list):
    ct = {}
    for c in list:
        ct[c] = 0
        for letter in c:
            if letter in string.ascii_lowercase or letter in string.ascii_uppercase:
                ct[c] += 1
    return max(ct.items(), key=operator.itemgetter(1))[0]


def clean_data(file):

    # Read file
    with open(file) as f:
        lines = f.readlines()

    # Get PIE words
    PIE_words_raw = [x for x in lines if x.startswith('*')]


    PIEwords = [lines[lines.index(PIE)].strip('*').strip('\n') for PIE in PIE_words_raw]

    english = [lines[lines.index(PIE) + 1].strip('*').strip('\n') for PIE in PIE_words_raw]

    other_langs = [lines[lines.index(PIE) + 2].strip('*').strip('\n') for PIE in PIE_words_raw]



    #TESTING!!!
    pattern = r'[A-Z]?[a-z]*-?[A-Z][a-z]+\.? ?([A-Z][a-z]+)? ?([A-Z][a-z]+)? '
    prog = re.compile(pattern)
    all_words = {} # to store dictionaries for each word

    for line in other_langs:
        dict = {}
        ix = other_langs.index(line)
        eng_word = english[ix]
        for phrase in line.split(', '):

            try:
                # Match regex to get language
                lang = prog.match(phrase).group().strip()

                # Add language and word to dictionary
                dict[lang] = phrase.split(lang)[1].strip()

            except:
                pass

        all_words[eng_word] = dict


    df = pd.DataFrame.from_dict(all_words)


    df.to_csv('words_and_langs.csv')

    df = pd.read_csv('words_and_langs.csv')
    df = df.rename(columns={'Unnamed: 0': 'Language'})
    df = df.set_index('Language')

    # Patterns
    p1 = re.compile(r'^[-]{0,2}\/[^$]+')  # / or --/ at the beginning
    p2 = re.compile(r'\/$')  # / at the end

    for ix, row in df.iterrows():
        for col in df.columns:
            word = row[col]
            if pd.isnull(word):
                continue

            try:
                df.set_value(row.name, col, p1.match(row[col]).group().strip('--').strip('/'))
                word = row[col]

            except:
                pass

            try:
                df.set_value(row.name, col, p2.match(row[col]).group().strip('--').strip('/'))
                word = row[col]

            except:
                pass

            if '/' in word:
                options = [x.strip('').strip(';') for x in word.split('/')]
                best_option = get_roman(options)
                df.set_value(row.name, col, best_option)
                word = row[col]


            elif ';' in word:
                options = [x.strip('').strip(';') for x in word.split(';')]
                best_option = get_roman(options)
                df.set_value(row.name, col, best_option)
                word = row[col]

            if ' (meaning' in word:
                df.set_value(row.name, col, word.split('(meaning')[0].strip())
                word = row[col]

            elif '(' in word:
                options = [x.strip().strip(')') for x in word.split('(')]
                best_option = get_roman(options)
                df.set_value(row.name, col, best_option)
                word = row[col]

    df.to_csv('words_and_langs.csv')
    return None

## MAYBE GET MISSING WORDS WITH A TRANSLATION API??
## Translate missing words
# List language codes
#googletrans.LANGCODES

translator = Translator()

# example
print(translator.translate('alder', 'cy'))




def get_phonetics(file):
    df = pd.read_csv(file)
    for ix, row in df.iterrows():
        for col in df.columns:
            if col == 'Language':
                continue
            word = row[col]
            if pd.isnull(word):
                continue
            phon = metaphone.doublemetaphone(word)
            df.set_value(row.name, col, phon[0])
    df.to_csv('phonetics.csv')

    return df




# Pull data from website
website = 'https://en.wiktionary.org/wiki/Appendix:List_of_Proto-Indo-European_nouns'
#get_data(website)

# Clean data and save to csv
#clean_data('rawdata.txt')

# Make df of phonetics
df = get_phonetics('words_and_langs.csv')
df = df.set_index('Language')




###############
# GET SIMILARITIES
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# # Similarity matrix for one word
def similarity_matrix(word_series):
    return np.asmatrix([similar(word1, word2)
                 for word1 in word_series
                 for word2 in word_series]).reshape((len(word_series), len(word_series)))




interesting = ['bear', 'beard', 'beast', 'bone', 'dog', 'ear', 'mother', 'earth', 'father', 'heart', 'nail']
#mom = df['mother'][df['mother'].notnull()]


words = pd.read_csv('words_and_langs.csv')
words = words.set_index('Language')

# Plot dendro for each word
#for word in df.columns:
for word in interesting:
    figure, ax = plt.subplots()
    series = df[word][df[word].notnull()]
    y = similarity_matrix(series)

    # Words in each language
    wrddf = words[words[word].notnull()][word]


    # Plot each word
    dendrogram(linkage(y), labels = series.index)
    plt.xticks(rotation = 45, size='small')
    plt.title(word)
    plt.tight_layout()
    plt.show()

# DF for language similarities
similarities = pd.DataFrame(index=df.index, columns = df.index)

# Fill NA with 0
df = df.fillna(0)


# Compare languages
# For every pair of languages, calculate similarities between words (only if both exist)
# Get mean of all word similarities between 2 languages and save to similarities df
for lang1 in df.index:
    for lang2 in df.index:
        if lang1 == lang2:
            similarities.set_value(lang1, lang2, 1)
            continue

        # Save similarities
        sims = []
        for word in df.columns:
            if df.get_value(lang1, word) != 0 and df.get_value(lang2, word) != 0:
                sims.append((similar(df.get_value(lang1, word), df.get_value(lang2, word))))


        if len(sims) > 1:
            #print(np.mean(sims))
            similarities.set_value(lang1, lang2, np.mean(sims))


# NAs to 0
similarities = similarities.fillna(0)

figure, ax = plt.subplots(figsize=(14, 5))
arr = np.asmatrix(similarities)

# Plot each word
dendrogram(linkage(arr), labels=similarities.index)
plt.xticks(rotation=45, size='xx-small')
plt.title('Language Similarities')
plt.tight_layout()
plt.show()
#plt.savefig('langs.pdf')



words = pd.read_csv('words_and_langs.csv')
words = words.set_index('Language')

for word in ['dog']:
    figure, ax = plt.subplots()
    series = df[word][df[word].notnull()]
    y = similarity_matrix(series)
    # Words in each language
    wrddf = words[words[word].notnull()][word]
    wrddf['Lithuanian'] = 'šunį'
    wrddf['Thracian'] = 'dinu'
    wrddf['Lydian'] = 'kan'
    wrddf['Dacian'] = 'kinu'

    # Plot each word
    # dendrogram(linkage(y), labels = series.index)
    # plt.xticks(rotation = 45, size='small')
    # plt.title(word)
    # plt.tight_layout()
    # plt.show()
    f = sns.heatmap(y)

    yticks = []
    for lang in wrddf.index:
        yticks.append('{} // {}'.format(wrddf[lang], lang))


    f.set_yticklabels(labels=yticks, rotation=0)
    f.set_xticklabels(labels=list(wrddf.index), rotation=45)
for word in ['mother']:
    figure, ax = plt.subplots(figsize=(10, 8))
    series = df[word][df[word].notnull()]
    y = similarity_matrix(series)
    # Words in each language
    wrddf = words[words[word].notnull()][word]
    # Plot each word
    # dendrogram(linkage(y), labels = series.index)
    # plt.xticks(rotation = 45, size='small')
    # plt.title(word)
    # plt.tight_layout()
    # plt.show()
    yticks = []
    for lang in wrddf.index:
        yticks.append('{} // {}'.format(wrddf[lang], lang))

    sns.heatmap(y, xticklabels=yticks, yticklabels=yticks)
    yticks = []
    for lang in wrddf.index:
        yticks.append('{} // {}'.format(wrddf[lang], lang))
    # plt.yticks(labels=yticks, rotation=0, size='x-small')
    plt.yticks(rotation=0, size='xx-small')
    plt.xticks(rotation=45, size='xx-small')
    plt.tight_layout()
    plt.title('Similarities Between the Word "Mother" in Indo-European Languages')
    plt.savefig('MotherSim.png')
