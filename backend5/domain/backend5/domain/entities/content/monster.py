class Monster:
    def __init__(self, name, hit_points, armor_class, speed, abilities, actions):
        self.name = name
        self.hit_points = hit_points
        self.armor_class = armor_class
        self.speed = speed
        self.abilities = abilities  # Dictionary of abilities (e.g., strength, dexterity)
        self.actions = actions  # List of actions the monster can take

    def attack(self, target):
        # Logic for attacking a target
        pass

    def take_damage(self, damage):
        # Logic for taking damage
        self.hit_points -= damage
        if self.hit_points <= 0:
            self.die()

    def die(self):
        # Logic for when the monster dies
        pass

    def __str__(self):
        return f"{self.name} (HP: {self.hit_points}, AC: {self.armor_class})"