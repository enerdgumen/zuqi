import React from "react";
import ErrorBoundary from "react-error-boundary";
import { SnackbarProvider } from "./Snackbar";
import { Theme } from "./Theme";
import Game from "./Game";

function App() {
  return (
    <Theme>
      <SnackbarProvider>
        <ErrorBoundary>
          <Game />
        </ErrorBoundary>
      </SnackbarProvider>
    </Theme>
  );
}

export default App;
