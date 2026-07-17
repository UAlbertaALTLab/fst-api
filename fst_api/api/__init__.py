from rest_framework import serializers, generics
from django.conf import settings
from hfst_altlab import TransducerFile, FullAnalysis
from functools import lru_cache
import Levenshtein

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
        self.standardized=analysis.standardized
        self.source=source
        self.levenshtein_distance = Levenshtein.distance(original_search, analysis.standardized)


@lru_cache(maxsize=10240)
def cached_analyse(wordform):
    normative_results = analyser_norm_fst.weighted_lookup_full_analysis(wordform, generator_norm_fst)
    if normative_results:
        return [APIAnalysis(analysis, settings.ANALYSER_NORM_FST, wordform) for analysis in normative_results]
    return [
        APIAnalysis(analysis, settings.ANALYSER_DESC_FST, wordform)
        for analysis in
        analyser_desc_fst.weighted_lookup_full_analysis(wordform, generator_norm_fst)
    ]


class AnalysisSerializer(serializers.Serializer):
    lemma = serializers.StringRelatedField()
    prefixes = serializers.ListField(child=serializers.StringRelatedField())
    suffixes = serializers.ListField(child=serializers.StringRelatedField())
    standardized = serializers.StringRelatedField()
    source = serializers.StringRelatedField()
    levenshtein_distance = serializers.FloatField()


class AnalysisList(generics.ListAPIView):
    """
    Apply the FST to the wordform and produce a list of analyses.
    """

    serializer_class = AnalysisSerializer

    def get_queryset(self):
        wordform = self.kwargs["wordform"]
        return cached_analyse(wordform)
