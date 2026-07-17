from functools import lru_cache

from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from hfst_altlab import TransducerFile, FullAnalysis
import Levenshtein
from rest_framework import serializers, generics
from rest_framework.decorators import api_view

transducer_cutoff = 2

analyser_desc_fst = TransducerFile(filename=settings.ANALYSER_DESC_FST, search_cutoff=transducer_cutoff)
analyser_norm_fst = TransducerFile(filename=settings.ANALYSER_NORM_FST, search_cutoff=transducer_cutoff)
generator_norm_fst = TransducerFile(filename=settings.GENERATOR_NORM_FST, search_cutoff=transducer_cutoff)

class APIAnalysis:
    lemma:str
    prefixes: list[str]
    suffixes: list[str]
    standardized: str
    source: str
    levenshtein_distance: float

    def __init__(self, analysis: FullAnalysis, source:str, original_search:str):
        self.lemma=analysis.lemma
        self.prefixes=analysis.prefixes
        self.suffixes=analysis.suffixes

        self.source=source

        standardization = generator_norm_fst.weighted_lookup_full_wordform(analysis)
        if standardization:
            (self.standardized, self.levenshtein_distance) = min(
                ((w.wordform, Levenshtein.distance(original_search, w.wordform if w.wordform else "")) for w in standardization)
                ,key= lambda x: x[1]
            )
        else:
            self.standardized = ""
            self.levenshtein_distance = 0.0
        self.weight = analysis.weight

@lru_cache(maxsize=10240)
def cached_analyse(wordform):
    normative_results = analyser_norm_fst.weighted_lookup_full_analysis(wordform)
    if normative_results:
        return [APIAnalysis(analysis, settings.ANALYSER_NORM_FST, wordform) for analysis in normative_results]
    return [
        APIAnalysis(analysis, settings.ANALYSER_DESC_FST, wordform)
        for analysis in
        analyser_desc_fst.weighted_lookup_full_analysis(wordform)
    ]

class StandardizedField(serializers.StringRelatedField):
    class Meta:
        swagger_schema_fields = {
            "type": openapi.TYPE_STRING,
            "title": "Standardized Wordform",
            "description": """
                A wordform obtained from taking the analysis in this entry and giving it to the normative analyser.

                To deal with the cases when the normative analyser produces more than one output for the analysis,
                we compute the Levenshtein edit distance to all the results and give the one that is the closest one
                to the input wordform parameter.
            """
        }

class LevenshteinDistanceField(serializers.FloatField):
    class Meta:
        swagger_schema_fields = {
            "type": openapi.TYPE_NUMBER,
            "title": "Levenshtein edit distance",
            "description": """
                Distance between the input parameter wordform and the wordform produced by providing the analysis
                in this result to the normative generator FST.  Since the normative generator can produce multiple different outputs,
                we pick the one with the minimum edit distance among all the options.  
                **The `levenshtein_distance` value always corresponds to the distance to the `standardized` wordform**
            """
        }

class WeightField(serializers.FloatField):
    class Meta:
        swagger_schema_fields = {
            "type": openapi.TYPE_NUMBER,
            "title": "Weight",
            "description": """
                If the FST in `source` is a weighted FST, we provide the weight assigned by the FST to this particular analysis.  If the FST is unweighted, this value is `0.0`.

                Note that *most* FSTs used at ALTLab are currently unweighted.  In Summer 2026, the only weighted FST used at ALTLab is the one for Blackfoot.
            """
        }

class SourceField(serializers.StringRelatedField):
    class Meta:
        swagger_schema_fields = {
            "type": openapi.TYPE_NUMBER,
            "title": "Source",
            "description": """
                The FST used to provide the results.  Either the value of `FST_API_FST_PATH/FST_API_ANALYSER_DESC_FST` or `FST_API_FST_PATH/FST_API_ANALYSER_NORM_FST`

                Currently, the API first attempts to use `FST_API_ANALYSER_NORM_FST` (`NORM`, in the Giella infrastructure, stands for *normative*.  It is the base FST.).
                If this FST produces no outputs, it attempts to use `FST_API_ANALYSER_DESC_FST` (`DESC`, in the Giella infrastructure, stands for *descriptive*.  It is usually the combination of the normative FST plus spelling relaxation rules, so it accepts misspelled results and provides analyses for them).

                Note that, currently, all the results in the list will have the same value for `source`.  In the future, this might not remain the case, as the API might be changed to return results from multiple FSTs.
            """
        }

class AnalysisSerializer(serializers.Serializer):
    """
    Specialized Field Classes are used in this Serializer to enable documentation in the API.
    Analysis fields are standard just because their documentation appears in the AnalysisList general documentation.
    """
    lemma = serializers.StringRelatedField()
    prefixes = serializers.ListField(child=serializers.StringRelatedField())
    suffixes = serializers.ListField(child=serializers.StringRelatedField())
    standardized = StandardizedField()
    levenshtein_distance = LevenshteinDistanceField()
    source = SourceField()
    weight = WeightField()

wordform_param = openapi.Parameter('wordform', openapi.IN_PATH, description="Word string being queried to the FSTs, usually comes from user input in a search", type=openapi.TYPE_STRING)
response = openapi.Response("", schema=AnalysisSerializer)

@swagger_auto_schema(manual_parameters=[wordform_param], responses={200: response})
class AnalysisList(generics.ListAPIView):
    """
    Analysis List

    Apply the FST to the wordform and produce a list of analyses.

    Note that this assumes an FST that produces analyses of the following form:

    ```
    <multi_character_token>* <single_character_token>* <multi_character_token>*
    ```

    An analysis is generated by parsing the stream of tokens produced by the FST as an analysis, and grouping them as follows:
    - All `multi_character_token`'s at the beginning are returned in the `"prefixes"` field, as a list of strings (one per token)
    - All `single_character_token`'s are put together in a single string and returned as the `"lemma"` field
    - All `multi_character_token`'s at the end are returned in the `"suffixes"` field, as a list of strings (one per token)

    All Giella, ALTLab, and ELF-Lab FSTs currently follow this convention. 
    """

    serializer_class = AnalysisSerializer

    def get_queryset(self):
        wordform = self.kwargs["wordform"]
        return cached_analyse(wordform)
