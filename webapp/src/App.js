import React, { Fragment } from "react";
import CssBaseline from "@material-ui/core/CssBaseline";
import { Center } from "./Layout";
import { Welcome } from "./Welcome";

function App() {
  return (
    <Fragment>
      <CssBaseline />
      <Center>
        <Welcome />
      </Center>
    </Fragment>
  );
}

export default App;
