from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Levenshtein import distance as levenshtein_distance
from datasketch import MinHash
from sentence_transformers import CrossEncoder
import numpy as np
from difflib import SequenceMatcher

class TextAnalyzer:
    def __init__(self):
        self.cross_encoder = CrossEncoder('cross-encoder/stsb-roberta-large')
    
    def compare(self, text1, text2):
        clean1, clean2 = self._preprocess(text1), self._preprocess(text2)
        
        metrics = {
            'jaccard': float(self._jaccard_similarity(clean1, clean2)),
            'cosine': float(self._cosine_similarity(clean1, clean2)),
            'levenshtein': float(self._levenshtein_similarity(text1, text2)),
            'minhash': float(self._minhash_similarity(clean1, clean2)),
            'semantic': float(self._semantic_similarity(text1, text2)),
            'longest_match': float(self._longest_common_substring(text1, text2))
        }
        
        return {
            'details': metrics,
            'score': float(self._calculate_score(metrics)),
            'heatmap': [[float(val) for val in row] for row in self._generate_heatmap(clean1, clean2)],
            'matches': self._find_matches(text1, text2)
        }
    
    def _preprocess(self, text):
        return text.lower().strip()
    
    def _jaccard_similarity(self, text1, text2):
        a, b = set(text1.split()), set(text2.split())
        return len(a & b) / len(a | b) if (a | b) else 0
    
    def _cosine_similarity(self, text1, text2):
        vectorizer = TfidfVectorizer(ngram_range=(1, 3), token_pattern=r"(?u)\\b\\w+\\b|[A-Za-z_][A-Za-z0-9_]*|\\S")
        try:
            tfidf = vectorizer.fit_transform([text1, text2])
            return cosine_similarity(tfidf[0], tfidf[1])[0][0]
        except ValueError:
            return 0.0
    
    def _levenshtein_similarity(self, text1, text2):
        max_len = max(len(text1), len(text2))
        return 1 - (levenshtein_distance(text1, text2) / max_len) if max_len else 0
    
    def _minhash_similarity(self, text1, text2):
        m1, m2 = MinHash(num_perm=128), MinHash(num_perm=128)
        for word in text1.split(): m1.update(word.encode('utf8'))
        for word in text2.split(): m2.update(word.encode('utf8'))
        return m1.jaccard(m2)
    
    def _semantic_similarity(self, text1, text2):
        return self.cross_encoder.predict([(text1, text2)])[0]
    
    def _longest_common_substring(self, text1, text2):
        match = SequenceMatcher(None, text1, text2).find_longest_match()
        return match.size / max(len(text1), len(text2))
    
    def _calculate_score(self, metrics):
        weights = {
            'jaccard': 0.2,
            'cosine': 0.3,
            'levenshtein': 0.15,
            'minhash': 0.15,
            'semantic': 0.15,
            'longest_match': 0.05
        }
        return sum(metrics[k] * weights[k] for k in weights)
    
    def _generate_heatmap(self, text1, text2, window_size=30):
        windows1 = [text1[i:i+window_size] for i in range(0, len(text1), window_size//2)]
        windows2 = [text2[i:i+window_size] for i in range(0, len(text2), window_size//2)]
        
        return [
            [self._cosine_similarity(w1, w2) for w2 in windows2[:20]] 
            for w1 in windows1[:20]
        ]
    
    def _find_matches(self, text1, text2, threshold=0.7):
        matches = []
        len1, len2 = len(text1), len(text2)
        
        for i in range(0, len1, 50):
            for j in range(0, len2, 50):
                section1 = text1[i:i+100]
                section2 = text2[j:j+100]
                similarity = self._cosine_similarity(section1, section2)
                if similarity > threshold:
                    matches.append({
                        'text1_start': i,
                        'text1_end': i+100,
                        'text2_start': j,
                        'text2_end': j+100,
                        'similarity': similarity
                    })
        return matches