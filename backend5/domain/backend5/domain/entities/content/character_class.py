class CharacterClass:
    def __init__(self, name, hit_die, primary_ability, saving_throws, proficiencies):
        self.name = name
        self.hit_die = hit_die
        self.primary_ability = primary_ability
        self.saving_throws = saving_throws
        self.proficiencies = proficiencies

    def __repr__(self):
        return f"<CharacterClass(name={self.name}, hit_die={self.hit_die}, primary_ability={self.primary_ability})>"

    def get_proficiencies(self):
        return self.proficiencies

    def get_saving_throws(self):
        return self.saving_throws

    def get_hit_die(self):
        return self.hit_die

    def get_name(self):
        return self.name