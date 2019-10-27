import React from "react";
import Grid from "@material-ui/core/Grid";

function Center({ children }) {
  return (
    <Grid
      container
      spacing={0}
      alignItems="center"
      justify="center"
      style={{ minHeight: "100vh" }}
    >
      {children}
    </Grid>
  );
}

export { Center };
