import React from "react";
import CssBaseline from "@material-ui/core/CssBaseline";
import { createMuiTheme, ThemeProvider } from "@material-ui/core/styles";
import { grey } from "@material-ui/core/colors";
import { SnackbarProvider } from "./Snackbar";
import { Center } from "./Layout";
import { Welcome } from "./Welcome";

const theme = createMuiTheme({
  palette: {
    background: {
      default: grey[200]
    }
  }
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider>
        <Center>
          <Welcome />
        </Center>
      </SnackbarProvider>
    </ThemeProvider>
  );
}

export default App;
