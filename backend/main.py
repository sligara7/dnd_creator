# place to design new characters, NPCs, and monsters/beasts/creatures for Dungeon & Dragons

# host as service on server (use a docker container)

# backend/core directory has: ability_scores, alignment, character, classes, equipment, feats, personality_and_backstory, skills, species, and spells;
# each subdirectory has a abstract class that every new character created must adhere to

# link to or embed free LLM to aid/populate new character creation;

# idea would be, player goes to webpage, provides answers to a series of questions like:

# prompt 1: describe your new character?
# prompt 2: what is the sex of your new character?
# prompt 3: tell me some things about your personality_and_backstory
# prompt 4: what are some characteristics (powers, abilities, etc) that you would like your character to have?
# prompt N: final prompt necessary to fully create your character

# with each prompt, the LLM auto-populates one of the abstract classes (or portions of)

# LLM should moderate the character creation so that every character created is roughly equal in terms of abilities and skills
# For instance, if a player creates "Bob, the plummer" and another creates "Pheonix, the Sun God", they would roughly progress equivalently as they level up
# the idea is not to be able to create a god-like character that cannot be defeated and no other character can compete with

# frontend would allow for a DM to go to the webpage and approve a new character creation as well as create NPCs, monsters, beasts, and other creatures (also utilizing the LLM)

# frontend would also allow players to view their characters and level them up as they progress

# should have some backend to save created characters

# Basically, everything should be modifiable as long as it adheres to a abstract classes for character creation, whether that be spells or weapons or species... all are customizable

# Players and DMs should also be able to go into their character and create a journal and notes as appropriate

# Another feature would be to create "way points" that track or save a player's evolution as they level up (should be included in the journal)

# cool feature would be for LLM to review and summarize events for the DM to keep a master journal of all characters and other significant events in game-player

# another cool feature would be at the end of a player creation, the LLM would automatically generate a series of images that best describe the character created

# should adhere as much as possible to DnD rules 5e (2024 edition)
