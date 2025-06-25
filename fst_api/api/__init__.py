from rest_framework import serializers, generics
from rest_framework.response import Response
from hfst_altlab import TransducerPair

fsts = TransducerPair(analyser="resources/analyser-dict-gt-desc.hfstol", generator="resources/generator-dict-gt-norm.hfstol")

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
        wordform = self.kwargs['wordform']
        return fsts.analyse(wordform)
