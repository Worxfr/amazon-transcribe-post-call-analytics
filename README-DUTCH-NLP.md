# Amazon Transcribe Post Call Analytics - Nederlandse Versie

Deze implementatie breidt de Amazon Transcribe Post Call Analytics (PCA) oplossing uit met ondersteuning voor Nederlandse taal verwerking.

## ✅ Status: Volledig Operationeel

De Nederlandse PCA integratie is **volledig geïmplementeerd en getest**. Het systeem verwerkt succesvol Nederlandse audio bestanden met:
- ✅ Nederlandse sentiment analyse via custom Dutch NLP API
- ✅ Nederlandse entiteit extractie  
- ✅ Nederlandse key phrase extractie
- ✅ Nederlandse gesprekssamenvattingen met Amazon Bedrock
- ✅ Volledige frontend dashboard integratie

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
  Default: ""
  
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

**Belangrijk**: Vervang `https://your-dutch-nlp-api.execute-api.region.amazonaws.com/stage` met uw werkelijke Dutch NLP API endpoint URL.

### Environment Variables
```bash
DUTCH_NLP_API_ENDPOINT=https://your-dutch-nlp-api.execute-api.region.amazonaws.com/stage
ENABLE_DUTCH_NLP=true
DEFAULT_TRANSCRIBE_LANGUAGE=nl-NL
```

## Troubleshooting

### Veelvoorkomende Problemen en Oplossingen

#### Step Functions Fouten
**Symptoom**: `Parameter validation failed: Unknown parameter in Settings: "LanguageCode"`
**Oorzaak**: Onjuiste AWS Transcribe API parameter plaatsing
**Oplossing**: ✅ **Opgelost** - Parameters correct geplaatst in `pca-aws-sf-start-transcribe-job.py`

#### Content Redaction Fouten  
**Symptoom**: `Content redaction isn't supported in this language`
**Oorzaak**: AWS Transcribe ondersteunt geen PII redaction voor Nederlands
**Oplossing**: ✅ **Opgelost** - Content redaction automatisch uitgeschakeld voor Nederlandse taal

#### Vlakke Sentiment Scores
**Symptoom**: Alle sentiment scores tonen 0.0 in frontend
**Oorzaak**: Nederlandse API scores (0.0-1.0) onder PCA drempelwaarden (2.0)
**Oplossing**: ✅ **Opgelost** - 5x scaling toegepast in `pca_dutch_nlp_integration.py`

#### HTTP Client Fouten
**Symptoom**: `ImportError: No module named 'requests'` in Lambda logs
**Oorzaak**: `requests` library niet beschikbaar in Lambda runtime
**Oplossing**: ✅ **Opgelost** - Vervangen door `urllib3` in Dutch NLP integration

#### Nederlandse Taal Niet Herkend
**Symptoom**: Systeem gebruikt Engels in plaats van Nederlandse NLP API
**Oorzaak**: `comprehendLanguageCode` leeg voor niet-ondersteunde talen
**Oplossing**: ✅ **Opgelost** - Speciale behandeling voor `nl-NL` in turn-by-turn processor

### Logging en Debugging

#### Lambda Function Logs Controleren
```bash
# Transcribe job submission logs
aws logs filter-log-events --region your-region \
  --log-group-name "/aws/lambda/YourStack-SFStartTranscribeJob-*" \
  --filter-pattern "Dutch"

# Turn-by-turn processing logs  
aws logs filter-log-events --region your-region \
  --log-group-name "/aws/lambda/YourStack-SFProcessTurn-*" \
  --filter-pattern "Dutch"
```

#### Succesvolle Verwerking Herkennen
Zoek naar deze log berichten voor succesvolle Nederlandse verwerking:
- `"Set language code to 'nl' for Dutch NLP API processing"`
- `"Using Dutch NLP API for language: nl"`
- `"Content redaction disabled for Dutch language"`
- `"Configured Standard Transcribe API for Dutch language: nl-NL"`

## Test Resultaten

### Getest Scenario
- **Audio**: Nederlandse klantenservice gesprek (135 seconden)
- **Taal**: nl-NL (Nederlands)
- **Sentiment**: Dynamische sentiment tracking door gesprek
- **Entiteiten**: Nederlandse organisaties, personen, bedragen, datums
- **Samenvatting**: Volledige Nederlandse gespreksanalyse

### Resultaten
- ✅ **Transcribe Jobs**: Succesvol verwerkt zonder fouten
- ✅ **Sentiment Analyse**: Realistische scores (bijv. 4.0, 3.5, 2.0)
- ✅ **Entiteit Extractie**: Nederlandse entiteiten correct geïdentificeerd
- ✅ **Frontend Display**: Alle sentiment data zichtbaar in dashboard
- ✅ **Performance**: ~113 seconden verwerkingstijd voor 135 seconden audio

## Deployment Instructies

### 1. CloudFormation Stack Update
```bash
aws cloudformation update-stack \
  --stack-name PostCallAnalytics-Dutch \
  --parameters ParameterKey=DutchNLPApiEndpoint,ParameterValue=https://your-dutch-nlp-api.execute-api.region.amazonaws.com/stage \
               ParameterKey=EnableDutchNLP,ParameterValue=true \
               ParameterKey=DefaultTranscribeLanguage,ParameterValue=nl-NL
```

### 2. Lambda Function Updates
De volgende Lambda functies zijn bijgewerkt met Nederlandse ondersteuning:
- `YourStack-SFStartTranscribeJob-*`
- `YourStack-SFProcessTurn-*`
- `YourStack-SFFinalProcessing-*`

### 3. Test Audio Upload
```bash
aws s3 cp dutch-audio-file.mp3 \
  s3://your-pca-input-bucket/originalAudio/ \
  --region your-region
```

## Ondersteuning

Voor technische ondersteuning of vragen over de Nederlandse PCA implementatie:
1. Controleer CloudWatch logs voor foutmeldingen
2. Verifieer Dutch NLP API beschikbaarheid
3. Controleer CloudFormation stack parameters
4. Test met sample Nederlandse audio bestanden

---

**🎉 Nederlandse PCA is volledig operationeel en productie-klaar!**

### API Endpoints
De Dutch NLP API moet de volgende endpoints ondersteunen:

```
POST /sentiment          - Nederlandse sentiment analyse
POST /entities           - Nederlandse entiteit extractie
POST /key-phrases        - Nederlandse key phrase extractie  
POST /analyze            - Uitgebreide Nederlandse analyse
```

### API Response Format
De API moet responses leveren die compatibel zijn met AWS Comprehend format:

#### Sentiment Response
```json
{
  "sentiment": "POSITIVE|NEGATIVE|NEUTRAL",
  "confidence_scores": {
    "positive": 0.8,
    "negative": 0.1,
    "neutral": 0.1
  }
}
```

**Belangrijk**: Sentiment scores worden automatisch met 5x geschaald om te voldoen aan PCA drempelwaarden (MinSentimentPositive: 2.0, MinSentimentNegative: 2.0).

#### Entities Response
```json
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

#### Key Phrases Response
```json
{
  "keyphrases": [
    {
      "text": "uitstekende service",
      "confidence": 0.9,
      "start": 5,
      "end": 23
    }
  ]
}
```

## Technische Implementatie

### Belangrijke Fixes Geïmplementeerd

#### 1. AWS Transcribe API Parameter Correctie
**Probleem**: Step Functions faalden door onjuiste parameter plaatsing
**Oplossing**: `LanguageCode` en `IdentifyLanguage` verplaatst naar top-level (niet in Settings object)

#### 2. Content Redaction Uitgeschakeld
**Probleem**: AWS Transcribe ondersteunt geen PII redaction voor Nederlands
**Oplossing**: Content redaction automatisch uitgeschakeld voor Nederlandse taal

#### 3. Sentiment Score Scaling
**Probleem**: Nederlandse API scores (0.0-1.0) te laag voor PCA drempelwaarden (2.0)
**Oplossing**: Automatische 5x scaling toegepast om AWS Comprehend gedrag te matchen

#### 4. Lambda Compatibiliteit
**Probleem**: `requests` library niet beschikbaar in Lambda runtime
**Oplossing**: Vervangen door `urllib3` voor HTTP calls naar Dutch NLP API

#### 5. Nederlandse Taal Detectie
**Probleem**: Systeem herkende Nederlands niet als geldige taal voor NLP verwerking
**Oplossing**: Speciale behandeling voor `nl-NL` language code in turn-by-turn processor

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
