from collections import defaultdict

import cyrtranslit
import rapidfuzz
from unidecode import unidecode

from src.infra.chache import another_cache
import heapq



@another_cache.cache_on_arguments()
def build_query_options(query: str):
    text_en = cyrtranslit.to_latin(query.lower(), 'ru')
    text_ru = cyrtranslit.to_cyrillic(query.lower(), 'ru')
    simplified_version = unidecode(query.lower())
    return text_ru, text_en, simplified_version


@another_cache.cache_on_arguments()
def search_nicknames(query: str, nicknames: list[str], limit: int = 5) -> tuple:
    """Поиск по префиксу с приоритетом по началу строки и транслитерацией"""
    query_options = build_query_options(query)

    nicknames_dict = {nickname.lower(): nickname for nickname in nicknames}
    def _scorer(s1, s2, score_cutoff=None):
        base_score = rapidfuzz.fuzz.WRatio(s1, s2, score_cutoff=score_cutoff)
        if s2.startswith(s1):
            return min(100, int(base_score) + 30)
        return base_score

    found_nickname_set = set()
    for query in query_options:
        matches = rapidfuzz.process.extract(
            query,
            nicknames_dict.keys(),
            scorer=_scorer,
            score_cutoff=70,
            limit=limit
        )
        found_nickname_set.update(matches)

    # Объединяем результаты, выбирая лучший балл для каждого никнейма
    best_scores = defaultdict(lambda: -float('inf'))

    for nickname, score, idx in found_nickname_set:
        best_scores[nickname] = max(best_scores[nickname], score)

    score_pairs = [(score, nickname) for nickname, score in best_scores.items()]
    sorted_pairs = heapq.nlargest(limit, score_pairs)
    fuzzy_results = tuple(nicknames_dict[nickname] for score, nickname in sorted_pairs)
    return fuzzy_results


if __name__ == '__main__':
    nicknames = ["Bodren", "Tsaplya", "Альпач", "Ведьмочка", "Snaff", "Молли", "Морти", "Йегерешкин", "FFT"]
    # print(f"{search_nicknames('Ц', nicknames)=}")
    # print(f"{search_nicknames('Ца', nicknames)=}")
    # print(f"{search_nicknames('Цап', nicknames)=}")
    # print(f"{search_nicknames('Цапл', nicknames)=}")
    # print(f"{search_nicknames('Tsaplya', nicknames)=}")
    print(f"{search_nicknames('М', nicknames)=}")
    print(f"{search_nicknames('Мо', nicknames)=}")
    print(f"{search_nicknames('Мол', nicknames)=}")
    print(f"{search_nicknames('Моли', nicknames)=}")
