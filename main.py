import argparse
import enum
import json
import random
from typing import List, Optional


def read_words():
    with open('words.json') as f:
        return json.load(f)


class LetterStatus(str, enum.Enum):
    UNSET = ' '
    CORRECT = 'v'
    WRONG = '-'
    CONTAINS = '+'


class WordleGuesser:
    WORD_LEN = 5

    def __init__(self, common_words: List[str], hard: bool):
        self._words = common_words
        self._hard = hard
        self._previous_word = '_' * self.WORD_LEN
        self._state = [LetterStatus.UNSET] * self.WORD_LEN
        self._used_letters = set()

    @property
    def state(self) -> List[LetterStatus]:
        return self._state

    def enter_state(self, state: List[LetterStatus]):
        self._state = state
        filtered_words = []
        for word in self._words:
            if self._matches(word):
                filtered_words.append(word)
        self._words = filtered_words

    def guess(self) -> Optional[str]:
        if not self._words:
            return
        scored_words = sorted(self._words, key=lambda x: (self._diversity_score(x), self._common_letter_placement_score(x), random.random()), reverse=True)
        self._previous_word = scored_words[0]
        for letter in self._previous_word:
            self._used_letters.add(letter)
        return self._previous_word

    def _matches(self, word: str) -> bool:
        word = word.lower()
        assert len(word) == len(self._state) == len(self._previous_word), 'wtf'
        for current_letter, previous_letter, status in zip(word.lower(), self._previous_word.lower(), self._state):
            if status is LetterStatus.UNSET:
                continue
            if status is LetterStatus.CORRECT and current_letter != previous_letter:
                return False
            if status is LetterStatus.WRONG and current_letter == previous_letter:
                return False
            if status is LetterStatus.CONTAINS and previous_letter not in word:
                return False
        return True

    def _diversity_score(self, word: str):
        if self._hard:
            return len(set(word))
        return len(set(word)) - len(set(word) & self._used_letters)

    def _common_letter_placement_score(self, word: str):
        score = 0
        # for other_word in self._words:
        #     for letter, other_letter, status in zip(word, other_word, self._state):
        #         if status is LetterStatus.CORRECT:
        #             continue
        #         score += int(letter == other_letter)
        return score


class Emulator:
    def __init__(self, secret_word: str):
        self._secret_word = secret_word

    def enter_word(self, word: str) -> List[LetterStatus]:
        state = []
        for secret_letter, letter in zip(self._secret_word.lower(), word.lower()):
            if secret_letter == letter:
                state.append(LetterStatus.CORRECT)
            elif letter in self._secret_word:
                state.append(LetterStatus.CONTAINS)
            else:
                state.append(LetterStatus.WRONG)
        return state


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--mode', choices=['emulate', 'play'])
    argparser.add_argument('--hard', action='store_true')
    args = argparser.parse_args()

    if args.mode == 'play':
        guesser = WordleGuesser(read_words(), args.hard)
        while not all([x is LetterStatus.CORRECT for x in guesser.state]):
            next_word = guesser.guess()
            if not next_word:
                print('I don\'t know the answer')
                return
            print('Guess:      ', next_word)
            while True:
                try:
                    state = input('Enter state: ')
                    assert len(state) == WordleGuesser.WORD_LEN, f'State len should be {WordleGuesser.WORD_LEN}'
                    state = [LetterStatus(x) for x in state]
                    break
                except Exception as e:
                    print(e)
            guesser.enter_state(state)

    if args.mode == 'emulate':
        secret_word = input('Enter a secret word:\n').strip()
        assert len(secret_word) == WordleGuesser.WORD_LEN

        emulator = Emulator(secret_word)
        guesser = WordleGuesser(read_words(), args.hard)

        while not all([x is LetterStatus.CORRECT for x in guesser.state]):
            next_word = guesser.guess()
            if not next_word:
                print('I don\'t know the answer')
                return
            print(next_word)

            state = emulator.enter_word(next_word)
            print(''.join(state))
            print()

            guesser.enter_state(state)


if __name__ == '__main__':
    main()
