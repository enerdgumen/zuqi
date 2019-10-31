import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import Box from "@material-ui/core/Box";
import Button from "@material-ui/core/Button";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import TextField from "@material-ui/core/TextField";
import CircularProgress from "@material-ui/core/CircularProgress";
import { makeStyles } from "@material-ui/core/styles";
import { useSnackbar } from "notistack";
import { EnterExitAnimation } from "./Animations";
import * as api from "./Api";

const useStyles = makeStyles(theme => ({
  root: {
    padding: theme.spacing(3)
  },
  row: {
    marginTop: theme.spacing(2),
    display: "flex",
    alignItems: "flex-end"
  },
  enterContainer: {
    position: "relative",
    marginLeft: theme.spacing(2)
  },
  enterProgress: {
    position: "absolute",
    top: "50%",
    left: "50%",
    marginTop: -12,
    marginLeft: -12
  }
}));

export function WelcomePanel({ onEnter, entering }) {
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
        <Box className={classes.enterContainer}>
          <Button
            variant="contained"
            color="primary"
            disabled={!username || entering}
            onClick={onEnter}
          >
            {t("Enter")}
          </Button>
          {entering && (
            <CircularProgress size={24} className={classes.enterProgress} />
          )}
        </Box>
      </Box>
    </Paper>
  );
}

export function Welcome() {
  const { t } = useTranslation();
  const { enqueueSnackbar, closeSnackbar } = useSnackbar();
  const [entering, setEntering] = useState(false);
  const handleEnter = async username => {
    setEntering(true);
    closeSnackbar();
    try {
      await api.enter(username);
    } catch (err) {
      enqueueSnackbar(t(err.message), {
        variant: "info"
      });
    } finally {
      setEntering(false);
    }
  };
  return <WelcomePanel onEnter={handleEnter} entering={entering} />;
}

export const WelcomeAnimated = () => (
  <EnterExitAnimation>
    <Welcome />
  </EnterExitAnimation>
);

export default WelcomeAnimated;
