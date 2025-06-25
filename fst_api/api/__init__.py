from rest_framework import serializers, generics
from django.conf import settings
from hfst_altlab import TransducerPair
from functools import lru_cache

fsts = TransducerPair(analyser=settings.ANALYSER_FST, generator=settings.GENERATOR_FST)


@lru_cache(maxsize=10240)
def cached_analyse(wordform):
    return fsts.analyse(wordform)


class AnalysisSerializer(serializers.Serializer):
    lemma = serializers.StringRelatedField()
    prefixes = serializers.ListField(child=serializers.StringRelatedField())
    suffixes = serializers.ListField(child=serializers.StringRelatedField())
    standardized = serializers.StringRelatedField()


class AnalysisList(generics.ListAPIView):
    """
    Apply the FST to the wordform and produce a list of analyses.
    """

    serializer_class = AnalysisSerializer

    def get_queryset(self):
        wordform = self.kwargs["wordform"]
        return cached_analyse(wordform)
