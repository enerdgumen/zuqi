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
import clsx from "clsx";

const useStyles = makeStyles(theme => ({
  root: {
    padding: theme.spacing(3),
    maxWidth: "50vw",
    zIndex: 1
  },
  question: {
    marginBottom: theme.spacing(2)
  },
  answer: {
    height: theme.spacing(5),
    alignItems: "center"
  },
  answerSuccess: {
    backgroundColor: green[50],
    "&:hover": {
      backgroundColor: green[100]
    }
  },
  answerFailure: {
    backgroundColor: red[50],
    "&:hover": {
      backgroundColor: red[100]
    }
  },
  greenCheckbox: {
    color: green[600]
  },
  redCheckbox: {
    color: red[700]
  },
  answerProgress: {
    color: grey[700]
  }
}));

const successStatus = "success";
const failureStatus = "failure";
const loadingStatus = "loading";

export function ChallengeButton({ onChallenge, challenging }) {
  const { t } = useTranslation();
  return (
    <LoadingButton
      variant="contained"
      color="primary"
      disabled={challenging}
      loading={challenging}
      onClick={onChallenge}
    >
      {t("Challenge")}
    </LoadingButton>
  );
}

export function QuestionPanel({ question, children }) {
  const classes = useStyles();
  return (
    <Paper className={classes.root}>
      <Typography className={classes.question} variant="h5">
        {question}
      </Typography>
      {children}
    </Paper>
  );
}

export function QuestionAnswers({ children }) {
  return <List>{children}</List>;
}

export function QuestionAnswer({ index, text, status, onSelect }) {
  const classes = useStyles();
  const id = `answer-${index}`;
  return (
    <ListItem
      key={id}
      className={clsx({
        [classes.answer]: true,
        [classes.answerSuccess]: status === successStatus,
        [classes.answerFailure]: status === failureStatus
      })}
      button
      onClick={onSelect && (() => onSelect(index))}
    >
      <ListItemIcon>
        <QuestionIcon status={status} />
      </ListItemIcon>
      <ListItemText id={id} primary={text} />
    </ListItem>
  );
}

function QuestionIcon({ status }) {
  const { greenCheckbox, redCheckbox, answerProgress } = useStyles();
  if (status === loadingStatus) {
    return <CircularProgress size={18} className={answerProgress} />;
  }
  if (status === successStatus || status === failureStatus) {
    return (
      <Checkbox
        className={status === successStatus ? greenCheckbox : redCheckbox}
        color="default"
        edge="start"
        checked={true}
        disableRipple
      />
    );
  }
  return <Checkbox edge="start" checked={false} disableRipple />;
}
