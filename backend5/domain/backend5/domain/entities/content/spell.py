class Spell:
    def __init__(self, name, level, school, casting_time, range, components, duration, description):
        self.name = name
        self.level = level
        self.school = school
        self.casting_time = casting_time
        self.range = range
        self.components = components
        self.duration = duration
        self.description = description

    def __repr__(self):
        return f"<Spell(name={self.name}, level={self.level}, school={self.school})>"

    def is_castable(self, caster_level):
        return caster_level >= self.level

    def get_spell_info(self):
        return {
            "name": self.name,
            "level": self.level,
            "school": self.school,
            "casting_time": self.casting_time,
            "range": self.range,
            "components": self.components,
            "duration": self.duration,
            "description": self.description,
        }