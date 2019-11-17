import React from "react";
import { Players, Player } from "../src/Players";

export default {
  title: "Players"
};

export const SomePlayers = () => (
  <Players>
    <Player username="luigi" status="alive" />
    <Player username="mario" status="loser" />
    <Player username="peach" status="challenging" />
    <Player username="goby" status="winner" />
  </Players>
);
