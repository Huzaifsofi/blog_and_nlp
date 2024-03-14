import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import nltk
import re

nltk.download('punkt')
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import cmudict, stopwords
import string

nltk.download('cmudict')
nltk.download('stopwords')

cmu_dict = cmudict.dict()
english_stopwords = set(stopwords.words('english'))
punctuation = set(string.punctuation)



class Defaultsetup:
    def __init__(self):
        self.stop_word_list = []

    def DirectrySetup(self):
        folder_name = 'articles'
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        else:
            print(f"Folder '{folder_name}' already exists.")

        data = [
            'URL_ID',
            'URL',
            'POSITIVE SCORE',
            'NEGATIVE SCORE',
            'POLARITY SCORE',
            'SUBJECTIVITY SCORE',
            'AVG SENTENCE LENGTH',
            'PERCENTAGE OF COMPLEX WORDS',
            'FOG INDEX',
            'AVG NUMBER OF WORDS PER SENTENCE',
            'COMPLEX WORD COUNT',
            'WORD COUNT',
            'SYLLABLE PER WORD',
            'PERSONAL PRONOUNS',
            'AVG WORD LENGTH',
        ]

        df = pd.DataFrame(columns=data)
        file_path = 'output_file.xlsx'

        df.to_excel(file_path, index=False)

    def TokenizerStopword(self):
        file_paths_list = ['./StopWords/StopWords_Auditor.txt', './StopWords/StopWords_Currencies.txt', './StopWords/StopWords_DatesandNumbers.txt', './StopWords/StopWords_Generic.txt', './StopWords/StopWords_GenericLong.txt']

        for file_path in file_paths_list: 
            # Open the text file in read mode
            with open(file_path, 'r') as file:
                # Read the entire content of the file
                stop_word = file.read()
                
                doc = word_tokenize(stop_word)

                for token in doc:
                    # Remove leading and trailing spaces from each token
                    stripped_token = token.strip()
                    # Check if the stripped token is not an empty string
                    if stripped_token:
                        # Append the stripped token to the list
                        self.stop_word_list.append(stripped_token.lower())
        return self.stop_word_list


class TextExtrater:
    def __init__(self):
        self.article_list = []


    def Data_scraper(self):
        self.article_list.clear()
        file_path = 'Input.xlsx'

        df = pd.read_excel(file_path)

        for index ,row in df.iterrows():
            id = row['URL_ID']
            url = row['URL']

            response = requests.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                title_element_1 = soup.find('h1', class_='entry-title')
                paragraph_element_1 = soup.find('div', class_='td-post-content tagdiv-type')

                title_element_2 = soup.find('h1', class_='tdb-title-text')
                paragraph_element_2 = soup.find('div', class_="tdb-block-inner td-fix-index")

                if title_element_1 and paragraph_element_1:
                    article_title = title_element_1.text.strip()  # Strip whitespace from the title
                    article_text = paragraph_element_1.get_text().strip()  # Strip whitespace from the text and handle line breaks
                    
                    article_data_1 = {
                        'URL_ID': id,
                        'URL': url,
                        'article_title': article_title,
                        'article_text': article_text,
                    }

                    self.article_list.append(article_data_1)
                    print(id)

                elif title_element_2 and paragraph_element_2:
                        article_title = title_element_2.text.strip()  # Strip whitespace from the title
                        article_text = paragraph_element_2.get_text().strip()  # Strip whitespace from the text and handle line breaks
                    
                        article_data_2 = {
                            'URL_ID': id,
                            'URL': url,
                            'article_title': article_title,
                            'article_text': article_text,
                        }

                        self.article_list.append(article_data_2)
                        print(id)
                else:
                    pass

            else:
                print(f"Failed to fetch URL for article with ID {id}. Status code: {response.status_code}")
        return self.article_list



class TextProcesser:
    def Article_Files(self, entrys):
        folder_name = 'articles'
        with open(f"./{folder_name}/{entrys['URL_ID']}.txt", 'w', encoding='utf-8') as file:
            file.write(entrys['article_title'] + "\n\n")  # Write title with blank lines before and after
            file.write(entrys['article_text'])  # Write article text
            print(f"file created: {entrys['URL_ID']}")

    def TokenizArticele(self, article_list):
        article_token_list = []
        article_title = article_list['article_title']
        article_text = article_list['article_text']

        all_txt = article_title + "\n\n" + article_text

        doc = word_tokenize(all_txt)

        for token in doc:
            # Remove leading and trailing spaces from each token
            stripped_token = token.strip()
            # Check if the stripped token is not an empty string
            if stripped_token:
                # Append the stripped token to the list
                article_token_list.append(stripped_token)
        return article_token_list

    def TokenizeSentense(self, article_list):
        article_token_sentence_list = []
        article_title = article_list['article_title']
        article_text = article_list['article_text']

        all_txt = article_title + "\n\n" + article_text

        doc = sent_tokenize(all_txt)

        for token in doc:
            # Remove leading and trailing spaces from each token
            stripped_token = token.strip()
            # Check if the stripped token is not an empty string
            if stripped_token:
                # Append the stripped token to the list
                article_token_sentence_list.append(stripped_token)
        return article_token_sentence_list


    def Filter_article(self, tokenized_article, stop_word_list):
        article_filtered_list = []

        for word in tokenized_article:
            if word.lower() not in stop_word_list:
                article_filtered_list.append(word)
        return article_filtered_list
    



class Data_Anyliser:

    def FindSumPostive(self, article_filtered_list):
        positive_word = 0
        positive_word_path = "./MasterDictionary/positive-words.txt"

        with open(positive_word_path, 'r') as file:
            positive_word_list = file.read().splitlines()

        for item in positive_word_list:
            if item in article_filtered_list:
                positive_word += 1
        return positive_word


    def FimSumNegative(self, article_filtered_list):
        negative_word = 0
        nagtive_word_path = "./MasterDictionary/negative-words.txt"

        with open(nagtive_word_path, 'r') as file:
            negative_word_list = file.read().splitlines()

        for item in negative_word_list:
            if item in article_filtered_list:
                negative_word += 1
        return negative_word
    
    def FindPolaritySum(self, positive_points, negative_points):
        Polarity_Score_raw = (positive_points - negative_points) / ((positive_points + negative_points) + 0.000001)
        Polarity_Score = round(Polarity_Score_raw)
        return Polarity_Score

    def FindSubjectivityScore(self, positive_points, negative_points):
        Subjectivity_Score = (positive_points + negative_points) / ((len(article_filtered_list)) + 0.000001)
        return round(Subjectivity_Score)
    
    def Find_Average_Sentence_Length(self, tokenized_article, TokenizeSentense):
        Average_Sentence_Length_raw = len(tokenized_article) / len(TokenizeSentense)
        Average_Sentence_Length = "{:.2f}".format(Average_Sentence_Length_raw)
        return Average_Sentence_Length
    
    def Find_Percentage_of_Complex_words(self, tokenized_article):
        complex_word_count = 0

        for word in tokenized_article:
            pronunciations = cmu_dict.get(word.lower())
            
            if pronunciations and len(pronunciations[0]) > 2:
                complex_word_count += 1
        complex_words = round((complex_word_count / len(tokenized_article)) * 100)
        return complex_words
    
    def Find_Fog_Index(self, Average_Sentence_Length, complex_words):
        Fog_Index = 0.4 * (float(Average_Sentence_Length) + float(complex_words))
        return Fog_Index
    
    def Average_Number_of_Words_Per_Sentence(self, tokenized_article, TokenizeSentense):
        Average_Sentence_Word_raw = len(tokenized_article) / len(TokenizeSentense)
        Average_Sentence_Word = "{:.2f}".format(Average_Sentence_Word_raw)
        return Average_Sentence_Word

    def Find_Complex_Word_Count(self, tokenized_article):
        complex_word_count = 0

        for word in tokenized_article:
            pronunciations = cmu_dict.get(word.lower())
            
            if pronunciations and len(pronunciations) > 2:
                complex_word_count += 1
        return complex_word_count
    
    def Find_Word_count(self, tokenized_article):
        nltk_filter_words = []

        for word in tokenized_article:
            if word.lower() not in english_stopwords and word not in punctuation and word.isalnum():
                nltk_filter_words.append(word)
        return nltk_filter_words
    

    def Find_Syllable_Count_Per_Word(self, articles):
        article_title = articles['article_title']
        article_text = articles['article_text']

        text = article_title + article_text

        vowel_pattern = r'[aeiouyAEIOUY]+'
        exception_pattern = r'(es|ed)$'

        # Compile regex patterns
        vowel_regex = re.compile(vowel_pattern)
        exception_regex = re.compile(exception_pattern)

        # Tokenize the text into words
        words = text.split()

        total_syllable_count = 0

        # Count syllables for each word
        for word in words:
            # Find all matches of vowels in the word
            vowels = vowel_regex.findall(word)

            # Find all matches of exceptions in the word
            exceptions = exception_regex.search(word)

            # Count the number of syllables based on vowels and exceptions
            syllable_count = len(vowels)

            # Handle exceptions (subtract syllable if the word ends with "es" or "ed")
            if exceptions:
                syllable_count -= 1

            # Ensure at least one syllable if syllable count is zero
            if syllable_count == 0:
                syllable_count = 1

            total_syllable_count += syllable_count

        return total_syllable_count




    def Find_Personal_Pronouns(self, articles):
        article_title = articles['article_title']
        article_text = articles['article_text']

        all_txt = article_title + article_text


        pronoun_pattern = r'\b(?:I|we|my|ours|us)\b'

        pronoun_regex = re.compile(pronoun_pattern, flags=re.IGNORECASE)

        text = ' '.join(all_txt)
        
        matches = pronoun_regex.findall(text)

        count = len(matches)

        return count
    


    def Find_Average_Word_Length(self, tokenized_words):
        total_characters = 0
        total_words = len(tokenized_words)

        # Calculate the total number of characters in all words
        for word in tokenized_words:
            total_characters += len(word)

        # Calculate the average word length
        average_word_length_raw = total_characters / total_words if total_words > 0 else 0

        average_word_length = "{:.2f}".format(average_word_length_raw)
        return average_word_length
    

    def AligValue(self, articles, positive_points, negative_points, Polarity_Score, Subjectivity_Score, Average_Sentence_Length, complex_words, Fog_Index, Average_Sentence_Word_per_sen, Complex_Word_Count, Word_count, Syllable_Count_Per_Word, Personal_Pronouns, Average_Word_Length):
        articles['POSITIVE SCORE'] = positive_points
        articles['NEGATIVE SCORE'] = negative_points
        articles['POLARITY SCORE'] = Polarity_Score
        articles['SUBJECTIVITY SCORE'] = Subjectivity_Score
        articles['AVG SENTENCE LENGTH'] = Average_Sentence_Length
        articles['PERCENTAGE OF COMPLEX WORDS'] = complex_words
        articles['FOG INDEX'] = Fog_Index
        articles['AVG NUMBER OF WORDS PER SENTENCE'] = Average_Sentence_Word_per_sen
        articles['COMPLEX WORD COUNT'] = Complex_Word_Count
        articles['WORD COUNT'] = len(Word_count)
        articles['SYLLABLE PER WORD'] = Syllable_Count_Per_Word
        articles['PERSONAL PRONOUNS'] = Personal_Pronouns
        articles['AVG WORD LENGTH'] = Average_Word_Length


    def Add_Value_file(self, articles):
        existing_data = pd.read_excel('output_file.xlsx')

        # New data to add
        new_data = pd.DataFrame({
            'URL_ID': [articles['URL_ID']],
            'URL': [articles['URL']],
            'POSITIVE SCORE': [articles['POSITIVE SCORE']],
            'NEGATIVE SCORE': [articles['NEGATIVE SCORE']],
            'POLARITY SCORE': [articles['POLARITY SCORE']],
            'SUBJECTIVITY SCORE': [articles['SUBJECTIVITY SCORE']],
            'AVG SENTENCE LENGTH': [articles['AVG SENTENCE LENGTH']],
            'PERCENTAGE OF COMPLEX WORDS': [articles['PERCENTAGE OF COMPLEX WORDS']],
            'FOG INDEX': [articles['FOG INDEX']],
            'AVG NUMBER OF WORDS PER SENTENCE': [articles['AVG NUMBER OF WORDS PER SENTENCE']],
            'COMPLEX WORD COUNT': [articles['COMPLEX WORD COUNT']],
            'WORD COUNT': [articles['WORD COUNT']],
            'SYLLABLE PER WORD': [articles['SYLLABLE PER WORD']],
            'PERSONAL PRONOUNS': [articles['PERSONAL PRONOUNS']],
            'AVG WORD LENGTH': [articles['AVG WORD LENGTH']],
        })

        # Remove any empty columns from new_data
        new_data = new_data.dropna(axis=1, how='all')

        # Concatenate existing data with new data
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)

        # Write the combined data back to Excel
        combined_data.to_excel('output_file.xlsx', index=False)


Setup = Defaultsetup()
Setup.DirectrySetup()
stop_word_list = Setup.TokenizerStopword()

Exterter = TextExtrater()
article_list = Exterter.Data_scraper()

for articles in article_list:
    print(articles)
    Processer = TextProcesser()

    Processer.Article_Files(articles)

    tokenized_article = Processer.TokenizArticele(articles)
    print(f"token {len(tokenized_article)}")

    TokenizeSentense = Processer.TokenizeSentense(articles)
    print(f" TokenizeSentense: {len(TokenizeSentense)}")

    article_filtered_list = Processer.Filter_article(tokenized_article, stop_word_list)
    print(f"filter {len(article_filtered_list)}")

    Anilizer = Data_Anyliser()
    positive_points = Anilizer.FindSumPostive(article_filtered_list)
    negative_points = Anilizer.FimSumNegative(article_filtered_list)
    print(f"positive: {positive_points}")
    print(f"negative: {negative_points}")
    
    Polarity_Score = Anilizer.FindPolaritySum(positive_points, negative_points)
    print(f"Polarity_Score: {Polarity_Score}")

    Subjectivity_Score = Anilizer.FindSubjectivityScore(positive_points, negative_points)
    print(f"Subjectivity_Score: {Subjectivity_Score}")

    Average_Sentence_Length = Anilizer.Find_Average_Sentence_Length(tokenized_article, TokenizeSentense)
    print(f"Average_Sentence_Length: {Average_Sentence_Length}")

    complex_words = Anilizer.Find_Percentage_of_Complex_words(tokenized_article)
    print(f"complex_words: {complex_words}")

    Fog_Index = Anilizer.Find_Fog_Index(Average_Sentence_Length, complex_words)
    print(f"Fog_Index: {Fog_Index}")

    Average_Sentence_Word_per_sen = Anilizer.Average_Number_of_Words_Per_Sentence(tokenized_article, TokenizeSentense)
    print(f"Average_Sentence_Word: {Average_Sentence_Word_per_sen}")

    Complex_Word_Count = Anilizer.Find_Complex_Word_Count(tokenized_article)
    print(f"Complex_Word_Count: {Complex_Word_Count}")

    Word_count = Anilizer.Find_Word_count(tokenized_article)
    print(f"Word_count: {len(Word_count)}")

    Syllable_Count_Per_Word = Anilizer.Find_Syllable_Count_Per_Word(articles)
    print(f"Syllable_Count_Per_Word: {Syllable_Count_Per_Word}")

    Personal_Pronouns = Anilizer.Find_Personal_Pronouns(articles)
    print(f"Personal_Pronouns: {Personal_Pronouns}")

    Average_Word_Length = Anilizer.Find_Average_Word_Length(Word_count)
    print(f"Average_Word_Length: {Average_Word_Length}")

    Anilizer.AligValue(articles, positive_points, negative_points, Polarity_Score, Subjectivity_Score, Average_Sentence_Length, complex_words, Fog_Index, Average_Sentence_Word_per_sen, Complex_Word_Count, Word_count, Syllable_Count_Per_Word, Personal_Pronouns, Average_Word_Length)
    print(" ")

    Anilizer.Add_Value_file(articles)