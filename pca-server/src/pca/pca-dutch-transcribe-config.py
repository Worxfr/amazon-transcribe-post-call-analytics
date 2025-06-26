"""
Dutch Language Configuration for PCA Transcribe Jobs
Extends the existing transcribe job configuration to support Dutch language processing
"""

import os
import logging
import pcaconfiguration as cf

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def configure_dutch_language_support():
    """
    Configure Dutch language support for Transcribe jobs
    """
    try:
        # Get Dutch language configuration from environment
        default_transcribe_language = os.environ.get('DEFAULT_TRANSCRIBE_LANGUAGE', 'en-US')
        enable_dutch_nlp = os.environ.get('ENABLE_DUTCH_NLP', 'false').lower() == 'true'
        
        # If Dutch NLP is enabled and default language is Dutch, configure accordingly
        if enable_dutch_nlp and default_transcribe_language.startswith('nl'):
            logger.info(f"Configuring Dutch language support with language: {default_transcribe_language}")
            
            # Override the transcribe language configuration for Dutch
            if cf.CONF_TRANSCRIBE_LANG in cf.appConfig:
                current_langs = cf.appConfig[cf.CONF_TRANSCRIBE_LANG]
                if isinstance(current_langs, str):
                    current_langs = current_langs.split(" | ")
                
                # Add Dutch if not already present
                if default_transcribe_language not in current_langs:
                    current_langs.append(default_transcribe_language)
                    cf.appConfig[cf.CONF_TRANSCRIBE_LANG] = current_langs
                    logger.info(f"Added Dutch language {default_transcribe_language} to transcribe languages")
            else:
                # Set Dutch as the primary language
                cf.appConfig[cf.CONF_TRANSCRIBE_LANG] = [default_transcribe_language]
                logger.info(f"Set Dutch language {default_transcribe_language} as primary transcribe language")
        
        return True
        
    except Exception as e:
        logger.error(f"Error configuring Dutch language support: {str(e)}")
        return False

def get_dutch_custom_vocabulary_name(base_name="dutch-contact-center-vocabulary"):
    """
    Get the Dutch custom vocabulary name
    """
    return f"{base_name}-nl-nl"

def create_dutch_custom_vocabulary_if_needed(transcribe_client):
    """
    Create Dutch custom vocabulary if it doesn't exist
    """
    try:
        vocab_name = get_dutch_custom_vocabulary_name()
        
        # Check if vocabulary already exists
        try:
            vocab_response = transcribe_client.get_vocabulary(VocabularyName=vocab_name)
            if vocab_response['VocabularyState'] == 'READY':
                logger.info(f"Dutch custom vocabulary {vocab_name} already exists and is ready")
                return vocab_name
        except transcribe_client.exceptions.NotFoundException:
            # Vocabulary doesn't exist, we'll create it
            pass
        
        # Define Dutch contact center vocabulary
        dutch_vocabulary_phrases = [
            "klantenservice",
            "klantenondersteuning", 
            "verzekering",
            "hypotheek",
            "bankrekening",
            "rekeningnummer",
            "pincode",
            "DigiD",
            "BSN",
            "burgerservicenummer",
            "IBAN",
            "betaalrekening",
            "spaarrekening",
            "creditcard",
            "internetbankieren",
            "mobiel bankieren",
            "klantnummer",
            "polisnummer",
            "schade",
            "claim",
            "premie",
            "dekkingsgraad",
            "eigen risico",
            "verzekeringsmaatschappij",
            "hypotheekadviseur",
            "rentevast",
            "aflossingsvrij",
            "annuïteit",
            "overwaarde",
            "restschuld",
            "taxatiewaarde",
            "WOZ-waarde",
            "notaris",
            "hypotheekakte",
            "NHG",
            "nationale hypotheek garantie"
        ]
        
        # Create the vocabulary
        transcribe_client.create_vocabulary(
            VocabularyName=vocab_name,
            LanguageCode='nl-NL',
            Phrases=dutch_vocabulary_phrases
        )
        
        logger.info(f"Created Dutch custom vocabulary: {vocab_name}")
        return vocab_name
        
    except Exception as e:
        logger.error(f"Error creating Dutch custom vocabulary: {str(e)}")
        return None

def configure_dutch_transcribe_settings(job_settings, transcribe_client):
    """
    Configure Transcribe job settings for Dutch language processing
    """
    try:
        enable_dutch_nlp = os.environ.get('ENABLE_DUTCH_NLP', 'false').lower() == 'true'
        default_language = os.environ.get('DEFAULT_TRANSCRIBE_LANGUAGE', 'en-US')
        
        if enable_dutch_nlp and default_language.startswith('nl'):
            # Add Dutch custom vocabulary
            vocab_name = create_dutch_custom_vocabulary_if_needed(transcribe_client)
            if vocab_name:
                job_settings['Settings'] = job_settings.get('Settings', {})
                job_settings['Settings']['VocabularyName'] = vocab_name
                logger.info(f"Added Dutch custom vocabulary {vocab_name} to job settings")
            
            # Configure for Dutch language
            job_settings['LanguageCode'] = default_language
            job_settings['IdentifyLanguage'] = False
            
            # Remove language options if set (since we're using a specific language)
            if 'LanguageOptions' in job_settings:
                job_settings['LanguageOptions'] = [default_language]
            
            logger.info(f"Configured Transcribe job settings for Dutch language: {default_language}")
        
        return job_settings
        
    except Exception as e:
        logger.error(f"Error configuring Dutch Transcribe settings: {str(e)}")
        return job_settings

def is_dutch_language_configured():
    """
    Check if Dutch language is configured for processing
    """
    enable_dutch_nlp = os.environ.get('ENABLE_DUTCH_NLP', 'false').lower() == 'true'
    default_language = os.environ.get('DEFAULT_TRANSCRIBE_LANGUAGE', 'en-US')
    
    return enable_dutch_nlp and default_language.startswith('nl')

def get_configured_language():
    """
    Get the configured language for transcription
    """
    if is_dutch_language_configured():
        return os.environ.get('DEFAULT_TRANSCRIBE_LANGUAGE', 'nl-NL')
    else:
        # Return the first configured language or default to English
        if cf.CONF_TRANSCRIBE_LANG in cf.appConfig and cf.appConfig[cf.CONF_TRANSCRIBE_LANG]:
            return cf.appConfig[cf.CONF_TRANSCRIBE_LANG][0]
        return 'en-US'

def log_language_configuration():
    """
    Log the current language configuration for debugging
    """
    try:
        enable_dutch_nlp = os.environ.get('ENABLE_DUTCH_NLP', 'false')
        default_language = os.environ.get('DEFAULT_TRANSCRIBE_LANGUAGE', 'en-US')
        dutch_nlp_endpoint = os.environ.get('DUTCH_NLP_API_ENDPOINT', 'Not configured')
        
        logger.info("=== PCA Language Configuration ===")
        logger.info(f"Enable Dutch NLP: {enable_dutch_nlp}")
        logger.info(f"Default Transcribe Language: {default_language}")
        logger.info(f"Dutch NLP API Endpoint: {dutch_nlp_endpoint}")
        logger.info(f"Is Dutch Configured: {is_dutch_language_configured()}")
        
        if cf.CONF_TRANSCRIBE_LANG in cf.appConfig:
            logger.info(f"Configured Transcribe Languages: {cf.appConfig[cf.CONF_TRANSCRIBE_LANG]}")
        
        logger.info("=== End Language Configuration ===")
        
    except Exception as e:
        logger.error(f"Error logging language configuration: {str(e)}")
