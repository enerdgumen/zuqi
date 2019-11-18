import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import Box from "@material-ui/core/Box";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import TextField from "@material-ui/core/TextField";
import { makeStyles } from "@material-ui/core/styles";
import { LoadingButton } from "./LoadingButton";

const useStyles = makeStyles(theme => ({
  root: {
    padding: theme.spacing(3)
  },
  row: {
    marginTop: theme.spacing(2),
    display: "flex",
    alignItems: "flex-end"
  },
  enterButton: {
    marginLeft: theme.spacing(2)
  }
}));

export function Welcome({ onEnter, entering }) {
  const { t } = useTranslation();
  const [username, setUsername] = useState();
  const catchReturn = ev => {
    if (ev.key === "Enter") {
      onEnter(username);
    }
  };
  const classes = useStyles();
  return (
    <Paper className={classes.root}>
      <Typography variant="h4">{t("Welcome to Zuqi")}</Typography>
      <Box className={classes.row}>
        <TextField
          autoFocus={true}
          label={t("Username")}
          onChange={e => setUsername(e.target.value)}
          onKeyPress={catchReturn}
        />
        <LoadingButton
          className={classes.enterButton}
          variant="contained"
          color="primary"
          disabled={!username}
          loading={entering}
          onClick={() => onEnter(username)}
        >
          {t("Enter")}
        </LoadingButton>
      </Box>
    </Paper>
  );
}

export default Welcome;
