# Duality (name pendng)

## Known bugs
- If the server disconnects from the player it will not correctly reconnect,
  assigning uuids and stuff on the server side, causing the client not to
  get responses. I would just return to the main menu / lobby in the client
  if it cannot return to the server and display an error message

## TODO
- [x] Correctly display waiting/done players in prompt submission
- [ ] Transition to next stage if all players have submitted their prompts 
