"""
Dutch NLP Integration for PCA
Extends the existing turn-by-turn processor to support Dutch language processing
using the Dutch NLP API instead of Amazon Comprehend for Dutch content.
"""

import json
import boto3
import urllib3
import os
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class DutchNLPProcessor:
    """
    Handles Dutch NLP processing using the Dutch NLP API
    """
    
    def __init__(self):
        self.dutch_nlp_endpoint = os.environ.get('DUTCH_NLP_API_ENDPOINT', '')
        self.enable_dutch_nlp = os.environ.get('ENABLE_DUTCH_NLP', 'false').lower() == 'true'
        self.timeout = 30
        self.http = urllib3.PoolManager()
        
    def is_dutch_language(self, language_code):
        """
        Check if the language code indicates Dutch
        """
        return language_code and language_code.lower().startswith('nl')
    
    def should_use_dutch_nlp(self, language_code):
        """
        Determine if we should use Dutch NLP API for processing
        """
        return (self.enable_dutch_nlp and 
                self.dutch_nlp_endpoint and 
                self.is_dutch_language(language_code))
    
    def process_dutch_sentiment(self, text):
        """
        Process sentiment analysis using Dutch NLP API
        Returns format compatible with Comprehend sentiment response
        """
        try:
            if not text or len(text.strip()) < 3:
                return self._get_neutral_sentiment()
                
            response = self.http.request(
                'POST',
                f"{self.dutch_nlp_endpoint}/sentiment",
                body=json.dumps({'text': text}),
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            
            if response.status != 200:
                logger.error(f"Dutch NLP API returned status {response.status}")
                return self._get_neutral_sentiment()
            
            sentiment_data = json.loads(response.data.decode('utf-8'))
            
            # Convert to Comprehend-compatible format with PCA scaling
            confidence_scores = sentiment_data.get('confidence_scores', {})
            
            # Scale the scores by 5.0 to match PCA's expected range (same as COMPREHEND_SENTIMENT_SCALER)
            SENTIMENT_SCALER = 5.0
            
            return {
                'Sentiment': sentiment_data.get('sentiment', 'NEUTRAL').upper(),
                'SentimentScore': {
                    'Positive': float(confidence_scores.get('positive', 0.0)) * SENTIMENT_SCALER,
                    'Negative': float(confidence_scores.get('negative', 0.0)) * SENTIMENT_SCALER,
                    'Neutral': float(confidence_scores.get('neutral', 1.0)) * SENTIMENT_SCALER
                }
            }
            
        except Exception as e:
            logger.error(f"Error in Dutch sentiment analysis: {str(e)}")
            return self._get_neutral_sentiment()
    
    def process_dutch_entities(self, text):
        """
        Process entity extraction using Dutch NLP API
        Returns format compatible with Comprehend entity response
        """
        try:
            if not text or len(text.strip()) < 3:
                return {'Entities': []}
                
            response = self.http.request(
                'POST',
                f"{self.dutch_nlp_endpoint}/entities",
                body=json.dumps({'text': text}),
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            
            if response.status != 200:
                logger.error(f"Dutch NLP API entities returned status {response.status}")
                return {'Entities': []}
            
            entities_data = json.loads(response.data.decode('utf-8'))
            
            # Convert to Comprehend-compatible format
            entities = []
            for entity in entities_data.get('entities', []):
                entities.append({
                    'Text': entity.get('text', ''),
                    'Type': self._map_entity_type(entity.get('type', 'OTHER')),
                    'Score': float(entity.get('confidence', 0.0)),
                    'BeginOffset': int(entity.get('start', 0)),
                    'EndOffset': int(entity.get('end', 0))
                })
            
            return {'Entities': entities}
            
        except Exception as e:
            logger.error(f"Error in Dutch entity extraction: {str(e)}")
            return {'Entities': []}
    
    def process_dutch_keyphrases(self, text):
        """
        Process key phrase extraction using Dutch NLP API
        Returns format compatible with Comprehend key phrases response
        """
        try:
            if not text or len(text.strip()) < 3:
                return {'KeyPhrases': []}
                
            response = requests.post(
                f"{self.dutch_nlp_endpoint}/key-phrases",
                json={'text': text},
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            keyphrases_data = response.json()
            
            # Convert to Comprehend-compatible format
            keyphrases = []
            for phrase in keyphrases_data.get('keyphrases', []):
                keyphrases.append({
                    'Text': phrase.get('text', ''),
                    'Score': float(phrase.get('confidence', 0.0)),
                    'BeginOffset': int(phrase.get('start', 0)),
                    'EndOffset': int(phrase.get('end', 0))
                })
            
            return {'KeyPhrases': keyphrases}
            
        except Exception as e:
            logger.error(f"Error in Dutch key phrase extraction: {str(e)}")
            return {'KeyPhrases': []}
    
    def comprehensive_dutch_analysis(self, text):
        """
        Perform comprehensive Dutch NLP analysis
        """
        try:
            if not text or len(text.strip()) < 3:
                return {
                    'sentiment': self._get_neutral_sentiment(),
                    'entities': {'Entities': []},
                    'keyphrases': {'KeyPhrases': []}
                }
                
            response = requests.post(
                f"{self.dutch_nlp_endpoint}/analyze",
                json={'text': text},
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            comprehensive_data = response.json()
            
            # Convert all responses to Comprehend-compatible format
            result = {
                'sentiment': self._convert_sentiment_response(comprehensive_data.get('sentiment', {})),
                'entities': self._convert_entities_response(comprehensive_data.get('entities', {})),
                'keyphrases': self._convert_keyphrases_response(comprehensive_data.get('keyphrases', {}))
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in comprehensive Dutch analysis: {str(e)}")
            # Fallback to individual calls
            return {
                'sentiment': self.process_dutch_sentiment(text),
                'entities': self.process_dutch_entities(text),
                'keyphrases': self.process_dutch_keyphrases(text)
            }
    
    def _get_neutral_sentiment(self):
        """
        Return neutral sentiment response with PCA scaling
        """
        SENTIMENT_SCALER = 5.0
        return {
            'Sentiment': 'NEUTRAL',
            'SentimentScore': {
                'Positive': 0.0,
                'Negative': 0.0,
                'Neutral': 1.0 * SENTIMENT_SCALER
            }
        }
    
    def _map_entity_type(self, dutch_entity_type):
        """
        Map Dutch entity types to Comprehend entity types
        """
        entity_mapping = {
            'PERSON': 'PERSON',
            'PERSOON': 'PERSON',
            'LOCATION': 'LOCATION',
            'LOCATIE': 'LOCATION',
            'PLAATS': 'LOCATION',
            'ORGANIZATION': 'ORGANIZATION',
            'ORGANISATIE': 'ORGANIZATION',
            'BEDRIJF': 'ORGANIZATION',
            'DATE': 'DATE',
            'DATUM': 'DATE',
            'TIME': 'DATE',
            'TIJD': 'DATE',
            'MONEY': 'QUANTITY',
            'GELD': 'QUANTITY',
            'BEDRAG': 'QUANTITY',
            'NUMBER': 'QUANTITY',
            'NUMMER': 'QUANTITY',
            'GETAL': 'QUANTITY',
            'EMAIL': 'OTHER',
            'PHONE': 'OTHER',
            'TELEFOON': 'OTHER'
        }
        
        return entity_mapping.get(dutch_entity_type.upper(), 'OTHER')
    
    def _convert_sentiment_response(self, sentiment_data):
        """
        Convert Dutch NLP sentiment response to Comprehend format
        """
        if not sentiment_data:
            return self._get_neutral_sentiment()
            
        sentiment_scores = sentiment_data.get('scores', {})
        return {
            'Sentiment': sentiment_data.get('sentiment', 'NEUTRAL').upper(),
            'SentimentScore': {
                'Positive': float(sentiment_scores.get('positive', 0.0)),
                'Negative': float(sentiment_scores.get('negative', 0.0)),
                'Neutral': float(sentiment_scores.get('neutral', 1.0))
            }
        }
    
    def _convert_entities_response(self, entities_data):
        """
        Convert Dutch NLP entities response to Comprehend format
        """
        if not entities_data:
            return {'Entities': []}
            
        entities = []
        for entity in entities_data.get('entities', []):
            entities.append({
                'Text': entity.get('text', ''),
                'Type': self._map_entity_type(entity.get('type', 'OTHER')),
                'Score': float(entity.get('confidence', 0.0)),
                'BeginOffset': int(entity.get('start', 0)),
                'EndOffset': int(entity.get('end', 0))
            })
        
        return {'Entities': entities}
    
    def _convert_keyphrases_response(self, keyphrases_data):
        """
        Convert Dutch NLP keyphrases response to Comprehend format
        """
        if not keyphrases_data:
            return {'KeyPhrases': []}
            
        keyphrases = []
        for phrase in keyphrases_data.get('keyphrases', []):
            keyphrases.append({
                'Text': phrase.get('text', ''),
                'Score': float(phrase.get('confidence', 0.0)),
                'BeginOffset': int(phrase.get('start', 0)),
                'EndOffset': int(phrase.get('end', 0))
            })
        
        return {'KeyPhrases': keyphrases}


def get_nlp_processor_for_language(language_code):
    """
    Factory function to get the appropriate NLP processor based on language
    """
    dutch_processor = DutchNLPProcessor()
    
    if dutch_processor.should_use_dutch_nlp(language_code):
        logger.info(f"Using Dutch NLP API for language: {language_code}")
        return dutch_processor
    else:
        logger.info(f"Using standard Comprehend for language: {language_code}")
        return None


def process_sentiment_with_language_support(text, language_code, comprehend_client=None):
    """
    Process sentiment with language-specific support
    """
    dutch_processor = get_nlp_processor_for_language(language_code)
    
    if dutch_processor:
        return dutch_processor.process_dutch_sentiment(text)
    else:
        # Fall back to standard Comprehend processing
        if comprehend_client and language_code:
            try:
                response = comprehend_client.detect_sentiment(Text=text, LanguageCode=language_code)
                response["SentimentScore"].pop("Mixed", None)
                # Scale the sentiment scores (matching existing PCA behavior)
                for sentiment_key in response["SentimentScore"]:
                    response["SentimentScore"][sentiment_key] *= 5.0
                return response
            except Exception as e:
                logger.error(f"Error in Comprehend sentiment analysis: {str(e)}")
        
        # Return neutral sentiment as fallback
        return {
            'Sentiment': 'NEUTRAL',
            'SentimentScore': {
                'Positive': 0.0,
                'Negative': 0.0,
                'Neutral': 1.0
            }
        }


def process_entities_with_language_support(text, language_code, comprehend_client=None):
    """
    Process entities with language-specific support
    """
    dutch_processor = get_nlp_processor_for_language(language_code)
    
    if dutch_processor:
        return dutch_processor.process_dutch_entities(text)
    else:
        # Fall back to standard Comprehend processing
        if comprehend_client and language_code:
            try:
                return comprehend_client.detect_entities(Text=text, LanguageCode=language_code)
            except Exception as e:
                logger.error(f"Error in Comprehend entity detection: {str(e)}")
        
        # Return empty entities as fallback
        return {'Entities': []}
