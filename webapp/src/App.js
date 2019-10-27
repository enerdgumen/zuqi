import React from "react";
import CssBaseline from "@material-ui/core/CssBaseline";
import { ThemeProvider } from "@material-ui/core/styles";
import { createMuiTheme } from "@material-ui/core/styles";
import indigo from "@material-ui/core/colors/indigo";
import { Center } from "./Layout";
import { Welcome } from "./Welcome";

const theme = createMuiTheme({
  palette: {
    background: {
      default: indigo[400]
    }
  }
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Center>
        <Welcome />
      </Center>
    </ThemeProvider>
  );
}

export default App;
