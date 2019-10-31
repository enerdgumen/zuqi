import React from "react";
import { SnackbarProvider } from "./Snackbar";
import { Center } from "./Layout";
import { Theme } from "./Theme";
import Welcome from "./Welcome";

function App() {
  return (
    <Theme>
      <SnackbarProvider>
        <Center>
          <Welcome />
        </Center>
      </SnackbarProvider>
    </Theme>
  );
}

export default App;
