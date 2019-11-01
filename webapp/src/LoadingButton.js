import React from "react";
import Box from "@material-ui/core/Box";
import Button from "@material-ui/core/Button";
import CircularProgress from "@material-ui/core/CircularProgress";
import { makeStyles } from "@material-ui/core/styles";
import { green } from "@material-ui/core/colors";
import clsx from "clsx";

const useStyles = makeStyles({
  container: {
    position: "relative",
    display: "flex",
    justifyContent: "center"
  },
  progress: {
    color: green[500],
    position: "absolute",
    top: "50%",
    left: "50%",
    marginTop: -12,
    marginLeft: -12
  }
});

export function LoadingButton({
  className,
  disabled,
  loading,
  children,
  ...props
}) {
  const classes = useStyles();
  return (
    <Box className={clsx([className, classes.container])}>
      <Button disabled={disabled || loading} {...props}>
        {children}
      </Button>
      {loading && <CircularProgress size={24} className={classes.progress} />}
    </Box>
  );
}
