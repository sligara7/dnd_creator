class SpellComponents:
    """
    Represents the components required for casting spells in D&D.
    """

    def __init__(self, verbal: bool, somatic: bool, material: bool, material_components: list = None):
        self.verbal = verbal  # Indicates if verbal components are required
        self.somatic = somatic  # Indicates if somatic components are required
        self.material = material  # Indicates if material components are required
        self.material_components = material_components if material_components is not None else []  # List of material components

    def __eq__(self, other):
        if not isinstance(other, SpellComponents):
            return NotImplemented
        return (self.verbal == other.verbal and
                self.somatic == other.somatic and
                self.material == other.material and
                self.material_components == other.material_components)

    def __repr__(self):
        return (f"SpellComponents(verbal={self.verbal}, "
                f"somatic={self.somatic}, "
                f"material={self.material}, "
                f"material_components={self.material_components})")

    def add_material_component(self, component: str):
        """
        Adds a material component to the spell.
        """
        self.material_components.append(component)

    def remove_material_component(self, component: str):
        """
        Removes a material component from the spell.
        """
        if component in self.material_components:
            self.material_components.remove(component)