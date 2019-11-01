import React from "react";
import { useTranslation } from "react-i18next";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import { makeStyles } from "@material-ui/core/styles";
import { LoadingButton } from "./LoadingButton";

const useStyles = makeStyles(theme => ({
  root: {
    padding: theme.spacing(3)
  },
  challangeButton: {
    marginTop: theme.spacing(2)
  }
}));

export function QuestionPanel({ question, onChallenge, disabled, challenging }) {
  const { t } = useTranslation();
  const classes = useStyles();
  return (
    <Paper className={classes.root}>
      <Typography variant="h5">{t(question)}</Typography>
      <LoadingButton
        className={classes.challangeButton}
        variant="contained"
        color="primary"
        disabled={disabled || challenging}
        loading={!disabled && challenging}
        onClick={onChallenge}
      >
        {t("Challenge")}
      </LoadingButton>
    </Paper>
  );
}
