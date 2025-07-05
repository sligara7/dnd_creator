# D&D Campaign Creator - Requirements Specification

uses: https://getimg.ai/use-cases/ai-dnd-map-maker

takes inputs from campaign creator (/backend_campaign/app.py) endpoints for creating maps (both campaign and encounter (tactical) maps) - should suggest theme and provide all necessary inputs to prompt

- maps should have grids to mark out distances
- encounter maps will have to support overlay of character positions for in-game play
- encounter maps will have to support overlay of ranges of spells and other character abilities
- encounter maps will have to support overlay of NPCs and monster positions

- campaign maps will have to mark out position of party of characters, ruins, cities, etc
- campaign maps are like operational level
- encounter maps are like tactical level maps

- database will need to store both campaign and encounter maps for future use and/or reference
- maps need to have a UUID

takes inputs from character creator (/backend/app.py) endpoints for creating images of characters, monsters, NPCs, and items (armors, weapons, and other items) that are created by the character creator service. These images will need to stored in this database, but associated with created content in /backend database.

should be containerized service in podman container.

references: 
https://docs.getimg.ai/reference/introduction
https://docs.getimg.ai/reference/introduction-1
https://docs.getimg.ai/reference/pricing
https://docs.getimg.ai/reference/image-responses
https://docs.getimg.ai/reference/errors
https://docs.getimg.ai/reference/rate-limits
https://docs.getimg.ai/reference/request-ids

character, NPC, monsters, and items creation endpoints at /backend/app.py
campaign creation endpoints at /backend_campaign/app.py



