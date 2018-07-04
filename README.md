# Web Retrieval Engine Implementation for University Domain [Python, Django, Anaconda]
Implemented web Retrieval/ Search engine by building custom crawler, preprocessor, query processor and retrieval engine evaluator.
1. Run main we crawler. Can change to website and web domain of choice.
2. Run TF-IDF calclutor.
3. Enter query term for retrieving or searching.
4. Can you version with interface. Django and python is required

Implementation & Feature Details:	
-	Developed vector space model based ad-hoc web retrieval engine and applied on 10, 000 webpages and docs (text, pdf, docx and pptx) fetched from University of Memphis domain (memphis.edu).
-	Used TF-IDF vector space model for webpage matching and cosine similarity function for webpage ranking.
-	Developed modules - web crawler (incremental), text preprocessor(removes- (markup, metadata, uppercase, digits, punctuation, space,  stop words), tokenization, stemming), Indexer (doc-url, doc-term, term-doc), TF-IDF vector generator, webpage relevance ranker and performance evaluator (F1, precision, recall). 

