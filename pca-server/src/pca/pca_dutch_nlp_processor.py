"""
Dutch NLP Processor for PCA
Integrates with the Dutch NLP API for sentiment analysis and entity extraction
"""

import json
import boto3
import requests
import os
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Process Dutch text using the Dutch NLP API
    """
    try:
        # Get configuration from environment variables
        dutch_nlp_endpoint = os.environ.get('DUTCH_NLP_API_ENDPOINT', '')
        enable_dutch_nlp = os.environ.get('ENABLE_DUTCH_NLP', 'false').lower() == 'true'
        
        if not enable_dutch_nlp:
            logger.info("Dutch NLP processing is disabled")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Dutch NLP processing is disabled',
                    'processed': False
                })
            }
        
        if not dutch_nlp_endpoint:
            logger.error("Dutch NLP API endpoint not configured")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Dutch NLP API endpoint not configured'
                })
            }
        
        # Extract text from the event
        text_to_process = event.get('text', '')
        if not text_to_process:
            logger.error("No text provided for processing")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No text provided for processing'
                })
            }
        
        # Process sentiment analysis
        sentiment_result = process_dutch_sentiment(dutch_nlp_endpoint, text_to_process)
        
        # Process entity extraction
        entities_result = process_dutch_entities(dutch_nlp_endpoint, text_to_process)
        
        # Process key phrase extraction
        keyphrases_result = process_dutch_keyphrases(dutch_nlp_endpoint, text_to_process)
        
        # Combine results
        result = {
            'sentiment': sentiment_result,
            'entities': entities_result,
            'keyphrases': keyphrases_result,
            'language': 'nl-NL',
            'processed_at': datetime.utcnow().isoformat(),
            'processed': True
        }
        
        logger.info(f"Successfully processed Dutch text with {len(entities_result.get('entities', []))} entities")
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Error processing Dutch NLP: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Error processing Dutch NLP: {str(e)}'
            })
        }

def process_dutch_sentiment(endpoint, text):
    """
    Process sentiment analysis using Dutch NLP API
    """
    try:
        response = requests.post(
            f"{endpoint}/sentiment",
            json={'text': text},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        response.raise_for_status()
        
        sentiment_data = response.json()
        
        # Convert to PCA format (similar to Comprehend format)
        return {
            'Sentiment': sentiment_data.get('sentiment', 'NEUTRAL').upper(),
            'SentimentScore': {
                'Positive': sentiment_data.get('scores', {}).get('positive', 0.0),
                'Negative': sentiment_data.get('scores', {}).get('negative', 0.0),
                'Neutral': sentiment_data.get('scores', {}).get('neutral', 0.0),
                'Mixed': sentiment_data.get('scores', {}).get('mixed', 0.0)
            }
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Dutch sentiment API: {str(e)}")
        # Return neutral sentiment as fallback
        return {
            'Sentiment': 'NEUTRAL',
            'SentimentScore': {
                'Positive': 0.0,
                'Negative': 0.0,
                'Neutral': 1.0,
                'Mixed': 0.0
            }
        }

def process_dutch_entities(endpoint, text):
    """
    Process entity extraction using Dutch NLP API
    """
    try:
        response = requests.post(
            f"{endpoint}/entities",
            json={'text': text},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        response.raise_for_status()
        
        entities_data = response.json()
        
        # Convert to PCA format (similar to Comprehend format)
        entities = []
        for entity in entities_data.get('entities', []):
            entities.append({
                'Text': entity.get('text', ''),
                'Type': entity.get('type', 'OTHER').upper(),
                'Score': entity.get('confidence', 0.0),
                'BeginOffset': entity.get('start', 0),
                'EndOffset': entity.get('end', 0)
            })
        
        return {
            'Entities': entities
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Dutch entities API: {str(e)}")
        return {
            'Entities': []
        }

def process_dutch_keyphrases(endpoint, text):
    """
    Process key phrase extraction using Dutch NLP API
    """
    try:
        response = requests.post(
            f"{endpoint}/keyphrases",
            json={'text': text},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        response.raise_for_status()
        
        keyphrases_data = response.json()
        
        # Convert to PCA format (similar to Comprehend format)
        keyphrases = []
        for phrase in keyphrases_data.get('keyphrases', []):
            keyphrases.append({
                'Text': phrase.get('text', ''),
                'Score': phrase.get('confidence', 0.0),
                'BeginOffset': phrase.get('start', 0),
                'EndOffset': phrase.get('end', 0)
            })
        
        return {
            'KeyPhrases': keyphrases
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Dutch keyphrases API: {str(e)}")
        return {
            'KeyPhrases': []
        }

def comprehensive_dutch_analysis(endpoint, text):
    """
    Perform comprehensive Dutch NLP analysis in a single call
    """
    try:
        response = requests.post(
            f"{endpoint}/comprehensive",
            json={'text': text},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Dutch comprehensive analysis API: {str(e)}")
        # Fallback to individual calls
        return {
            'sentiment': process_dutch_sentiment(endpoint, text),
            'entities': process_dutch_entities(endpoint, text),
            'keyphrases': process_dutch_keyphrases(endpoint, text)
        }
