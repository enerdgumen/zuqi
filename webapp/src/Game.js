import _ from "lodash";
import React, { useEffect, useState, Fragment } from "react";
import { useImmer } from "use-immer";
import { useTranslation } from "react-i18next";
import { useSnackbar } from "notistack";
import CircularProgress from "@material-ui/core/CircularProgress";
import { Welcome } from "./Welcome";
import {
  QuestionPanel,
  ChallengeButton,
  QuestionAnswers,
  QuestionAnswer
} from "./Question";
import { Players, Player } from "./Players";
import { Center } from "./Layout";
import { openSocket } from "./Socket";
import { createBrowserHistory } from "history";

const history = createBrowserHistory();

function Game() {
  const { t } = useTranslation();
  const { enqueueSnackbar } = useSnackbar();
  const [connection, setConnection] = useState();
  const handleLogin = connection => {
    setConnection(connection);
    saveUsername(connection.username);
  };
  const handleError = err => {
    enqueueSnackbar(t(err.message), {
      variant: "warning"
    });
  };
  const saveUsername = username => {
    history.push(`?uid=${username}`);
  };
  const getUsername = () => {
    return new URLSearchParams(history.location.search).get("uid");
  }
  if (!connection) {
    return (
      <Login
        initialUsername={getUsername()}
        onLogin={handleLogin}
        onError={handleError}
      />
    );
  }
  return <Session {...connection} />;
}

function Login({ initialUsername, onLogin, onError }) {
  const [autoLogin, setAutoLogin] = useState(Boolean(initialUsername));
  const [entering, setEntering] = useState(false);
  const handleEnter = async username => {
    try {
      setEntering(true);
      const socket = await openSocket(username);
      onLogin({ socket, username });
    } catch (err) {
      setEntering(false);
      setAutoLogin(false);
      onError(err);
    }
  };
  useEffect(() => {
    if (autoLogin) handleEnter(initialUsername);
  }, []);
  return (
    <Center>
      {autoLogin && <CircularProgress />}
      {!autoLogin && <Welcome onEnter={handleEnter} entering={entering} />}
    </Center>
  );
}

function Session({ socket, username }) {
  const { t } = useTranslation();
  const { enqueueSnackbar } = useSnackbar();
  const [session, updateSession] = useImmer({
    question: null,
    answers: [],
    answersStatus: [],
    answer: null,
    players: [],
    playersStatus: {},
    challenging: false
  });
  const handleChallenge = () => {
    updateSession(it => {
      it.challenging = true;
    });
    socket.sendJson({ action: "challenge" });
  };
  const handleAnswer = index => {
    updateSession(it => {
      it.answer = index;
      it.answers[index].status = "loading";
    });
    socket.sendJson({ answer: index });
  };
  socket.onmessage = message => {
    const data = JSON.parse(message.data);
    console.log("message:", data);
    switch (data.event) {
      case "question":
        return updateSession(it => {
          it.question = data.question;
          it.answers = [];
          it.answer = null;
          it.playersStatus = {};
          it.challenging = false;
        });
      case "joined":
        return updateSession(it => {
          it.players.push({ username: data.user });
        });
      case "left":
        enqueueSnackbar(t("{{user}} has left the game", data));
        return updateSession(it => {
          const index = _.findIndex(
            it.players,
            it => it.username === data.user
          );
          delete it.players[index];
        });
      case "challenged":
        // TODO: if I'm challenged start countdown
        return updateSession(it => {
          it.playersStatus[data.user] = "challenging";
          it.challenging = true;
        });
      case "reply":
        return updateSession(it => {
          it.answers = data.answers.map(text => ({ text }));
        });
      case "lost":
        return updateSession(it => {
          it.challenging = false;
          it.playersStatus[data.user] = "loser";
          if (data.user === username) {
            it.answers[it.answer].status = "failure";
          }
        });
      case "end":
        return updateSession(it => {
          it.playersStatus[data.winner] = "winner";
          if (data.winner === username) {
            it.answers[it.answer].status = "success";
          }
        });
      default:
        console.log("unexpected message", data);
    }
  };
  const {
    question,
    answers,
    answer,
    players,
    playersStatus,
    challenging
  } = session;
  return (
    <Fragment>
      <SessionPlayers players={players} status={playersStatus} />
      <Center>
        {question && (
          <SessionQuestion
            question={question}
            answers={answers}
            answer={answer}
            challenging={challenging}
            onChallenge={handleChallenge}
            onAnswer={handleAnswer}
          />
        )}
        {!question && <CircularProgress />}
      </Center>
    </Fragment>
  );
}

function SessionPlayers({ players, status }) {
  return (
    <Players>
      {players.map(player => (
        <Player
          key={player.username}
          username={player.username}
          status={status[player.username]}
        />
      ))}
    </Players>
  );
}

function SessionQuestion({
  question,
  answers,
  answer,
  challenging,
  onChallenge,
  onAnswer
}) {
  return (
    <QuestionPanel question={question}>
      {answers.length === 0 && (
        <ChallengeButton onChallenge={onChallenge} challenging={challenging} />
      )}
      {answers.length > 0 && (
        <QuestionAnswers>
          {answers.map(({ text, status }, index) => (
            <QuestionAnswer
              key={index}
              index={index}
              text={text}
              status={status}
              onSelect={answer !== null ? undefined : onAnswer}
            />
          ))}
        </QuestionAnswers>
      )}
    </QuestionPanel>
  );
}

export default Game;
