import pandas as pd
from gensim import corpora, models, similarities
import tempfile
import logging
import os
from nltk.corpus import stopwords
from string import punctuation
import json 

def lda_analysis(name):

        main_attr = name
        custom_stopwords = ['RT','rt', 'diwali']

        df = pd.read_csv(f"data/{main_attr}.csv")
        df.head()

        tweets = df["text"]
        tweets.info()

        TEMP_FOLDER = tempfile.gettempdir()
        print('Folder "{}" will be used to save temporary dictionary and corpus.'.format(TEMP_FOLDER))

        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

        corpus=[]
        a=[]
        for i in range(len(tweets)):
                a=tweets[i]
                corpus.append(a)
                
        corpus[0:10]


        # removing common words and tokenizing
        stoplist = stopwords.words('english') + list(punctuation) + custom_stopwords

        texts = [[word for word in str(document).lower().split() if word not in stoplist] for document in corpus]

        dictionary = corpora.Dictionary(texts)
        dictionary.save(os.path.join(TEMP_FOLDER, f'{main_attr}.dict'))

        corpus = [dictionary.doc2bow(text) for text in texts]
        corpora.MmCorpus.serialize(os.path.join(TEMP_FOLDER, f'{main_attr}.mm'), corpus)

        tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model

        corpus_tfidf = tfidf[corpus]  # step 2 -- use the model to transform vectors

        total_topics = 15

        lda = models.LdaModel(corpus, id2word=dictionary, num_topics=total_topics)
        corpus_lda = lda[corpus_tfidf] # create a double wrapper over the original corpus: bow->tfidf->fold-in-lsi

        #Show first n important word in the topics:
        top_topics = lda.show_topics(10,5,log=False, formatted=True)
        top_topic = lda.top_topics(corpus)

        avg_topic_coherence = sum([t[1] for t in top_topic]) / total_topics
        print("Average topic coherence: %.4f." % avg_topic_coherence)   

        lda_topics = {i[0]: i[1].split(" + ") for i in lda.print_topics(-1)}

        with open(f"export/{main_attr}/lda_topics.json", "w") as f:
                json.dump(lda_topics, f)

if __name__ == "__main__":
        lda_analysis("worldcup")