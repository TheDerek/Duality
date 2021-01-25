from dataclasses import dataclass
from typing import Dict, List


@dataclass()
class Situation:
    prompts: str
    drawing: str
    results: str


SITUATIONS: List[Situation] = [
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
        " you stop _ from being invented",
        "Draw world without _ and _",
        "What does this world lack?"
    ),
    Situation(
        "For some inexplicable reason you are chosen to man the first interstellar voyage of human kind."
        " During this voyage you encounter an alien species who you are surprised to find look eerily similar to _.",
        "Draw an alien who looks similar to both _ and _",
        "To what or whom does this alien bear an uncommon resemblance to?"
    ),
    Situation(
        "As a great explorer, you have discovered many wonders and ancient civilisations. However by far and away"
        " your greatest discovery is _.",
        "During a trip to the British Museum you come across an exhibit that depicts both _ and _. Draw what this"
        " exhibit looks like.",
        "What wonders does this museum exhibit depict?",
    ),
    Situation(
        "You managed to win a radio competition for an all expenses paid holiday. To your dismay you discover that the"
        " location of the holiday is in fact _",
        "Draw a tourist that would be equally welcome in both _ and _.",
        "Where is this tourist going to?"
    ),
    Situation(
        "As a world renowned fighter there is little you are afraid of. However just the mere thought of _ puts you on"
        " edge.",
        "Draw someone scared of both _ and _.",
        "What is this person afraid of?"
    )
]
