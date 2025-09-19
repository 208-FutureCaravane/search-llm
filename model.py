"""
Multilingual embedding model using LangChain for Arabic, French, English, and Darija support.
"""

import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from typing import Tuple, Dict
import re

class MultilingualEmbeddingModel:
    def __init__(self):
        """Initialize the multilingual embedding model."""
        # Use a multilingual sentence transformer model that supports Arabic via LangChain
        # Using a smaller, more efficient model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Response messages for different languages
        self.response_messages = {
            'en': "Here are the best dishes that matched your request: ",
            'fr': "Voici les meilleurs plats qui correspondent à votre demande : ",
            'ar': "إليك أفضل الأطباق التي تطابق طلبك: ",
            'da': "Hadi ahsan al tabaq li kaywafeq talab dyalek: ",  # Darija approximation
            'es': "Aquí están los mejores platos que coinciden con tu solicitud: ",  # Spanish fallback
            'default': "Here are the best dishes that matched your request: "
        }
    
    def _detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            str: Language code (en, fr, ar, etc.)
        """
        try:
            # Clean text for better detection
            cleaned_text = re.sub(r'[^\w\s]', '', text)
            detected_lang = detect(cleaned_text)
            
            # Handle Darija (Moroccan Arabic) - it's often detected as Arabic
            # Look for common Darija words/patterns
            darija_indicators = [
                'dyali', 'dyal', 'kayji', 'kayn', 'machi', 'bach', 'ghi', 
                'bzaf', 'shwiya', 'bghit', 'fin', 'fuq', 'taht', 'hna'
            ]
            
            if any(word in text.lower() for word in darija_indicators):
                return 'da'  # Darija
            
            return detected_lang
            
        except (LangDetectException, Exception):
            # If detection fails, try to identify by script
            if any('\u0600' <= char <= '\u06FF' for char in text):
                return 'ar'  # Arabic script
            return 'en'  # Default to English
    
    def _get_response_message(self, language_code: str) -> str:
        """
        Get the appropriate response message based on detected language.
        
        Args:
            language_code (str): Detected language code
            
        Returns:
            str: Localized response message
        """
        return self.response_messages.get(language_code, self.response_messages['default'])
    
    def embed_multilingual_query(self, query: str) -> Tuple[np.ndarray, str]:
        """
        Embed a multilingual query and return the vector with localized response message.
        
        Args:
            query (str): Multilingual query string (Arabic, French, English, or Darija)
            
        Returns:
            Tuple[np.ndarray, str]: A tuple containing:
                - embedding vector as numpy array
                - localized response message in the detected language
        """
        # Detect the language of the input
        detected_language = self._detect_language(query)
        
        # Generate embedding using LangChain HuggingFace embeddings
        embedding_vector = self.embeddings.embed_query(query)
        
        # Convert to numpy array for consistency
        embedding_array = np.array(embedding_vector)
        
        # Get the appropriate response message
        response_message = self._get_response_message(detected_language)
        
        return embedding_array, response_message
    
    def embed_documents(self, documents: list) -> np.ndarray:
        """
        Embed multiple documents.
        
        Args:
            documents (list): List of document strings to embed
            
        Returns:
            np.ndarray: Array of embedding vectors
        """
        embeddings_list = self.embeddings.embed_documents(documents)
        return np.array(embeddings_list)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get information about supported languages.
        
        Returns:
            Dict[str, str]: Dictionary mapping language codes to language names
        """
        return {
            'en': 'English',
            'fr': 'French (Français)',
            'ar': 'Arabic (العربية)',
            'da': 'Darija (الدارجة المغربية)',
            'es': 'Spanish (Español) - Fallback'
        }


# Example usage function
def demo_multilingual_embedding():
    """Demonstrate the multilingual embedding functionality."""
    model = MultilingualEmbeddingModel()
    
    # Test queries in different languages
    test_queries = [
        "I want spicy chicken dishes",  # English
        "Je veux des plats de poulet épicés",  # French
        "أريد أطباق دجاج حارة",  # Arabic
        "bghit tabaq dyal djaj har",  # Darija
    ]
    
    print("Multilingual Embedding Demo:")
    print("=" * 50)
    
    for query in test_queries:
        embedding, response_msg = model.embed_multilingual_query(query)
        print(f"\nQuery: {query}")
        print(f"Response: {response_msg}")
        print(f"Embedding shape: {embedding.shape}")
        print(f"First 5 values: {embedding[:5]}")
        print("-" * 30)

if __name__ == "__main__":
    demo_multilingual_embedding()
