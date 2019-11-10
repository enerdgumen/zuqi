import React from "react";
import { useTranslation } from "react-i18next";
import CircularProgress from "@material-ui/core/CircularProgress";
import Avatar from "@material-ui/core/Avatar";
import Paper from "@material-ui/core/Paper";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import ListItemAvatar from "@material-ui/core/ListItemAvatar";
import ListItemSecondaryAction from "@material-ui/core/ListItemSecondaryAction";
import { makeStyles } from "@material-ui/core/styles";
import { green, red, orange } from "@material-ui/core/colors";
import CheckIcon from "@material-ui/icons/Check";
import CloseIcon from "@material-ui/icons/Close";
import { Typography } from "@material-ui/core";
import PeopleIcon from '@material-ui/icons/People';

const statusChallenging = "challenging";
const statusLoser = "loser";
const statusWinner = "winner";

const statusProps = {
  [statusChallenging]: { color: orange },
  [statusWinner]: { color: green },
  [statusLoser]: { color: red }
};

const useStyles = makeStyles(theme => ({
  root: {
    minWidth: '12em',
    maxWidth: '20em',
    position: "fixed",
    top: "50%",
    left: '1em',
    transform: "translate(0, -50%)"
  },
  title: {
    marginTop: theme.spacing(1),
    marginBottom: 0,
    marginLeft: theme.spacing(3),
    marginRight: theme.spacing(1),
    '& svg': {
      verticalAlign: 'middle',
      position: 'relative',
      top: -2
    }
  },
  item: ({ color }) => ({
    backgroundColor: color && color[50]
  }),
  avatar: ({ color }) => ({
    color: "#fff",
    backgroundColor: color && color[500]
  }),
  username: ({ color }) => ({
    color: color && color[900],
    "& span": { fontWeight: 700 }
  }),
  icon: ({ color }) => ({
    color: color && color[700]
  })
}));

export function Players({ children }) {
  const { t } = useTranslation();
  const classes = useStyles();
  return (
    <Paper square={true} elevation={1} className={classes.root}>
      <Typography className={classes.title} variant="h6"><PeopleIcon /> {t('Players')}</Typography>
      <List dense>{children}</List>
    </Paper>
  );
}

export function Player({ username, status }) {
  const classes = useStyles(statusProps[status]);
  return (
    <ListItem className={classes.item}>
      <ListItemAvatar>
        <Avatar className={classes.avatar}>{username[0].toUpperCase()}</Avatar>
      </ListItemAvatar>
      <ListItemText className={classes.username} primary={username} />
      <ListItemSecondaryAction>
        {status === statusChallenging && (
          <CircularProgress className={classes.icon} size={18} />
        )}
        {status === statusWinner && <CheckIcon className={classes.icon} />}
        {status === statusLoser && <CloseIcon className={classes.icon} />}
      </ListItemSecondaryAction>
    </ListItem>
  );
}
