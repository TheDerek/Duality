from dataclasses import dataclass
from typing import Dict, List


@dataclass()
class Situation:
    prompt: str
    drawing: str
    results: str


def get_situations() -> Dict[int, Situation]:
    situations: List[Situation] = [
        Situation(
            "In a radical departure from your current profession you decide to apply for a job at a _.",
            "Draw a model employee who could work for both a _ and a _",
            "What companies could this model employee work for?"
        ),
        Situation(
            "Much to the annoyance of your peers, you decide to take up _ as a hobby.",
            "Draw a person proficient in both _ and _",
            "What hobbies is this person an expert of?"
        ),
        Situation(
            "There is a 21st century hell for 21st century sins, what would one of those sins be?",
            "Draw someone who commits both _ and _",
            "What sins does this person commit?"
        ),
        Situation(
            "You use a newly developed time machine to travel back in time. To make your current time a better place"
            " you decide to save _ from an untimely death.",
            "Draw the ideal person, half _ and half _",
            "Who is this person comprised of?"
        ),
        Situation(
            "For some inexplicable reason you are chosen to man the first interstellar voyage of human kind."
            " During this voyage you encounter an alien species who you are surprised to find look eerily similar to a"
            " _, a common household object.",
            "Draw an alien who looks similar to both a _ and a _",
            "What objects is this alien similar to?"
        ),
        Situation(
            "As a great explorer, you have discovered many wonders and ancient civilisations. However by far and away"
            " your greatest discovery is _.",
            "During a trip to the British Museum you come across an exhibit that depicts both _ and _. Draw what this"
            " exhibit looks like.",
            "What wonders does this museum exhibit depict?"
        ),
    ]

    return {index: situation for index, situation in enumerate(situations)}
