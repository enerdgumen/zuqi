import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import { amber, green } from "@material-ui/core/colors";
import { SnackbarProvider } from "notistack";

const useStyles = makeStyles(theme => ({
  error: { backgroundColor: theme.palette.error.dark },
  info: { backgroundColor: theme.palette.primary.main },
  success: { backgroundColor: green[600] },
  warning: { backgroundColor: amber[700] }
}));

const Provider = ({ children }) => {
  const classes = useStyles();
  return (
    <SnackbarProvider
      anchorOrigin={{
        vertical: "bottom",
        horizontal: "right"
      }}
      classes={{
        variantSuccess: classes.success,
        variantError: classes.error,
        variantWarning: classes.warning,
        variantInfo: classes.info
      }}
    >
      {children}
    </SnackbarProvider>
  );
};

export { Provider as SnackbarProvider };
