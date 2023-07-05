from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from gingerit.gingerit import GingerIt

def process(extracted_text):
    parser = PlaintextParser.from_string(extracted_text, Tokenizer("english"))


    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 10)  


    summary_text = " ".join(str(sentence) for sentence in summary)


    ginger_parser = GingerIt()
    try:
        corrected_summary = ginger_parser.parse(summary_text)
        result = corrected_summary['result']
    except KeyError:
        result = summary_text
    return result
