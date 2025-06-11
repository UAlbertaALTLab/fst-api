import hfst
from .types import Analysis


class FileTransducer:
    """
    Loads an ``..................hfst`` or an ``.hfstol`` transducer file.
    This is intended as a replacement and extension of the 
    hfst-optimized-lookup python package, but depending on the
    hfst project to pack the C code directly.  This provides the
    added benefit of regaining access to weighted FSTs without extra work.
    Note that lookup will only be fast if the input file has been processed
    into the hfstol format.
    """
    def __init__(self, filename:str, search_cutoff:str=60):
        self.cutoff=search_cutoff

        # Now we extract the transducer and store it.
        stream = hfst.HfstInputStream(filename)
        transducers = stream.read_all()
        if not len(transducers) == 1:
            error = ValueError(self)
            error.add_note("We expected a single transducer to arise in the file.")
            stream.close()
            raise error

        stream.close()
        self.transducer = transducers[0]
        if self.transducer.is_infinitely_ambiguous():
            raise RuntimeWarning("The transducer is infinitely ambiguous.")

    def bulk_lookup(self, words: list[str]) -> dict[str,set[str]]:
        """
         Like ``lookup()`` but applied to multiple inputs. Useful for generating multiple
        surface forms.

        :param words: list of words to lookup
        :type words: list[str]
        :return: a dictionary mapping words in the input to a set of its tranductions
        :rtype: dict[str, set[str]]
        """
        return { word : self.lookup(word) for word in words}

    def lookup(self, input: str) -> list[str]:
        """
        Lookup the input string, returning a list of tranductions.  This is
        most similar to using ``hfst-optimized-lookup`` on the command line.

        :param str string: The string to lookup.
        :return: list of analyses as concatenated strings, or an empty list if the input
            cannot be analyzed.
        :rtype: list[str]
        """
        return [''.join(transduction) for transduction in self.lookup_symbols(input)]

    def weighted_lookup_lemma_with_affixes(self, surface_form: str) -> list[tuple[float, Analysis]]:
        """
        Analyze the input string, returning a list
        of :py:class:`types.Analysis` objects.

        .. note::
            this method assumes an analyzer in which all multicharacter symbols
            represent affixes, and all lexical symbols are contiguous.


        :param str string: The string to lookup.
        :return: list of analyses as :py:class:`types.Analysis`
            objects, or an empty list if there are no analyses.
        :rtype: list of :py:class:`types.Analysis`
        """
        raw_weighted_analyses = self.lookup_symbols(surface_form)
        return [(weight,_parse_analysis(analysis)) for weight, analysis in raw_weighted_analyses]

    def lookup_symbols(self, input: str) -> list[list[str]]:
        """
        Transduce the input string. The result is a list of tranductions. Each
        tranduction is a list of symbols returned in the model; that is, the symbols are
        not concatenated into a single string.

        :param str input: The string to lookup.
        :return:
        :rtype: list[list[str]]
        """
        return [
            [symbol for symbol in symbols if not hfst.is_diacritic(symbol)]
            for weight, symbols in self.weighted_lookup_symbols_with_flags(input)
        ]    

    def weighted_lookup_symbols_with_flags(self, input: str) -> list[tuple[float,list[str]]]:
        """
        Transduce the input string, preserving the weight information coming from HFST and separating each symbol

        :param str input: The string to lookup.
        :return: A list of tuples, each containing the weight(float), and a list of strings, each a language symbol
        :rtype: list[tuple[float,list[str]]]
        """
        return list(self.transducer.lookup(input,time_cutoff=self.cutoff, output='raw'))

    def symbol_count(self) -> int:
        """
        symbol_count() -> int

        Returns the number of symbols in the sigma (the symbol table or alphabet).

        :rtype: int
        """
        return len(self.transducer.get_alphabet())
    
def _parse_analysis(letters_and_tags: list[str]) -> Analysis:
    prefix_tags = []
    prefix_flags = []
    lemma_chars = []
    lemma_flags = []
    suffix_tags = []
    suffix_flags = []
    
    tag_destination = prefix_tags
    flag_destination = prefix_flags
    for symbol in letters_and_tags:
        if len(symbol) == 1:
            if hfst.is_diacritic(symbol):
                lemma_flags.append(symbol)
            else:
                lemma_chars.append(symbol)
            tag_destination = suffix_tags
            flag_destination = suffix_flags
        else:
            if hfst.is_diacritic(symbol):
                flag_destination.append(symbol)
            else:
                tag_destination.append(symbol)

    return Analysis(
        tuple(prefix_tags),
        ''.join(lemma_chars),
        tuple(suffix_tags),
        tuple(prefix_flags),
        tuple(lemma_flags),
        tuple(suffix_flags)
    )