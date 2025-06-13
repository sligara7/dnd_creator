class Skills:
    """
    Represents a collection of skills for a character in D&D.
    Each skill has a name and a proficiency level.
    """

    def __init__(self, skill_name: str, proficiency_level: int):
        self.skill_name = skill_name
        self.proficiency_level = proficiency_level

    def __repr__(self):
        return f"<Skill(name={self.skill_name}, proficiency_level={self.proficiency_level})>"

    def is_proficient(self) -> bool:
        """
        Check if the character is proficient in this skill.
        """
        return self.proficiency_level > 0

    def get_skill_info(self) -> dict:
        """
        Returns a dictionary representation of the skill.
        """
        return {
            "name": self.skill_name,
            "proficiency_level": self.proficiency_level
        }