# Amazon Transcribe Post Call Analytics - Nederlandse Versie

Deze implementatie breidt de Amazon Transcribe Post Call Analytics (PCA) oplossing uit met ondersteuning voor Nederlandse taal verwerking.

## Overzicht

De Nederlandse versie van PCA integreert met een aangepaste Dutch NLP API voor:
- Nederlandse sentiment analyse
- Nederlandse entiteit extractie  
- Nederlandse key phrase extractie
- Nederlandse gesprekssamenvattingen

## Architectuur Wijzigingen

### 1. Nederlandse NLP API Integratie
- **Dutch NLP Processor** (`pca-dutch-nlp-processor.py`): Lambda functie voor Nederlandse NLP verwerking
- **Dutch NLP Integration** (`pca-dutch-nlp-integration.py`): Integratie laag tussen PCA en Dutch NLP API
- **Dutch Transcribe Config** (`pca-dutch-transcribe-config.py`): Nederlandse taal configuratie voor Transcribe

### 2. Bedrock Nederlandse Samenvatting
- **Dutch Bedrock Summarization** (`pca-bedrock-dutch-summarization.py`): Nederlandse prompts en verwerking voor gesprekssamenvattingen

## Configuratie Parameters

### CloudFormation Parameters
```yaml
DutchNLPApiEndpoint:
  Type: String
  Description: Endpoint URL voor Dutch NLP API
  
EnableDutchNLP:
  Type: String
  Default: "false"
  AllowedValues: ["true", "false"]
  Description: Schakel Nederlandse NLP verwerking in

DefaultTranscribeLanguage:
  Type: String
  Default: "nl-NL"
  Description: Standaard taal voor Amazon Transcribe jobs
```

### Environment Variables
```bash
DUTCH_NLP_API_ENDPOINT=https://your-dutch-nlp-api.amazonaws.com
ENABLE_DUTCH_NLP=true
DEFAULT_TRANSCRIBE_LANGUAGE=nl-NL
```

## Nederlandse NLP API Integratie

### Verwachte API Endpoints
De Dutch NLP API moet de volgende endpoints ondersteunen:

#### Sentiment Analyse
```
POST /sentiment
Content-Type: application/json

{
  "text": "Nederlandse tekst voor analyse"
}

Response:
{
  "sentiment": "POSITIVE|NEGATIVE|NEUTRAL",
  "scores": {
    "positive": 0.8,
    "negative": 0.1,
    "neutral": 0.1,
    "mixed": 0.0
  }
}
```

#### Entiteit Extractie
```
POST /entities
Content-Type: application/json

{
  "text": "Nederlandse tekst voor analyse"
}

Response:
{
  "entities": [
    {
      "text": "Amsterdam",
      "type": "LOCATION",
      "confidence": 0.95,
      "start": 10,
      "end": 19
    }
  ]
}
```

#### Key Phrase Extractie
```
POST /keyphrases
Content-Type: application/json

{
  "text": "Nederlandse tekst voor analyse"
}

Response:
{
  "keyphrases": [
    {
      "text": "belangrijke zin",
      "confidence": 0.85,
      "start": 5,
      "end": 20
    }
  ]
}
```

#### Uitgebreide Analyse
```
POST /comprehensive
Content-Type: application/json

{
  "text": "Nederlandse tekst voor analyse"
}

Response:
{
  "sentiment": { /* sentiment response */ },
  "entities": { /* entities response */ },
  "keyphrases": { /* keyphrases response */ }
}
```

## Nederlandse Custom Vocabulary

De implementatie bevat een voorgedefinieerde Nederlandse woordenlijst voor contactcenters:

```python
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
    # ... meer Nederlandse termen
]
```

## Nederlandse Samenvatting Structuur

De Bedrock integratie gebruikt Nederlandse prompts voor gestructureerde samenvattingen:

```
SAMENVATTING: [Korte samenvatting]
HOOFDONDERWERP: [Primaire onderwerp]
KLANT SENTIMENT: [Positief/Negatief/Neutraal]
MEDEWERKER SENTIMENT: [Positief/Negatief/Neutraal]
BELANGRIJKSTE PUNTEN: [Lijst van punten]
ACTIEPUNTEN: [Vervolgacties]
OPLOSSING: [Ja/Nee/Gedeeltelijk]
KWALITEIT GESPREK: [Uitstekend/Goed/Voldoende/Onvoldoende]
```

## Deployment

### 1. Deploy de Dutch NLP API
Zorg ervoor dat de Dutch NLP API beschikbaar is en toegankelijk vanuit de PCA Lambda functies.

### 2. Update CloudFormation Parameters
```bash
aws cloudformation update-stack \
  --stack-name PostCallAnalytics \
  --use-previous-template \
  --parameters \
    ParameterKey=EnableDutchNLP,ParameterValue=true \
    ParameterKey=DutchNLPApiEndpoint,ParameterValue=https://your-dutch-nlp-api.com \
    ParameterKey=DefaultTranscribeLanguage,ParameterValue=nl-NL
```

### 3. Test met Nederlandse Audio
Upload Nederlandse audio bestanden naar de input bucket om de functionaliteit te testen.

## Monitoring en Troubleshooting

### CloudWatch Logs
Monitor de volgende log groepen:
- `/aws/lambda/pca-dutch-nlp-processor`
- `/aws/lambda/pca-aws-sf-process-turn-by-turn`

### Veelvoorkomende Problemen

1. **Dutch NLP API niet bereikbaar**
   - Controleer de endpoint URL
   - Verificeer netwerk connectiviteit
   - Check API authenticatie

2. **Nederlandse Custom Vocabulary niet gevonden**
   - Controleer of de vocabulary succesvol is aangemaakt
   - Verificeer de vocabulary status in Transcribe console

3. **Sentiment scores lijken incorrect**
   - Controleer de mapping tussen Dutch NLP API en Comprehend formaat
   - Verificeer de sentiment score scaling

## Uitbreidingen

### Ondersteuning voor Andere Nederlandse Dialecten
De implementatie kan worden uitgebreid voor:
- Vlaams (België)
- Surinaams Nederlands
- Nederlandse dialecten

### Aanvullende NLP Features
- Nederlandse named entity recognition
- Nederlandse topic modeling
- Nederlandse emotion detection

## Licentie

Deze Nederlandse uitbreiding volgt dezelfde Apache-2.0 licentie als het hoofdproject.

## Ondersteuning

Voor vragen over de Nederlandse implementatie, raadpleeg de documentatie of open een issue in de repository.
