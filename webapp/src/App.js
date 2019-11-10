import React from "react";
import { SnackbarProvider } from "./Snackbar";
import { Theme } from "./Theme";
import Game from "./Game";

function App() {
  return (
    <Theme>
      <SnackbarProvider>
        <Game />
      </SnackbarProvider>
    </Theme>
  );
}

export default App;
