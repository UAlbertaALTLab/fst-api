from functools import cache

from django.conf import settings
from hfst import TransducerFile
from .types import RichAnalysis

FST_DIR = settings.BASE_DIR / "resources" / "fst"


@cache
def strict_generator():
    return TransducerFile(FST_DIR / settings.STRICT_GENERATOR_FST_FILENAME)


@cache
def strict_generator_with_morpheme_boundaries():
    return TransducerFile(FST_DIR / "generator-gt-dict-norm-with-boundaries.hfstol")


@cache
def relaxed_analyzer():
    return TransducerFile(FST_DIR / settings.RELAXED_ANALYZER_FST_FILENAME)


@cache
def strict_analyzer():
    return TransducerFile(FST_DIR / settings.STRICT_ANALYZER_FST_FILENAME)

def rich_analyze_relaxed(text):
    return list(
        RichAnalysis(r) for r in relaxed_analyzer().lookup_lemma_with_affixes(text)
    )

def rich_analyze_strict(text):
    return list(
        RichAnalysis(r) for r in strict_analyzer().lookup_lemma_with_affixes(text)
    )
