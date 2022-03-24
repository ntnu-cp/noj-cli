import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from .submission import Submission


class MultiDeadLinePolicy:
    '''
    Given submission and deadline-ratio tuple to generate scores
    '''

    class ProblemStat:

        def __init__(
            self,
            pid: int,
            deadlines: List[Tuple[datetime, int]],
        ) -> None:
            self.pid = pid
            # Sort by time
            self.deadlines = sorted(deadlines)
            # High score before each deadline
            self.scores = [0] * len(deadlines)

        def update(self, submission: Submission):
            assert submission.problem_id == self.pid
            for i, s in enumerate(self.scores):
                if submission.created < self.deadlines[i][0]:
                    self.scores[i] = max(s, submission.score)

        @property
        def final_score(self):
            diffs = [
                self.scores[i] - s
                for i, s in enumerate([0] + self.scores[:-1])
            ]
            final = sum(d * self.deadlines[i][1] / 100
                        for i, d in enumerate(diffs))
            return final

        def __repr__(self) -> str:
            cls_name = self.__class__.__name__
            score_infos = [(d[0].isoformat(), d[1], s)
                           for d, s in zip(self.deadlines, self.scores)]
            return f'{cls_name}({self.pid}, {score_infos})'

    def __init__(
        self,
        submissions: List[Submission],
        students: List[str] = None,
        weights: Optional[Dict[int, int]] = None,
        deadlines: List[Tuple[datetime, int]] = [],
        excludes: Optional[List[str]] = None,
    ) -> None:
        if len(submissions) == 0:
            raise ValueError('Empty submissions')
        self.submissions = submissions
        if students is None:
            students = {s.user.username for s in submissions}
        if excludes is not None:
            if not isinstance(students, set):
                students = {*students}
            students -= {*excludes}
            students = [*students]
        self.students = students
        if len(deadlines) == 0:
            deadlines = [(datetime.max, 100)]
        self.deadlines = deadlines
        # If not specified
        if weights is None:
            pids = [*{s.problem_id for s in self.submissions}]
            weight = 100 // len(pids)
            weights = {pid: weight for pid in pids}
            weights[pids[0]] += (100 - len(pids) * weight)
        self.weights = weights

    def validate(self):
        assert sum(self.weights.values()) == 100, self.weights
        assert {*self.weights} == {*(s.problem_id for s in self.submissions)}

    def gen_score(self, out: Path):
        self.validate()
        # student: { pid: score }
        stu_dict = lambda: {
            pid: self.ProblemStat(
                pid,
                self.deadlines,
            )
            for pid in self.weights
        }
        scores = {s: stu_dict() for s in self.students}
        # Update problem
        for s in self.submissions:
            u = s.user.username
            if u in scores:
                scores[u][s.problem_id].update(s)
        # Generate csv rows
        rows = []
        for u, stats in scores.items():
            logging.debug(f'User {u}')
            for stat in stats.values():
                logging.debug(repr(stat))
            total = sum(self.weights[pid] * stat.final_score / 100
                        for pid, stat in stats.items())
            rows.append({
                'username': u,
                **{pid: stat.final_score
                   for pid, stat in stats.items()},
                'total': total,
            })
        with out.open('w') as f:
            writer = csv.DictWriter(
                f,
                [
                    'username',
                    *self.weights,
                    'total',
                ],
            )
            writer.writeheader()
            writer.writerows(rows)
