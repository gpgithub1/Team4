import numpy as np
import tensorflow as tf
import collections
import re
import pandas as pd
import nltk
import itertools
import pickle

def get_conversations():
    with open("questions.txt","r") as f:
        questions_lines=f.read().split(" +++$+++ ")

    with open("answers.txt","r") as f1:
        answers_lines = f1.read().split(" +++$+++ ")


    questions = []
    answers = []

    for line in range(len(questions_lines)):
        questions.append(questions_lines[line])
    questions = questions[:86080]

    for line in range(len(answers_lines)):
        answers.append(answers_lines[line])
    answers = answers[:86080]

    for i in range(0, 9):
        print(questions[i])
        print(answers[i])

    def clean_text(text):
        text = text.lower()
        text = re.sub(r"i'm", "i am", text)
        text = re.sub(r"he's","he is", text)
        text = re.sub(r"she's","she is", text)
        text = re.sub(r"it's","it is", text)
        text = re.sub(r"that's", "that is", text)
        text = re.sub(r"what's", "that is", text)
        text = re.sub(r"where's", "where is", text)
        text = re.sub(r"how's", "how is", text)
        text = re.sub(r"\'ll", " will", text)
        text = re.sub(r"\'ve", " have", text)
        text = re.sub(r"\'re", " are", text)
        text = re.sub(r"\'d", " would", text)
        text = re.sub(r"\'re", " are", text)
        text = re.sub(r"won't", "will not", text)
        text = re.sub(r"can't", "cannot", text)
        text = re.sub(r"n't", " not", text)
        text = re.sub(r"n'", "ng", text)
        text = re.sub(r"'bout", "about", text)
        text = re.sub(r"'til", "until", text)
        text = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,]", "", text)
        return text
    clean_questions = []
    for question in questions:
        clean_questions.append(clean_text(question))


    clean_answers = []
    for answer in answers:
        clean_answers.append(clean_text(answer))

    return clean_questions, clean_answers

def prepare_seq2seq_files(questions, answers, path='',TESTSET_SIZE = 30000):

    # open files
    train_enc = open('train.enc','w')
    train_dec = open('train.dec','w')
    test_enc  = open('test.enc', 'w')
    test_dec  = open('test.dec', 'w')

    # choose 30,000 (TESTSET_SIZE) items to put into testset
    test_ids = random.sample([i for i in range(len(questions))],TESTSET_SIZE)

    for i in range(len(questions)):
        if i in test_ids:
            test_enc.write(questions[i]+'\n')
            test_dec.write(answers[i]+ '\n' )
        else:
            train_enc.write(questions[i]+'\n')
            train_dec.write(answers[i]+ '\n' )
        if i%10000 == 0:
            print('\n>> written {} lines'.format(i))

    # close files
    train_enc.close()
    train_dec.close()
    test_enc.close()
    test_dec.close()

def filter_line(line, whitelist):
    return ''.join([ ch for ch in line if ch in whitelist ])

EN_WHITELIST = '0123456789abcdefghijklmnopqrstuvwxyz ' # space is included in whitelist
EN_BLACKLIST = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\''

limit = {
        'maxq' : 25,
        'minq' : 2,
        'maxa' : 25,
        'mina' : 2
        }

UNK = 'unk'
VOCAB_SIZE = 8000

def filter_data(qseq, aseq):
    filtered_q, filtered_a = [], []
    raw_data_len = len(qseq)

    assert len(qseq) == len(aseq)

    for i in range(raw_data_len):
        qlen, alen = len(qseq[i].split(' ')), len(aseq[i].split(' '))
        if qlen >= limit['minq'] and qlen <= limit['maxq']:
            if alen >= limit['mina'] and alen <= limit['maxa']:
                filtered_q.append(qseq[i])
                filtered_a.append(aseq[i])

    # print the fraction of the original data, filtered
    filt_data_len = len(filtered_q)
    filtered = int((raw_data_len - filt_data_len)*100/raw_data_len)
    print(str(filtered) + '% filtered from original data')

    return filtered_q, filtered_a


'''
 read list of words, create index to word,
  word to index dictionaries
    return tuple( vocab->(word, count), idx2w, w2idx )
'''
def index_(tokenized_sentences, vocab_size):
    # get frequency distribution
    freq_dist = nltk.FreqDist(itertools.chain(*tokenized_sentences))
    # get vocabulary of 'vocab_size' most used words
    vocab = freq_dist.most_common(vocab_size)
    # index2word
    index2word = ['_'] + [UNK] + [ x[0] for x in vocab ]
    # word2index
    word2index = dict([(w,i) for i,w in enumerate(index2word)] )
    return index2word, word2index, freq_dist

'''
 filter based on number of unknowns (words not in vocabulary)
  filter out the worst sentences
'''
def filter_unk(qtokenized, atokenized, w2idx):
    data_len = len(qtokenized)

    filtered_q, filtered_a = [], []

    for qline, aline in zip(qtokenized, atokenized):
        unk_count_q = len([ w for w in qline if w not in w2idx ])
        unk_count_a = len([ w for w in aline if w not in w2idx ])
        if unk_count_a <= 2:
            if unk_count_q > 0:
                if unk_count_q/len(qline) > 0.2:
                    pass
            filtered_q.append(qline)
            filtered_a.append(aline)

    # print the fraction of the original data, filtered
    filt_data_len = len(filtered_q)
    filtered = int((data_len - filt_data_len)*100/data_len)
    print(str(filtered) + '% filtered from original data')

    return filtered_q, filtered_a

def filter_unk_questions(qtokenized, w2idx):
    data_len = len(qtokenized)

    filtered_q = []

    for qline in qtokenize:
        unk_count_q = len([ w for w in qline if w not in w2idx ])
        if unk_count_q > 0:
            if unk_count_q/len(qline) > 0.2:
                pass
        filtered_q.append(qline)


    # print the fraction of the original data, filtered
    filt_data_len = len(filtered_q)
    filtered = int((data_len - filt_data_len)*100/data_len)
    print(str(filtered) + '% filtered from original data')

    return filtered_q



'''
 create the final dataset :
  - convert list of items to arrays of indices
  - add zero padding
      return ( [array_en([indices]), array_ta([indices]) )

'''
def zero_pad(qtokenized, atokenized, w2idx):
    # num of rows
    data_len = len(qtokenized)

    # numpy arrays to store indices
    idx_q = np.zeros([data_len, limit['maxq']], dtype=np.int32)
    idx_a = np.zeros([data_len, limit['maxa']], dtype=np.int32)

    for i in range(data_len):
        q_indices = pad_seq(qtokenized[i], w2idx, limit['maxq'])
        a_indices = pad_seq(atokenized[i], w2idx, limit['maxa'])

        #print(len(idx_q[i]), len(q_indices))
        #print(len(idx_a[i]), len(a_indices))
        idx_q[i] = np.array(q_indices)
        idx_a[i] = np.array(a_indices)

    return idx_q, idx_a


def zero_pad_question(qtokenized, w2idx):
    # num of rows
    data_len = len(qtokenized)

    # numpy arrays to store indices
    idx_q = np.zeros([data_len, limit['maxq']], dtype=np.int32)

    for i in range(data_len):
        q_indices = pad_seq(qtokenized[i], w2idx, limit['maxq'])

        #print(len(idx_q[i]), len(q_indices))
        #print(len(idx_a[i]), len(a_indices))
        idx_q[i] = np.array(q_indices)

    return idx_q


'''
 replace words with indices in a sequence
  replace with unknown if word not in lookup
    return [list of indices]
'''
def pad_seq(seq, lookup, maxlen):
    indices = []
    for word in seq:
        if word in lookup:
            indices.append(lookup[word])
        else:
            indices.append(lookup[UNK])
    return indices + [0]*(maxlen - len(seq))





def process_data():

    clean_questions, clean_answers = get_conversations()

    # change to lower case (just for en)
    clean_questions = [ line.lower() for line in clean_questions ]
    clean_answers = [ line.lower() for line in clean_answers ]

    # filter out unnecessary characters
    print('\n>> Filter lines')
    clean_questions = [ filter_line(line, EN_WHITELIST) for line in clean_questions ]
    clean_answers = [ filter_line(line, EN_WHITELIST) for line in clean_answers ]

    # filter out too long or too short sequences
    print('\n>> 2nd layer of filtering')
    qlines, alines = filter_data(clean_questions, clean_answers)

    for q,a in zip(qlines[141:145], alines[141:145]):
        print('q : [{0}]; a : [{1}]'.format(q,a))

    # convert list of [lines of text] into list of [list of words ]
    print('\n>> Segment lines into words')
    qtokenized = [ [w.strip() for w in wordlist.split(' ') if w] for wordlist in qlines ]
    atokenized = [ [w.strip() for w in wordlist.split(' ') if w] for wordlist in alines ]
    print('\n:: Sample from segmented list of words')

    for q,a in zip(qtokenized[141:145], atokenized[141:145]):
        print('q : [{0}]; a : [{1}]'.format(q,a))

    # indexing -> idx2w, w2idx
    print('\n >> Index words')
    idx2w, w2idx, freq_dist = index_( qtokenized + atokenized, vocab_size=VOCAB_SIZE)

    # filter out sentences with too many unknowns
    print('\n >> Filter Unknowns')
    qtokenized, atokenized = filter_unk(qtokenized, atokenized, w2idx)
    print('\n Final dataset len : ' + str(len(qtokenized)))


    print('\n >> Zero Padding')
    idx_q, idx_a = zero_pad(qtokenized, atokenized, w2idx)

    print('\n >> Save numpy arrays to disk')
    # save them
    np.save('idx_q.npy', idx_q)
    np.save('idx_a.npy', idx_a)

    # let us now save the necessary dictionaries
    metadata = {
            'w2idx' : w2idx,
            'idx2w' : idx2w,
            'limit' : limit,
            'freq_dist' : freq_dist
                }

    # write to disk : data control dictionaries
    with open('metadata.pkl', 'wb') as f:
        pickle.dump(metadata, f)

    # count of unknowns
    unk_count = (idx_q == 1).sum() + (idx_a == 1).sum()
    # count of words
    word_count = (idx_q > 1).sum() + (idx_a > 1).sum()

    print('% unknown : {0}'.format(100 * (unk_count/word_count)))
    print('Dataset count : ' + str(idx_q.shape[0]))

if __name__ == '__main__':
    process_data()


def load_data(path):
    # read data control dictionaries
    with open(path+'metadata.pkl', 'rb') as f:
        metadata = pickle.load(f)
    # read numpy arrays
    idx_q = np.load(path+'idx_q.npy')
    idx_a = np.load(path+'idx_a.npy')
    return metadata, idx_q, idx_a
