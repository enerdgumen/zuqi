import React from "react";
import CircularProgress from "@material-ui/core/CircularProgress";
import Avatar from "@material-ui/core/Avatar";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import ListItemAvatar from "@material-ui/core/ListItemAvatar";
import ListItemSecondaryAction from "@material-ui/core/ListItemSecondaryAction";
import { makeStyles } from "@material-ui/core/styles";
import { green, red, orange } from "@material-ui/core/colors";
import CheckIcon from "@material-ui/icons/Check";
import CloseIcon from "@material-ui/icons/Close";

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
    maxWidth: 240,
    backgroundColor: theme.palette.background.paper
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
  const classes = useStyles();
  return (
    <List className={classes.root} dense>
      {children}
    </List>
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
