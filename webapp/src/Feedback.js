import React, { useState } from "react";
import Snackbar from "@material-ui/core/Snackbar";

function Feedback({ message }) {
  const [open, setOpen] = useState(true);
  return (
    <Snackbar
      anchorOrigin={{
        vertical: "bottom",
        horizontal: "center"
      }}
      open={open}
      onClose={() => setOpen(false)}
      autoHideDuration={3000}
      message={message}
    />
  );
}

export { Feedback };
