# Duality (name pendng)

## Known bugs
- If the server disconnects from the player it will not correctly reconnect,
  assigning uuids and stuff on the server side, causing the client not to
  get responses. I would just return to the main menu / lobby in the client
  if it cannot return to the server and display an error message
- With the current canvas implementation the mouse dose not continue drawing if
  it leaves the canvas area, this is not good

## TODO
- [x] Correctly display waiting/done players in prompt submission
- [x] Transition to next stage if all players have submitted their prompts 
- [ ] Save drawing to database
- [ ] Make waiting/done for players generic so it can be used across stages
- [ ] Make player status generic
- [ ] Add a seperate waiting stage that is displayed after submission of prompt/drawing
