import React from "react";
import { useTranslation } from "react-i18next";
import Paper from "@material-ui/core/Paper";
import Typography from "@material-ui/core/Typography";
import CircularProgress from "@material-ui/core/CircularProgress";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import ListItemText from "@material-ui/core/ListItemText";
import Checkbox from "@material-ui/core/Checkbox";
import { makeStyles } from "@material-ui/core/styles";
import { green, grey, red } from "@material-ui/core/colors";
import { LoadingButton } from "./LoadingButton";

const useStyles = makeStyles(theme => ({
  root: {
    padding: theme.spacing(3)
  },
  challangeButton: {
    marginTop: theme.spacing(2)
  },
  greenCheckbox: {
    color: green[600]
  },
  redCheckbox: {
    color: red[700]
  }
}));

export function QuestionPanel({
  question,
  onChallenge,
  disabled,
  challenging
}) {
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

export function QuestionAnswers({ answers, onSelect, selection, status }) {
  return (
    <List component="nav">
      {answers.map((answer, index) => {
        const id = `answer-${index}`;
        const isSelected = index === selection;
        return (
          <ListItem key={id} button onClick={() => onSelect(index)}>
            <ListItemIcon>
              <QuestionIcon status={isSelected && status} />
            </ListItemIcon>
            <ListItemText id={id} primary={answer} />
          </ListItem>
        );
      })}
    </List>
  );
}

function QuestionIcon({ status }) {
  const { greenCheckbox, redCheckbox } = useStyles();
  if (status === "loading") {
    return <CircularProgress size={20} color={grey[900]} />;
  }
  if (status === "success" || status === "failure") {
    return (
      <Checkbox
        className={status === "success" ? greenCheckbox : redCheckbox}
        color="default"
        edge="start"
        checked={true}
      />
    );
  }
  return <Checkbox edge="start" checked={false} />;
}
