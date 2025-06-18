import nltk
nltk.data.path.append('./nltk_data')  # This makes it use your local folder

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
import string
import re

class NLPPipeline:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
    def preprocess_text(self, text, language='english'):
        """
        Clean and preprocess text for analysis
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        processed_tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words and token.isalpha()
        ]
        
        return ' '.join(processed_tokens)
    
    def extract_key_phrases(self, text, num_phrases=5):
        """
        Extract important key phrases using TF-IDF
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        sentences = sent_tokenize(text)
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        X = vectorizer.fit_transform(sentences)
        
        # Get top phrases
        feature_array = vectorizer.get_feature_names_out()
        tfidf_sorting = X.sum(axis=0).A1.argsort()[::-1]
        
        return [feature_array[i] for i in tfidf_sorting[:num_phrases]]
    
    def calculate_readability(self, text):
        """
        Calculate Flesch Reading Ease score
        """
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        num_sentences = len(sentences)
        num_words = len(words)
        num_syllables = sum(self._count_syllables(word) for word in words)
        
        if num_sentences == 0 or num_words == 0:
            return 0
            
        return 206.835 - 1.015 * (num_words / num_sentences) - 84.6 * (num_syllables / num_words)
    
    def _count_syllables(self, word):
        """
        Approximate syllable count for a word
        """
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        
        if word[0] in vowels:
            count += 1
            
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
                
        if word.endswith('e'):
            count -= 1
        if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
            count += 1
            
        return max(1, count)
    
    def detect_language(self, text):
        """
        Simple language detection based on common words
        """
        common_words = {
            'english': ['the', 'be', 'to', 'of', 'and'],
            'french': ['le', 'la', 'de', 'et', 'à'],
            'spanish': ['el', 'la', 'de', 'y', 'en']
        }
        
        text_lower = text.lower()
        scores = {}
        
        for lang, words in common_words.items():
            scores[lang] = sum(word in text_lower for word in words)
            
        return max(scores.items(), key=lambda x: x[1])[0] if scores else 'unknown'