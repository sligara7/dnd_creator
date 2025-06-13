class ContentFactory:
    """
    Factory class for creating content entities.
    """

    @staticmethod
    def create_species(name, traits):
        """
        Create a species entity.

        :param name: The name of the species.
        :param traits: The traits associated with the species.
        :return: A new species entity.
        """
        from domain.entities.content.species import Species
        return Species(name=name, traits=traits)

    @staticmethod
    def create_character_class(name, features):
        """
        Create a character class entity.

        :param name: The name of the character class.
        :param features: The features associated with the character class.
        :return: A new character class entity.
        """
        from domain.entities.content.character_class import CharacterClass
        return CharacterClass(name=name, features=features)

    @staticmethod
    def create_subclass(name, parent_class, features):
        """
        Create a subclass entity.

        :param name: The name of the subclass.
        :param parent_class: The parent character class.
        :param features: The features associated with the subclass.
        :return: A new subclass entity.
        """
        from domain.entities.content.subclass import Subclass
        return Subclass(name=name, parent_class=parent_class, features=features)

    @staticmethod
    def create_spell(name, level, description):
        """
        Create a spell entity.

        :param name: The name of the spell.
        :param level: The level of the spell.
        :param description: The description of the spell.
        :return: A new spell entity.
        """
        from domain.entities.content.spell import Spell
        return Spell(name=name, level=level, description=description)

    @staticmethod
    def create_feat(name, description):
        """
        Create a feat entity.

        :param name: The name of the feat.
        :param description: The description of the feat.
        :return: A new feat entity.
        """
        from domain.entities.content.feat import Feat
        return Feat(name=name, description=description)

    @staticmethod
    def create_equipment(name, type, properties):
        """
        Create an equipment entity.

        :param name: The name of the equipment.
        :param type: The type of the equipment.
        :param properties: The properties associated with the equipment.
        :return: A new equipment entity.
        """
        from domain.entities.content.equipment import Equipment
        return Equipment(name=name, type=type, properties=properties)

    @staticmethod
    def create_magic_item(name, properties):
        """
        Create a magic item entity.

        :param name: The name of the magic item.
        :param properties: The properties associated with the magic item.
        :return: A new magic item entity.
        """
        from domain.entities.content.magic_item import MagicItem
        return MagicItem(name=name, properties=properties)

    @staticmethod
    def create_background(name, features):
        """
        Create a background entity.

        :param name: The name of the background.
        :param features: The features associated with the background.
        :return: A new background entity.
        """
        from domain.entities.content.background import Background
        return Background(name=name, features=features)

    @staticmethod
    def create_monster(name, challenge_rating, features):
        """
        Create a monster entity.

        :param name: The name of the monster.
        :param challenge_rating: The challenge rating of the monster.
        :param features: The features associated with the monster.
        :return: A new monster entity.
        """
        from domain.entities.content.monster import Monster
        return Monster(name=name, challenge_rating=challenge_rating, features=features)