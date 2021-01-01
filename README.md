# Duality (name pendng)

## Known bugs
- If the server disconnects from the player it will not correctly reconnect,
  assigning uuids and stuff on the server side, causing the client not to
  get responses. I would just return to the main menu / lobby in the client
  if it cannot return to the server and display an error message
- A user can join the game with a name that is already in use in the game if they
  use a different case, this should have been dealt with, need to test
- With the current canvas implementation the mouse dose not continue drawing if
  it leaves the canvas area, this is not good

## TODO
- [x] Correctly display waiting/done players in prompt submission
- [ ] Transition to next stage if all players have submitted their prompts 
