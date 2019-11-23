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
      <Grid item xs={12} sm={10} md={8} lg={5} xl={4}>
        {children}
      </Grid>
    </Grid>
  );
}

export { Center };
