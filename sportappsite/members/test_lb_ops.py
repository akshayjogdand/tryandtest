from dataclasses import dataclass
import random
from collections import namedtuple
from prettytable import PrettyTable
import itertools


def pp(title, x):
    print(title)
    sample = x[0]
    f_names = sample.__dataclass_fields__.keys()
    pt = PrettyTable()
    pt.field_names = f_names

    for i in x:
        row = list()

        for f in f_names:
            row.append(getattr(i, f))

        pt.add_row(row)

    print(pt)


Match = namedtuple("Match", ("match_number",))

ALWAYS_ZERO = set()

MEMBERS = "A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,Z,Y,Z".split(",")


@dataclass
class LeaderboardEntry:
    member: str
    previous_total: int
    this_match: int
    total: int
    previous_position: int
    position_now: int
    movement: int
    match: int

    def __repr__(self):
        return f"{self.member}-{self.match}  PT={self.previous_total}  MS={self.this_match} T={self.total}    PP={self.previous_position}  PN={self.position_now} M={self.movement}"


def gen_lb(match, prev=None, skew_scores=False):
    if prev is None:
        le_cache = list()
        for name in MEMBERS:
            this_match = random.randint(0, 1000)
            le = LeaderboardEntry(
                name, 0, this_match, this_match, 0, 0, 0, match.match_number
            )
            le_cache.append(le)

    else:
        le_cache = prev
        for p in le_cache:
            this_match = random.randint(0, 1000)
            p.this_match = this_match
            p.previous_total = p.total
            p.total = this_match + p.total
            p.match = match.match_number
            p.previous_position = p.position_now

    if skew_scores:
        le_to_skew = (
            random.randrange(0, len(le_cache), 1)
            for i in range(1, random.randrange(1, 10, 1))
        )
        same_score = random.randint(0, 1000)
        skewed_members = []

        for index in set(le_to_skew):
            le = le_cache[index]
            le.this_match = same_score - le.previous_total
            le.total = same_score
            skewed_members.append(le.member)

        print(f"Skewed score: {same_score}")

    for le in le_cache:
        if le.member in ALWAYS_ZERO:
            le.total = 0
            le.previous_total = 0
            le.this_match = 0

    return le_cache


def do_sorting(match, le_cache):
    le_cache.sort(key=lambda e: e.previous_position)
    le_cache.sort(key=lambda e: e.total, reverse=True)
    grouped_by_total = itertools.groupby(le_cache, lambda le: le.total)

    for position, (_, entries) in enumerate(grouped_by_total, 1):
        for le in entries:
            le.position_now = position
            if le.previous_position != 0:
                le.movement = (le.position_now - le.previous_position) * -1
            else:
                le.movement = le.position_now

            if match.match_number == 1:
                le.movement = 0

    pp(f"Match {match.match_number}, always_zero={ALWAYS_ZERO}", le_cache)


def main():
    for z in (
        random.randrange(0, len(MEMBERS), 1)
        for i in range(1, random.randrange(1, 10, 1))
    ):
        ALWAYS_ZERO.add(MEMBERS[z])

    match = Match(1)
    m1 = gen_lb(match)
    do_sorting(match, m1)

    match = Match(2)
    m2 = gen_lb(match, m1)
    do_sorting(match, m2)

    match = Match(3)
    m3 = gen_lb(match, m2)
    do_sorting(match, m3)

    match = Match(4)
    m4 = gen_lb(match, m3)
    do_sorting(match, m4)

    match = Match(5)
    m5 = gen_lb(match, m4)
    do_sorting(match, m5)

    match = Match(6)
    m6 = gen_lb(match, m5, skew_scores=True)
    do_sorting(match, m6)

    match = Match(7)
    m7 = gen_lb(match, m5, skew_scores=True)
    do_sorting(match, m6)

    match = Match(8)
    m8 = gen_lb(match, m5, skew_scores=True)
    do_sorting(match, m7)


if __name__ == "__main__":
    main()
