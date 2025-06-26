"""
Dutch Language Summarization for PCA using Amazon Bedrock
Provides Dutch-specific prompts and processing for call summarization
"""

import json
import boto3
import logging
import os
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_dutch_summary_prompt(transcript, call_metadata=None):
    """
    Generate a Dutch-specific prompt for call summarization
    """
    base_prompt = f"""
Analyseer het volgende Nederlandse klantenservice gesprek en geef een gestructureerde samenvatting:

GESPREK TRANSCRIPT:
{transcript}

Geef een samenvatting in het Nederlands met de volgende structuur:

SAMENVATTING:
[Korte samenvatting van het gesprek in 2-3 zinnen]

HOOFDONDERWERP:
[Het primaire onderwerp of de reden voor het gesprek]

KLANT SENTIMENT:
[Positief/Negatief/Neutraal met korte uitleg]

MEDEWERKER SENTIMENT:
[Positief/Negatief/Neutraal met korte uitleg]

BELANGRIJKSTE PUNTEN:
- [Punt 1]
- [Punt 2]
- [Punt 3]

ACTIEPUNTEN:
[Eventuele vervolgacties of afspraken]

OPLOSSING:
[Of het probleem is opgelost: Ja/Nee/Gedeeltelijk]

KWALITEIT GESPREK:
[Beoordeling van de kwaliteit van de klantenservice: Uitstekend/Goed/Voldoende/Onvoldoende]
"""

    # Add metadata context if available
    if call_metadata:
        metadata_context = "\n\nCONTEXT INFORMATIE:\n"
        if 'duration' in call_metadata:
            metadata_context += f"- Gespreksduur: {call_metadata['duration']} seconden\n"
        if 'channel_count' in call_metadata:
            metadata_context += f"- Aantal kanalen: {call_metadata['channel_count']}\n"
        if 'date' in call_metadata:
            metadata_context += f"- Datum: {call_metadata['date']}\n"
        
        base_prompt = metadata_context + base_prompt

    return base_prompt

def get_dutch_comprehensive_analysis_prompt(transcript, call_metadata=None):
    """
    Generate a comprehensive Dutch analysis prompt
    """
    prompt = f"""
Voer een uitgebreide analyse uit van dit Nederlandse klantenservice gesprek:

GESPREK TRANSCRIPT:
{transcript}

Geef een gedetailleerde analyse in het Nederlands met:

1. GESPREKSANALYSE:
   - Duur en structuur van het gesprek
   - Communicatiestijl van beide partijen
   - Effectiviteit van de communicatie

2. SENTIMENT ANALYSE:
   - Klant sentiment per gespreksonderdeel
   - Medewerker sentiment en professionaliteit
   - Sentiment ontwikkeling tijdens het gesprek

3. ONDERWERP CLASSIFICATIE:
   - Primaire categorie (bijv. Verzekering, Banking, Hypotheek)
   - Secundaire onderwerpen
   - Complexiteit van de vraag

4. KLANTENSERVICE KWALITEIT:
   - Responstijd en efficiency
   - Empathie en begrip
   - Probleemoplossend vermogen
   - Professionaliteit

5. COMPLIANCE EN PROCEDURES:
   - Werden juiste procedures gevolgd?
   - Privacy en veiligheid aspecten
   - Documentatie en verificatie

6. VERBETERPUNTEN:
   - Wat ging goed?
   - Wat kan beter?
   - Specifieke aanbevelingen

7. RISICO INDICATOREN:
   - Klant tevredenheid risico
   - Escalatie potentieel
   - Compliance risico's

Geef concrete, actionable feedback voor kwaliteitsverbetering.
"""
    
    return prompt

def summarize_dutch_call_with_bedrock(transcript, model_id="anthropic.claude-3-sonnet-20240229-v1:0", call_metadata=None):
    """
    Summarize a Dutch call using Amazon Bedrock
    """
    try:
        bedrock_client = boto3.client('bedrock-runtime')
        
        # Get Dutch-specific prompt
        prompt = get_dutch_summary_prompt(transcript, call_metadata)
        
        # Prepare the request based on model type
        if "claude" in model_id.lower():
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.1,
                "anthropic_version": "bedrock-2023-05-31"
            }
        else:
            # Generic format for other models
            request_body = {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 2000,
                    "temperature": 0.1,
                    "topP": 0.9
                }
            }
        
        # Make the request to Bedrock
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body),
            contentType='application/json',
            accept='application/json'
        )
        
        # Parse the response
        response_body = json.loads(response['body'].read())
        
        if "claude" in model_id.lower():
            summary_text = response_body['content'][0]['text']
        else:
            summary_text = response_body.get('results', [{}])[0].get('outputText', '')
        
        # Parse the structured summary
        parsed_summary = parse_dutch_summary(summary_text)
        
        logger.info("Successfully generated Dutch call summary using Bedrock")
        return parsed_summary
        
    except Exception as e:
        logger.error(f"Error generating Dutch summary with Bedrock: {str(e)}")
        return generate_fallback_dutch_summary(transcript)

def parse_dutch_summary(summary_text):
    """
    Parse the structured Dutch summary into a dictionary
    """
    try:
        summary_dict = {
            "Samenvatting": "",
            "Hoofdonderwerp": "",
            "Klant_Sentiment": "",
            "Medewerker_Sentiment": "",
            "Belangrijkste_Punten": [],
            "Actiepunten": "",
            "Oplossing": "",
            "Kwaliteit_Gesprek": "",
            "Taal": "Nederlands",
            "Gegenereerd_Op": datetime.utcnow().isoformat()
        }
        
        # Split the summary into sections
        sections = summary_text.split('\n')
        current_section = None
        
        for line in sections:
            line = line.strip()
            if not line:
                continue
                
            # Identify section headers
            if line.startswith('SAMENVATTING:'):
                current_section = 'Samenvatting'
                summary_dict[current_section] = line.replace('SAMENVATTING:', '').strip()
            elif line.startswith('HOOFDONDERWERP:'):
                current_section = 'Hoofdonderwerp'
                summary_dict[current_section] = line.replace('HOOFDONDERWERP:', '').strip()
            elif line.startswith('KLANT SENTIMENT:'):
                current_section = 'Klant_Sentiment'
                summary_dict[current_section] = line.replace('KLANT SENTIMENT:', '').strip()
            elif line.startswith('MEDEWERKER SENTIMENT:'):
                current_section = 'Medewerker_Sentiment'
                summary_dict[current_section] = line.replace('MEDEWERKER SENTIMENT:', '').strip()
            elif line.startswith('BELANGRIJKSTE PUNTEN:'):
                current_section = 'Belangrijkste_Punten'
            elif line.startswith('ACTIEPUNTEN:'):
                current_section = 'Actiepunten'
                summary_dict[current_section] = line.replace('ACTIEPUNTEN:', '').strip()
            elif line.startswith('OPLOSSING:'):
                current_section = 'Oplossing'
                summary_dict[current_section] = line.replace('OPLOSSING:', '').strip()
            elif line.startswith('KWALITEIT GESPREK:'):
                current_section = 'Kwaliteit_Gesprek'
                summary_dict[current_section] = line.replace('KWALITEIT GESPREK:', '').strip()
            elif line.startswith('- ') and current_section == 'Belangrijkste_Punten':
                summary_dict['Belangrijkste_Punten'].append(line[2:])
            elif current_section and not line.startswith(('SAMENVATTING:', 'HOOFDONDERWERP:', 'KLANT SENTIMENT:', 'MEDEWERKER SENTIMENT:', 'BELANGRIJKSTE PUNTEN:', 'ACTIEPUNTEN:', 'OPLOSSING:', 'KWALITEIT GESPREK:')):
                # Continue previous section
                if current_section in ['Samenvatting', 'Hoofdonderwerp', 'Klant_Sentiment', 'Medewerker_Sentiment', 'Actiepunten', 'Oplossing', 'Kwaliteit_Gesprek']:
                    if summary_dict[current_section]:
                        summary_dict[current_section] += ' ' + line
                    else:
                        summary_dict[current_section] = line
        
        return summary_dict
        
    except Exception as e:
        logger.error(f"Error parsing Dutch summary: {str(e)}")
        return {
            "Samenvatting": summary_text,
            "Taal": "Nederlands",
            "Fout": f"Parsing error: {str(e)}",
            "Gegenereerd_Op": datetime.utcnow().isoformat()
        }

def generate_fallback_dutch_summary(transcript):
    """
    Generate a basic fallback summary when Bedrock is not available
    """
    word_count = len(transcript.split())
    
    return {
        "Samenvatting": "Automatische samenvatting niet beschikbaar. Handmatige review vereist.",
        "Hoofdonderwerp": "Niet bepaald",
        "Klant_Sentiment": "Neutraal",
        "Medewerker_Sentiment": "Neutraal", 
        "Belangrijkste_Punten": ["Transcript bevat " + str(word_count) + " woorden"],
        "Actiepunten": "Handmatige review vereist",
        "Oplossing": "Niet bepaald",
        "Kwaliteit_Gesprek": "Niet beoordeeld",
        "Taal": "Nederlands",
        "Status": "Fallback summary",
        "Gegenereerd_Op": datetime.utcnow().isoformat()
    }

def is_dutch_content(text):
    """
    Simple heuristic to detect if content is likely Dutch
    """
    dutch_indicators = [
        'de', 'het', 'een', 'van', 'en', 'in', 'op', 'met', 'voor', 'aan',
        'klantenservice', 'verzekering', 'hypotheek', 'bankrekening',
        'dank je wel', 'dank u wel', 'goedemorgen', 'goedemiddag'
    ]
    
    text_lower = text.lower()
    dutch_word_count = sum(1 for word in dutch_indicators if word in text_lower)
    
    # If more than 3 Dutch indicators found, likely Dutch content
    return dutch_word_count >= 3
